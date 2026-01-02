"""
PrimeLLM Tool Calling Utilities

Helper functions for working with tool calls in chat completions.
"""

from typing import Any, Callable, Dict, List, Optional, Union
import json


# Type aliases
ToolExecutor = Callable[[Dict[str, Any]], Any]
ToolRegistry = Dict[str, ToolExecutor]


def execute_tools(
    assistant_message: Dict[str, Any],
    tools: ToolRegistry
) -> List[Dict[str, Any]]:
    """
    Execute all tool calls from an assistant message.
    
    Takes the assistant message containing tool_calls, matches them against
    a registry of tool executors, executes them, and returns tool role messages
    ready to be appended to the conversation history.
    
    Args:
        assistant_message: The assistant message containing tool_calls
        tools: Registry mapping tool names to executor functions
        
    Returns:
        List of tool role messages
        
    Example:
        tools = {
            "get_weather": lambda args: {"temp": 72, "condition": "sunny"},
            "search": lambda args: [{"title": "Result 1"}]
        }
        
        response = client.chat.create(...)
        assistant_msg = response["choices"][0]["message"]
        
        if assistant_msg.get("tool_calls"):
            tool_messages = execute_tools(assistant_msg, tools)
            # tool_messages ready to append to conversation
    """
    tool_calls = assistant_message.get("tool_calls", [])
    if not tool_calls:
        return []
    
    results = []
    for tool_call in tool_calls:
        tool_call_id = tool_call.get("id", "")
        function_info = tool_call.get("function", {})
        function_name = function_info.get("name", "")
        
        executor = tools.get(function_name)
        
        if not executor:
            results.append({
                "role": "tool",
                "tool_call_id": tool_call_id,
                "content": json.dumps({"error": f"Unknown tool: {function_name}"})
            })
            continue
        
        try:
            args_str = function_info.get("arguments", "{}")
            args = json.loads(args_str)
            result = executor(args)
            results.append({
                "role": "tool",
                "tool_call_id": tool_call_id,
                "content": json.dumps(result) if not isinstance(result, str) else result
            })
        except Exception as e:
            results.append({
                "role": "tool",
                "tool_call_id": tool_call_id,
                "content": json.dumps({"error": str(e)})
            })
    
    return results


def has_tool_calls(message: Dict[str, Any]) -> bool:
    """
    Check if a message has tool calls that need execution.
    
    Args:
        message: The message to check
        
    Returns:
        True if the message has tool calls
    """
    return (
        message.get("role") == "assistant" and
        isinstance(message.get("tool_calls"), list) and
        len(message.get("tool_calls", [])) > 0
    )


def create_tool(
    name: str,
    description: str,
    parameters: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Create a tool definition from a function.
    
    Args:
        name: Tool name
        description: Tool description
        parameters: JSON Schema for parameters
        
    Returns:
        Tool definition object
        
    Example:
        weather_tool = create_tool(
            "get_weather",
            "Get current weather for a location",
            {
                "type": "object",
                "properties": {
                    "location": {"type": "string", "description": "City name"}
                },
                "required": ["location"]
            }
        )
    """
    return {
        "type": "function",
        "function": {
            "name": name,
            "description": description,
            "parameters": parameters
        }
    }


def parse_tool_arguments(tool_call: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """
    Parse tool call arguments safely.
    
    Args:
        tool_call: The tool call to parse
        
    Returns:
        Parsed arguments dict or None on error
    """
    try:
        function_info = tool_call.get("function", {})
        args_str = function_info.get("arguments", "{}")
        return json.loads(args_str)
    except:
        return None
