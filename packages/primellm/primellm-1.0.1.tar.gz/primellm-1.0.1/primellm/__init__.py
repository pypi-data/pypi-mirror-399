"""
PrimeLLM Python SDK v1.0.0

Official Python client for the PrimeLLM unified AI API.
Supports streaming, tool calling, multi-turn agents, and structured outputs.
"""

from .client import PrimeLLM
from .async_client import AsyncPrimeLLM
from .errors import (
    PrimeLLMError,
    AuthenticationError,
    InsufficientCreditsError,
    RateLimitError,
    NotFoundError,
    ValidationError,
    ServerError,
)
from .tokenizer import count_tokens, set_tokenizer_adapter
from .tools import execute_tools, has_tool_calls, create_tool, parse_tool_arguments
from .structured import from_pydantic, json_object, json_schema, grammar

__version__ = "1.0.1"
__all__ = [
    # Main clients
    "PrimeLLM",
    "AsyncPrimeLLM",
    
    # Errors
    "PrimeLLMError",
    "AuthenticationError",
    "InsufficientCreditsError",
    "RateLimitError",
    "NotFoundError",
    "ValidationError",
    "ServerError",
    
    # Tokenizer
    "count_tokens",
    "set_tokenizer_adapter",
    
    # Tools
    "execute_tools",
    "has_tool_calls",
    "create_tool",
    "parse_tool_arguments",
    
    # Structured outputs
    "from_pydantic",
    "json_object",
    "json_schema",
    "grammar",
]
