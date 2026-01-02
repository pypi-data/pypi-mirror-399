"""
PrimeLLM Async Python SDK

Async client using httpx.AsyncClient for non-blocking operations.
"""

from __future__ import annotations

import os
import random
from typing import Any, Dict, List, Optional, AsyncIterator, Union

import httpx

from .errors import (
    PrimeLLMError,
    create_error_from_status,
)
from .tools import execute_tools, has_tool_calls
from .tokenizer import count_tokens


# Retryable status codes
RETRYABLE_STATUSES = [429, 502, 503, 504]

# Default retry config
DEFAULT_MAX_RETRIES = 3
DEFAULT_BASE_DELAY = 0.3
DEFAULT_MAX_DELAY = 10.0


class AsyncPrimeLLM:
    """
    Async PrimeLLM API Client
    
    Production-grade async client with streaming, retries, and full API access.
    
    Args:
        api_key: Your PrimeLLM API key. If not provided, reads from
                 PRIMELLM_API_KEY environment variable.
        base_url: API base URL. Default: https://api.primellm.in
        timeout: Request timeout in seconds. Default: 60
        max_retries: Max retry attempts for failed requests. Default: 3
        openai_compatible: Use OpenAI-compatible endpoint. Default: False
        app_name: App name for attribution headers.
        app_url: App URL for attribution headers.
    
    Example:
        async with AsyncPrimeLLM(api_key="primellm_XXX") as client:
            response = await client.chat.create(
                model="gpt-5.1",
                messages=[{"role": "user", "content": "Hello!"}]
            )
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
        
        self._client: Optional[httpx.AsyncClient] = None
        
        # Initialize sub-clients
        self.chat = AsyncChatClient(self)
        self.embeddings = AsyncEmbeddingsClient(self)
        self.models = AsyncModelsClient(self)
        self.keys = AsyncKeysClient(self)
        self.credits = AsyncCreditsClient(self)
        self.batch = AsyncBatchClient(self)
    
    async def __aenter__(self) -> "AsyncPrimeLLM":
        self._client = httpx.AsyncClient(timeout=self.timeout)
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb) -> None:
        if self._client:
            await self._client.aclose()
            self._client = None
    
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
    
    async def _sleep_with_backoff(self, attempt: int) -> None:
        """Sleep with exponential backoff and jitter."""
        import asyncio
        delay = min(
            DEFAULT_MAX_DELAY,
            DEFAULT_BASE_DELAY * (2 ** attempt) + random.uniform(0.1, 0.3)
        )
        await asyncio.sleep(delay)
    
    async def request(
        self,
        path: str,
        body: Optional[Dict[str, Any]] = None,
        method: str = "POST",
    ) -> Dict[str, Any]:
        """
        Make async HTTP request with retries and error handling.
        """
        if not self._client:
            self._client = httpx.AsyncClient(timeout=self.timeout)
        
        url = f"{self.base_url}{path}"
        last_error = None
        
        for attempt in range(self.max_retries):
            try:
                if method == "GET":
                    res = await self._client.get(url, headers=self._headers())
                else:
                    res = await self._client.post(url, json=body or {}, headers=self._headers())
                
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
                    await self._sleep_with_backoff(attempt)
                    continue
                
                raise create_error_from_status(res.status_code, f"PrimeLLM API error: {res.status_code}", detail)
                
            except httpx.RequestError as exc:
                if attempt < self.max_retries - 1:
                    last_error = PrimeLLMError(f"Request failed: {exc}")
                    await self._sleep_with_backoff(attempt)
                    continue
                raise PrimeLLMError(f"Request failed after {self.max_retries} attempts: {exc}") from exc
        
        raise last_error or PrimeLLMError("Request failed after retries")
    
    async def stream_request(
        self,
        path: str,
        body: Dict[str, Any],
    ) -> AsyncIterator[Dict[str, Any]]:
        """
        Make async streaming HTTP request.
        """
        if not self._client:
            self._client = httpx.AsyncClient(timeout=self.timeout)
        
        url = f"{self.base_url}{path}"
        body = {**body, "stream": True}
        
        async with self._client.stream("POST", url, json=body, headers=self._headers()) as res:
            if res.status_code // 100 != 2:
                await res.aread()
                detail = res.text
                try:
                    err_json = res.json()
                    detail = err_json.get("detail", detail)
                except:
                    pass
                raise create_error_from_status(res.status_code, f"Streaming failed: {res.status_code}", detail)
            
            async for line in res.aiter_lines():
                if not line.startswith("data:"):
                    continue
                data = line[5:].strip()
                if not data or data == "[DONE]":
                    continue
                try:
                    import json
                    yield json.loads(data)
                except:
                    continue
    
    async def run(
        self,
        model: str,
        input: Union[str, List[Dict[str, str]]],
        tools: Optional[Dict[str, Any]] = None,
        max_turns: int = 10,
        stop_when: Optional[Any] = None,
        context_strategy: Optional[str] = None,
        context_limit: Optional[int] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """
        High-level run() API for multi-turn conversations with tool execution.
        
        Args:
            model: Model name
            input: Initial user message or list of messages
            tools: Registry mapping tool names to executor functions
            max_turns: Maximum conversation turns
            stop_when: Callback to check if should stop
            context_strategy: Strategy for managing context ("truncate", "middle-out")
            context_limit: Maximum tokens for context
            **kwargs: Additional parameters (temperature, max_tokens, etc.)
            
        Returns:
            RunResult dict with text, messages, usage, turns
        """
        tools = tools or {}
        
        # Initialize messages
        if isinstance(input, str):
            messages = [{"role": "user", "content": input}]
        else:
            messages = list(input)
        
        total_usage = {"prompt_tokens": 0, "completion_tokens": 0, "total_tokens": 0}
        turn = 0
        
        # Build tool definitions
        tool_defs = None
        if tools:
            tool_defs = [
                {"type": "function", "function": {"name": name, "description": f"Function: {name}", "parameters": {}}}
                for name in tools.keys()
            ]
        
        while turn < max_turns:
            turn += 1
            
            # Apply context management
            context_messages = messages
            if context_strategy and context_limit:
                context_messages = self._manage_context(messages, context_limit, context_strategy)
            
            # Make request
            request_body = {"model": model, "messages": context_messages, **kwargs}
            if tool_defs:
                request_body["tools"] = tool_defs
            
            response = await self.chat.create(**request_body)
            
            choice = response["choices"][0]
            assistant_msg = choice["message"]
            messages.append(assistant_msg)
            
            # Accumulate usage
            if "usage" in response:
                total_usage["prompt_tokens"] += response["usage"].get("prompt_tokens", 0)
                total_usage["completion_tokens"] += response["usage"].get("completion_tokens", 0)
                total_usage["total_tokens"] += response["usage"].get("total_tokens", 0)
            
            finish_reason = choice.get("finish_reason")
            
            if finish_reason in ("stop", "length"):
                break
            
            # Handle tool calls
            if finish_reason == "tool_calls" and has_tool_calls(assistant_msg):
                tool_messages = execute_tools(assistant_msg, tools)
                messages.extend(tool_messages)
                continue
            
            break
        
        last_assistant = [m for m in messages if m.get("role") == "assistant"][-1] if messages else {}
        text = last_assistant.get("content", "") or ""
        
        return {
            "text": text,
            "messages": messages,
            "usage": total_usage,
            "turns": turn,
            "finish_reason": "stop"
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
            system_msgs = [m for m in messages if m.get("role") == "system"]
            other_msgs = [m for m in messages if m.get("role") != "system"]
            
            while count_tokens(system_msgs + other_msgs) > limit and len(other_msgs) > 1:
                other_msgs.pop(0)
            
            return system_msgs + other_msgs
        
        elif strategy == "middle-out":
            system_msgs = [m for m in messages if m.get("role") == "system"]
            other_msgs = [m for m in messages if m.get("role") != "system"]
            keep_recent = min(4, len(other_msgs))
            recent = other_msgs[-keep_recent:]
            
            if count_tokens(system_msgs + recent) <= limit:
                return system_msgs + recent
            return system_msgs + [recent[-1]] if recent else system_msgs
        
        return messages


class AsyncChatClient:
    """Async Chat sub-client"""
    
    def __init__(self, client: AsyncPrimeLLM):
        self._client = client
    
    async def create(
        self,
        model: str,
        messages: List[Dict[str, str]],
        **kwargs: Any,
    ) -> Dict[str, Any]:
        """Create a chat completion."""
        payload = {"model": model, "messages": messages, **kwargs}
        return await self._client.request(self._client._get_chat_path(), payload)
    
    async def stream(
        self,
        model: str,
        messages: List[Dict[str, str]],
        **kwargs: Any,
    ) -> AsyncIterator[Dict[str, Any]]:
        """Stream chat completion."""
        payload = {"model": model, "messages": messages, **kwargs}
        async for chunk in self._client.stream_request(self._client._get_chat_path(), payload):
            yield chunk


class AsyncEmbeddingsClient:
    """Async Embeddings sub-client"""
    
    def __init__(self, client: AsyncPrimeLLM):
        self._client = client
    
    async def create(
        self,
        input: Union[str, List[str]],
        model: str = "embed-1",
    ) -> Dict[str, Any]:
        """Create embeddings."""
        payload = {"model": model, "input": input}
        return await self._client.request("/v1/embeddings", payload)


class AsyncModelsClient:
    """Async Models sub-client"""
    
    def __init__(self, client: AsyncPrimeLLM):
        self._client = client
    
    async def list(self) -> Dict[str, Any]:
        """List available models."""
        return await self._client.request("/v1/models", method="GET")


class AsyncKeysClient:
    """Async API Keys sub-client"""
    
    def __init__(self, client: AsyncPrimeLLM):
        self._client = client
    
    async def list(self) -> Dict[str, Any]:
        """List API keys."""
        return await self._client.request("/v1/keys", method="GET")
    
    async def create(self, label: Optional[str] = None) -> Dict[str, Any]:
        """Create a new API key."""
        return await self._client.request("/v1/keys", {"label": label})
    
    async def revoke(self, key_id: int) -> Dict[str, Any]:
        """Revoke an API key."""
        return await self._client.request("/v1/keys/revoke", {"key_id": key_id})


class AsyncCreditsClient:
    """Async Credits sub-client"""
    
    def __init__(self, client: AsyncPrimeLLM):
        self._client = client
    
    async def get(self) -> Dict[str, Any]:
        """Get current credit balance."""
        return await self._client.request("/v1/credits", method="GET")


class AsyncBatchClient:
    """Async Batch sub-client (Phase 3)"""
    
    def __init__(self, client: AsyncPrimeLLM):
        self._client = client
    
    async def create(self, inputs: List[Dict[str, Any]], model: str) -> Dict[str, Any]:
        """Create a new batch job."""
        return await self._client.request("/v1/batch", {"inputs": inputs, "model": model})
    
    async def get(self, id: str) -> Dict[str, Any]:
        """Get batch job status."""
        return await self._client.request(f"/v1/batch/{id}", method="GET")
    
    async def cancel(self, id: str) -> Dict[str, Any]:
        """Cancel a batch job."""
        return await self._client.request(f"/v1/batch/{id}/cancel", {})
