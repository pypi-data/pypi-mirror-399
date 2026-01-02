"""
PrimeLLM Python SDK v1.0.0

Production-grade SDK with streaming, retries, tool calling, and full API parity.

Example:
    from primellm import PrimeLLM
    
    client = PrimeLLM(api_key="primellm_XXX")
    response = client.chat.create(
        model="gpt-5.1",
        messages=[{"role": "user", "content": "Hello!"}],
    )
    print(response["choices"][0]["message"]["content"])
"""

from __future__ import annotations

import os
import time
import random
from typing import Any, Dict, List, Optional, Iterator, Union, Callable

import httpx

from .errors import (
    PrimeLLMError,
    AuthenticationError,
    InsufficientCreditsError,
    RateLimitError,
    create_error_from_status,
)
from .tokenizer import count_tokens, set_tokenizer_adapter
from .streaming import stream_reader
from .tools import execute_tools, has_tool_calls, create_tool, parse_tool_arguments


# Retryable status codes
RETRYABLE_STATUSES = [429, 502, 503, 504]

# Default retry config
DEFAULT_MAX_RETRIES = 3
DEFAULT_BASE_DELAY = 0.3  # 300ms
DEFAULT_MAX_DELAY = 10.0  # 10s


class PrimeLLM:
    """
    PrimeLLM API Client
    
    Production-grade client with streaming, retries, tool calling, and full API access.
    
    Args:
        api_key: Your PrimeLLM API key. If not provided, reads from
                 PRIMELLM_API_KEY environment variable.
        base_url: API base URL. Default: https://api.primellm.in
        timeout: Request timeout in seconds. Default: 60
        max_retries: Max retry attempts for failed requests. Default: 3
        openai_compatible: Use OpenAI-compatible endpoint (/v1/chat/completions). Default: False
        app_name: App name for attribution headers (X-PrimeLLM-App-Name).
        app_url: App URL for attribution headers (X-PrimeLLM-App-Url).
    
    Example:
        client = PrimeLLM(api_key="primellm_XXX")
        response = client.chat.create(model="gpt-5.1", messages=[...])
        
        # With OpenAI-compatible mode
        client = PrimeLLM(api_key="primellm_XXX", openai_compatible=True)
    """
    
    def __init__(
        self,
        api_key: Optional[str] = None,
        base_url: str = "https://api.primellm.in",
        timeout: float = 60.0,
        max_retries: int = DEFAULT_MAX_RETRIES,
        openai_compatible: bool = False,
        app_name: Optional[str] = None,
        app_url: Optional[str] = None,
    ) -> None:
        self.api_key = api_key or os.getenv("PRIMELLM_API_KEY")
        if not self.api_key:
            raise PrimeLLMError(
                "PrimeLLM API key is required. "
                "Pass api_key=... or set PRIMELLM_API_KEY env var."
            )
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
        self.max_retries = max_retries
        self.openai_compatible = openai_compatible
        self.app_name = app_name
        self.app_url = app_url
        
        # Initialize sub-clients
        self.chat = ChatClient(self)
        self.embeddings = EmbeddingsClient(self)
        self.models = ModelsClient(self)
        self.keys = KeysClient(self)
        self.credits = CreditsClient(self)
        self.tokens = TokensClient()
        self.tools = ToolsClient()
        self.batch = BatchClient(self)
    
    def _headers(self) -> Dict[str, str]:
        """Build request headers with authentication and attribution."""
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }
        if self.app_name:
            headers["X-PrimeLLM-App-Name"] = self.app_name
        if self.app_url:
            headers["X-PrimeLLM-App-Url"] = self.app_url
        return headers
    
    def _get_chat_path(self) -> str:
        """Get the chat endpoint path based on compatibility mode."""
        return "/v1/chat/completions" if self.openai_compatible else "/v1/chat"
    
    def _sleep_with_backoff(self, attempt: int) -> None:
        """Sleep with exponential backoff and jitter."""
        delay = min(
            DEFAULT_MAX_DELAY,
            DEFAULT_BASE_DELAY * (2 ** attempt) + random.uniform(0.1, 0.3)
        )
        time.sleep(delay)
    
    def request(
        self,
        path: str,
        body: Optional[Dict[str, Any]] = None,
        method: str = "POST",
    ) -> Dict[str, Any]:
        """
        Make HTTP request with retries and error handling.
        
        Args:
            path: API endpoint path
            body: Request body (for POST)
            method: HTTP method (GET, POST)
            
        Returns:
            Parsed JSON response
            
        Raises:
            PrimeLLMError: On request failure
        """
        url = f"{self.base_url}{path}"
        last_error = None
        
        for attempt in range(self.max_retries):
            try:
                with httpx.Client(timeout=self.timeout) as client:
                    if method == "GET":
                        res = client.get(url, headers=self._headers())
                    else:
                        res = client.post(url, json=body or {}, headers=self._headers())
                
                if res.status_code // 100 == 2:
                    return res.json()
                
                # Parse error
                detail = res.text
                try:
                    err_json = res.json()
                    detail = err_json.get("detail", detail)
                except:
                    pass
                
                # Check if retryable
                if res.status_code in RETRYABLE_STATUSES and attempt < self.max_retries - 1:
                    last_error = create_error_from_status(res.status_code, f"Request failed: {res.status_code}", detail)
                    self._sleep_with_backoff(attempt)
                    continue
                
                raise create_error_from_status(res.status_code, f"PrimeLLM API error: {res.status_code}", detail)
                
            except httpx.RequestError as exc:
                if attempt < self.max_retries - 1:
                    last_error = PrimeLLMError(f"Request failed: {exc}")
                    self._sleep_with_backoff(attempt)
                    continue
                raise PrimeLLMError(f"Request failed after {self.max_retries} attempts: {exc}") from exc
        
        raise last_error or PrimeLLMError("Request failed after retries")
    
    def stream_request(
        self,
        path: str,
        body: Dict[str, Any],
    ) -> Iterator[Dict[str, Any]]:
        """
        Make streaming HTTP request.
        
        Args:
            path: API endpoint path
            body: Request body with stream=true
            
        Yields:
            Chunk dictionaries from SSE events
        """
        url = f"{self.base_url}{path}"
        body = {**body, "stream": True}
        
        with httpx.Client(timeout=self.timeout) as client:
            with client.stream("POST", url, json=body, headers=self._headers()) as res:
                if res.status_code // 100 != 2:
                    res.read()
                    detail = res.text
                    try:
                        err_json = res.json()
                        detail = err_json.get("detail", detail)
                    except:
                        pass
                    raise create_error_from_status(res.status_code, f"Streaming failed: {res.status_code}", detail)
                
                yield from stream_reader(res)
    
    def run(
        self,
        model: Union[str, Callable],
        input: Union[str, List[Dict[str, str]]],
        tools: Optional[Dict[str, Callable]] = None,
        max_turns: int = 10,
        stop_when: Optional[Callable] = None,
        context_strategy: Optional[str] = None,
        context_limit: Optional[int] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """
        High-level run() API for multi-turn conversations with tool execution.
        
        Args:
            model: Model name or function returning model name
            input: Initial user message or list of messages
            tools: Registry mapping tool names to executor functions
            max_turns: Maximum conversation turns (default: 10)
            stop_when: Callback to check if should stop (receives context dict)
            context_strategy: Strategy for managing context ("truncate", "middle-out", "summarize")
            context_limit: Maximum tokens for context
            **kwargs: Additional parameters (temperature, max_tokens, response_format, etc.)
            
        Returns:
            Dict with text, messages, usage, turns, finish_reason
            
        Example:
            # Simple chat
            result = client.run(
                model="gpt-5.1",
                input="What's 2+2?"
            )
            print(result["text"])
            
            # With tools
            result = client.run(
                model="gpt-5.1",
                input="What's the weather in Paris?",
                tools={
                    "get_weather": lambda args: {"temp": 22, "condition": "sunny"}
                },
                max_turns=5
            )
            
            # With dynamic model selection
            result = client.run(
                model=lambda ctx: "gpt-4" if ctx["turn"] > 2 else "gpt-5.1",
                input="Complex task here..."
            )
        """
        tools = tools or {}
        
        # Initialize messages
        if isinstance(input, str):
            messages = [{"role": "user", "content": input}]
        else:
            messages = list(input)
        
        total_usage = {"prompt_tokens": 0, "completion_tokens": 0, "total_tokens": 0}
        turn = 0
        last_timings = None
        
        # Build tool definitions from registry
        tool_defs = None
        if tools:
            tool_defs = [
                {"type": "function", "function": {"name": name, "description": f"Function: {name}", "parameters": {}}}
                for name in tools.keys()
            ]
        
        while turn < max_turns:
            turn += 1
            
            context = {
                "turn": turn,
                "messages": messages,
                "last_message": messages[-1] if messages else None,
                "usage": total_usage
            }
            
            # Apply context management if needed
            context_messages = messages
            if context_strategy and context_limit:
                context_messages = self._manage_context(messages, context_limit, context_strategy)
            
            # Resolve dynamic model
            resolved_model = model(context) if callable(model) else model
            
            # Resolve dynamic parameters
            request_kwargs = {}
            for key, value in kwargs.items():
                request_kwargs[key] = value(context) if callable(value) else value
            
            # Make the request
            response = self.chat.create(
                model=resolved_model,
                messages=context_messages,
                tools=tool_defs,
                **request_kwargs
            )
            
            choice = response["choices"][0]
            assistant_message = choice["message"]
            messages.append(assistant_message)
            
            # Accumulate usage
            if "usage" in response:
                total_usage["prompt_tokens"] += response["usage"].get("prompt_tokens", 0)
                total_usage["completion_tokens"] += response["usage"].get("completion_tokens", 0)
                total_usage["total_tokens"] += response["usage"].get("total_tokens", 0)
            
            last_timings = response.get("timings")
            
            # Check stop conditions
            if stop_when and stop_when(context):
                break
            
            finish_reason = choice.get("finish_reason")
            
            if finish_reason in ("stop", "length"):
                break
            
            # Handle tool calls
            if finish_reason == "tool_calls" and has_tool_calls(assistant_message):
                tool_messages = execute_tools(assistant_message, tools)
                messages.extend(tool_messages)
                continue
            
            break
        
        last_assistant = [m for m in messages if m.get("role") == "assistant"]
        text = last_assistant[-1].get("content", "") if last_assistant else ""
        
        return {
            "text": text,
            "messages": messages,
            "usage": total_usage,
            "turns": turn,
            "finish_reason": "stop",
            "timings": last_timings
        }
    
    def _manage_context(
        self,
        messages: List[Dict[str, Any]],
        limit: int,
        strategy: str
    ) -> List[Dict[str, Any]]:
        """Apply context management strategy."""
        token_count = count_tokens(messages)
        
        if token_count <= limit:
            return messages
        
        if strategy == "truncate":
            # Remove oldest non-system messages
            system_msgs = [m for m in messages if m.get("role") == "system"]
            other_msgs = [m for m in messages if m.get("role") != "system"]
            
            while count_tokens(system_msgs + other_msgs) > limit and len(other_msgs) > 1:
                other_msgs.pop(0)
            
            return system_msgs + other_msgs
        
        elif strategy == "middle-out":
            # Keep system prompt and recent messages, remove from middle
            system_msgs = [m for m in messages if m.get("role") == "system"]
            other_msgs = [m for m in messages if m.get("role") != "system"]
            keep_recent = min(4, len(other_msgs))
            recent = other_msgs[-keep_recent:]
            
            if count_tokens(system_msgs + recent) <= limit:
                return system_msgs + recent
            return system_msgs + [recent[-1]] if recent else system_msgs
        
        elif strategy == "summarize":
            # For now, fall back to truncate (summarize requires additional API call)
            return self._manage_context(messages, limit, "truncate")
        
        return messages


class ChatClient:
    """Chat sub-client"""
    
    def __init__(self, client: PrimeLLM):
        self._client = client
    
    def create(
        self,
        model: str,
        messages: List[Dict[str, str]],
        **kwargs: Any,
    ) -> Dict[str, Any]:
        """
        Create a chat completion.
        
        Args:
            model: Model name (e.g., "gpt-5.1")
            messages: List of message dicts with "role" and "content"
            **kwargs: Extra parameters (temperature, max_tokens, tools, response_format, etc.)
            
        Returns:
            Chat completion response dict
        """
        payload = {"model": model, "messages": messages, **kwargs}
        return self._client.request(self._client._get_chat_path(), payload)
    
    def stream(
        self,
        model: str,
        messages: List[Dict[str, str]],
        **kwargs: Any,
    ) -> Iterator[Dict[str, Any]]:
        """
        Stream chat completion.
        
        Args:
            model: Model name
            messages: List of message dicts
            **kwargs: Extra parameters
            
        Yields:
            Chunk dicts with delta content
        """
        payload = {"model": model, "messages": messages, **kwargs}
        yield from self._client.stream_request(self._client._get_chat_path(), payload)


class EmbeddingsClient:
    """Embeddings sub-client"""
    
    def __init__(self, client: PrimeLLM):
        self._client = client
    
    def create(
        self,
        input: Union[str, List[str]],
        model: str = "embed-1",
    ) -> Dict[str, Any]:
        """
        Create embeddings for input text.
        
        Args:
            input: Text or list of texts to embed
            model: Embedding model name
            
        Returns:
            Embeddings response with data array
        """
        payload = {"model": model, "input": input}
        return self._client.request("/v1/embeddings", payload)


class ModelsClient:
    """Models sub-client"""
    
    def __init__(self, client: PrimeLLM):
        self._client = client
    
    def list(self) -> Dict[str, Any]:
        """List available models."""
        return self._client.request("/v1/models", method="GET")


class KeysClient:
    """API Keys sub-client"""
    
    def __init__(self, client: PrimeLLM):
        self._client = client
    
    def list(self) -> Dict[str, Any]:
        """List API keys."""
        return self._client.request("/v1/keys", method="GET")
    
    def create(self, label: Optional[str] = None) -> Dict[str, Any]:
        """Create a new API key."""
        return self._client.request("/v1/keys", {"label": label})
    
    def revoke(self, key_id: int) -> Dict[str, Any]:
        """Revoke an API key."""
        return self._client.request("/v1/keys/revoke", {"key_id": key_id})


class CreditsClient:
    """Credits sub-client"""
    
    def __init__(self, client: PrimeLLM):
        self._client = client
    
    def get(self) -> Dict[str, Any]:
        """Get current credit balance."""
        return self._client.request("/v1/credits", method="GET")


class TokensClient:
    """Token counting utility"""
    
    def count(self, input: Union[str, List[Dict[str, str]]]) -> int:
        """
        Count tokens in text or messages.
        
        Args:
            input: Text string or list of message dicts
            
        Returns:
            Estimated token count
        """
        return count_tokens(input)
    
    def set_adapter(self, adapter) -> None:
        """Set custom tokenizer adapter."""
        set_tokenizer_adapter(adapter)


class ToolsClient:
    """Tool calling utilities"""
    
    execute = staticmethod(execute_tools)
    has_tool_calls = staticmethod(has_tool_calls)
    create = staticmethod(create_tool)
    parse_arguments = staticmethod(parse_tool_arguments)


class BatchClient:
    """Batch jobs sub-client (Phase 3)"""
    
    def __init__(self, client: PrimeLLM):
        self._client = client
    
    def create(self, inputs: List[Dict[str, Any]], model: str) -> Dict[str, Any]:
        """
        Create a new batch job.
        
        Args:
            inputs: Array of batch input items
            model: Model to use for all requests
            
        Returns:
            Batch creation response
        """
        return self._client.request("/v1/batch", {"inputs": inputs, "model": model})
    
    def get(self, id: str) -> Dict[str, Any]:
        """
        Get batch job status.
        
        Args:
            id: Batch job ID
            
        Returns:
            Batch job info
        """
        return self._client.request(f"/v1/batch/{id}", method="GET")
    
    def cancel(self, id: str) -> Dict[str, Any]:
        """
        Cancel a batch job.
        
        Args:
            id: Batch job ID
            
        Returns:
            Updated batch job info
        """
        return self._client.request(f"/v1/batch/{id}/cancel", {})
