"""
PrimeLLM Python SDK v1.0.0 Tests

Unit tests for all Phase 1-3 features.
"""

import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from primellm import (
    PrimeLLM,
    AsyncPrimeLLM,
    execute_tools,
    has_tool_calls,
    create_tool,
    parse_tool_arguments,
    json_object,
    json_schema,
    PrimeLLMError,
)


# ============================================================
# Test Utilities
# ============================================================

pass_count = 0
fail_count = 0


def test(name, fn):
    global pass_count, fail_count
    try:
        fn()
        print(f"✅ {name}")
        pass_count += 1
    except Exception as e:
        print(f"❌ {name}: {e}")
        fail_count += 1


def assert_eq(actual, expected, message=None):
    if actual != expected:
        raise AssertionError(message or f"Expected {expected}, got {actual}")


# ============================================================
# Phase 1 Tests
# ============================================================

print("\n=== Phase 1: Must-Have Features ===\n")


def test_openai_compatible_mode():
    client = PrimeLLM(api_key="test_key", openai_compatible=True)
    assert_eq(client._get_chat_path(), "/v1/chat/completions")


def test_default_mode_path():
    client = PrimeLLM(api_key="test_key")
    assert_eq(client._get_chat_path(), "/v1/chat")


def test_create_tool():
    tool = create_tool("get_weather", "Get weather", {"type": "object"})
    assert_eq(tool["type"], "function")
    assert_eq(tool["function"]["name"], "get_weather")
    assert_eq(tool["function"]["description"], "Get weather")


def test_has_tool_calls_true():
    msg = {
        "role": "assistant",
        "content": None,
        "tool_calls": [{"id": "1", "type": "function", "function": {"name": "test", "arguments": "{}"}}]
    }
    assert has_tool_calls(msg), "Should detect tool calls"


def test_has_tool_calls_false():
    msg = {"role": "assistant", "content": "Hello"}
    assert not has_tool_calls(msg), "Should not detect tool calls"


def test_parse_tool_arguments():
    tool_call = {
        "id": "1",
        "type": "function",
        "function": {"name": "test", "arguments": '{"location":"Paris"}'}
    }
    args = parse_tool_arguments(tool_call)
    assert_eq(args["location"], "Paris")


def test_parse_tool_arguments_invalid():
    tool_call = {
        "id": "1",
        "type": "function",
        "function": {"name": "test", "arguments": "invalid json"}
    }
    args = parse_tool_arguments(tool_call)
    assert_eq(args, None)


def test_execute_tools():
    assistant_msg = {
        "role": "assistant",
        "content": None,
        "tool_calls": [{
            "id": "call_1",
            "type": "function",
            "function": {"name": "get_weather", "arguments": '{"city":"Paris"}'}
        }]
    }
    
    tools = {
        "get_weather": lambda args: {"temp": 22, "city": args["city"]}
    }
    
    results = execute_tools(assistant_msg, tools)
    
    assert_eq(len(results), 1)
    assert_eq(results[0]["role"], "tool")
    assert_eq(results[0]["tool_call_id"], "call_1")
    
    import json
    content = json.loads(results[0]["content"])
    assert_eq(content["temp"], 22)
    assert_eq(content["city"], "Paris")


def test_execute_tools_unknown():
    assistant_msg = {
        "role": "assistant",
        "content": None,
        "tool_calls": [{
            "id": "call_1",
            "type": "function",
            "function": {"name": "unknown_tool", "arguments": "{}"}
        }]
    }
    
    results = execute_tools(assistant_msg, {})
    
    assert_eq(len(results), 1)
    import json
    content = json.loads(results[0]["content"])
    assert "error" in content and "Unknown tool" in content["error"]


def test_env_var_api_key():
    original = os.environ.get("PRIMELLM_API_KEY")
    os.environ["PRIMELLM_API_KEY"] = "env_test_key"
    
    client = PrimeLLM()
    assert_eq(client.api_key, "env_test_key")
    
    if original:
        os.environ["PRIMELLM_API_KEY"] = original
    else:
        del os.environ["PRIMELLM_API_KEY"]


def test_missing_api_key():
    original = os.environ.get("PRIMELLM_API_KEY")
    if "PRIMELLM_API_KEY" in os.environ:
        del os.environ["PRIMELLM_API_KEY"]
    
    threw = False
    try:
        PrimeLLM()
    except PrimeLLMError as e:
        threw = True
        assert "required" in str(e).lower()
    
    if original:
        os.environ["PRIMELLM_API_KEY"] = original
    
    assert threw, "Should throw without API key"


test("OpenAI-compatible mode changes endpoint path", test_openai_compatible_mode)
test("Default mode uses /v1/chat endpoint", test_default_mode_path)
test("createTool creates valid tool definition", test_create_tool)
test("has_tool_calls detects tool calls in message", test_has_tool_calls_true)
test("has_tool_calls returns False for no tool calls", test_has_tool_calls_false)
test("parse_tool_arguments parses JSON arguments", test_parse_tool_arguments)
test("parse_tool_arguments returns None for invalid JSON", test_parse_tool_arguments_invalid)
test("execute_tools executes tool functions", test_execute_tools)
test("execute_tools handles unknown tools", test_execute_tools_unknown)
test("Client reads API key from env", test_env_var_api_key)
test("Client throws if no API key provided", test_missing_api_key)


# ============================================================
# Phase 2 Tests
# ============================================================

print("\n=== Phase 2: Developer Experience ===\n")


def test_run_method_exists():
    client = PrimeLLM(api_key="test_key")
    assert callable(client.run), "run method should be callable"


def test_tokens_count_string():
    client = PrimeLLM(api_key="test_key")
    count = client.tokens.count("Hello world")
    assert count > 0, "Should count tokens"


def test_tokens_count_messages():
    client = PrimeLLM(api_key="test_key")
    count = client.tokens.count([
        {"role": "user", "content": "Hello"},
        {"role": "assistant", "content": "Hi there!"}
    ])
    assert count > 0, "Should count tokens in messages"


def test_structured_json_object():
    fmt = json_object()
    assert_eq(fmt["type"], "json_object")


def test_structured_json_schema():
    fmt = json_schema("TestSchema", {"type": "object"})
    assert_eq(fmt["type"], "json_schema")
    assert_eq(fmt["json_schema"]["name"], "TestSchema")


test("run() method exists on client", test_run_method_exists)
test("tokens.count() works with string", test_tokens_count_string)
test("tokens.count() works with messages", test_tokens_count_messages)
test("json_object() creates valid format", test_structured_json_object)
test("json_schema() creates valid format", test_structured_json_schema)


# ============================================================
# Phase 3 Tests
# ============================================================

print("\n=== Phase 3: Differentiators ===\n")


def test_app_attribution():
    client = PrimeLLM(
        api_key="test_key",
        app_name="TestApp",
        app_url="https://test.com"
    )
    headers = client._headers()
    assert_eq(headers.get("X-PrimeLLM-App-Name"), "TestApp")
    assert_eq(headers.get("X-PrimeLLM-App-Url"), "https://test.com")


def test_batch_client_exists():
    client = PrimeLLM(api_key="test_key")
    assert client.batch, "Batch client should exist"
    assert callable(client.batch.create)
    assert callable(client.batch.get)
    assert callable(client.batch.cancel)


def test_async_client_exists():
    # Just check import works
    assert AsyncPrimeLLM, "AsyncPrimeLLM should be importable"


test("App attribution headers can be configured", test_app_attribution)
test("batch client exists with create/get/cancel methods", test_batch_client_exists)
test("AsyncPrimeLLM client exists", test_async_client_exists)


# ============================================================
# Backward Compatibility Tests
# ============================================================

print("\n=== Backward Compatibility ===\n")


def test_v020_style_creation():
    client = PrimeLLM(api_key="test_key")
    assert client.chat, "chat client should exist"
    assert client.embeddings, "embeddings client should exist"
    assert client.models, "models client should exist"
    assert client.credits, "credits client should exist"
    assert client.keys, "keys client should exist"
    assert client.tokens, "tokens client should exist"


def test_chat_create_exists():
    client = PrimeLLM(api_key="test_key")
    assert callable(client.chat.create)


def test_chat_stream_exists():
    client = PrimeLLM(api_key="test_key")
    assert callable(client.chat.stream)


test("v0.2.0 style client creation works", test_v020_style_creation)
test("chat.create method exists", test_chat_create_exists)
test("chat.stream method exists", test_chat_stream_exists)


# ============================================================
# Summary
# ============================================================

print("\n=== Test Summary ===\n")
print(f"Passed: {pass_count}")
print(f"Failed: {fail_count}")
print(f"Total: {pass_count + fail_count}")

if fail_count > 0:
    sys.exit(1)
