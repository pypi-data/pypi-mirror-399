"""
PrimeLLM Structured Outputs Utilities

Helpers for working with structured outputs and JSON schemas.
"""

from typing import Any, Dict, Type, Optional

try:
    from pydantic import BaseModel
    PYDANTIC_AVAILABLE = True
except ImportError:
    PYDANTIC_AVAILABLE = False
    BaseModel = None  # type: ignore


def from_pydantic(
    model: Type,
    name: Optional[str] = None,
    description: Optional[str] = None,
    strict: bool = True
) -> Dict[str, Any]:
    """
    Convert a Pydantic model to a JSON schema response_format.
    
    Args:
        model: The Pydantic model class
        name: Schema name (defaults to model class name)
        description: Schema description (defaults to model docstring)
        strict: Whether to enforce strict schema validation
        
    Returns:
        response_format dict for use in chat.create()
        
    Example:
        from pydantic import BaseModel
        
        class WeatherResponse(BaseModel):
            temperature: float
            condition: str
            
        response = client.chat.create(
            model="gpt-5.1",
            messages=[...],
            response_format=from_pydantic(WeatherResponse)
        )
        
    Raises:
        ImportError: If Pydantic is not installed
        TypeError: If model is not a Pydantic BaseModel
    """
    if not PYDANTIC_AVAILABLE:
        raise ImportError(
            "Pydantic is required for from_pydantic(). "
            "Install it with: pip install pydantic"
        )
    
    if not (isinstance(model, type) and issubclass(model, BaseModel)):
        raise TypeError(f"Expected Pydantic BaseModel, got {type(model)}")
    
    schema = model.model_json_schema()
    
    return {
        "type": "json_schema",
        "json_schema": {
            "name": name or model.__name__,
            "description": description or model.__doc__ or f"Schema for {model.__name__}",
            "schema": schema,
            "strict": strict
        }
    }


def json_object() -> Dict[str, Any]:
    """
    Create a JSON object response_format.
    
    Returns:
        response_format dict for JSON object output
        
    Example:
        response = client.chat.create(
            model="gpt-5.1",
            messages=[...],
            response_format=json_object()
        )
    """
    return {"type": "json_object"}


def json_schema(
    name: str,
    schema: Dict[str, Any],
    description: Optional[str] = None,
    strict: bool = True
) -> Dict[str, Any]:
    """
    Create a JSON schema response_format.
    
    Args:
        name: Schema name
        schema: JSON Schema definition
        description: Schema description
        strict: Whether to enforce strict validation
        
    Returns:
        response_format dict for JSON schema output
        
    Example:
        response = client.chat.create(
            model="gpt-5.1",
            messages=[...],
            response_format=json_schema(
                name="WeatherResponse",
                schema={
                    "type": "object",
                    "properties": {
                        "temperature": {"type": "number"},
                        "condition": {"type": "string"}
                    },
                    "required": ["temperature", "condition"]
                }
            )
        )
    """
    return {
        "type": "json_schema",
        "json_schema": {
            "name": name,
            "description": description or f"Schema for {name}",
            "schema": schema,
            "strict": strict
        }
    }


def grammar(grammar_str: str) -> Dict[str, Any]:
    """
    Create a grammar-based response_format (Phase 3 feature).
    
    Args:
        grammar_str: Grammar specification string
        
    Returns:
        response_format dict for grammar-based output
    """
    return {
        "type": "grammar",
        "grammar": grammar_str
    }
