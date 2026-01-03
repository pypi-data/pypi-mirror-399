"""Test fixtures for llamaindex-agentserver-adapter."""

import pytest


@pytest.fixture
def sample_string_input_request():
    """Sample request with string input."""
    return {
        "input": "Hello, how are you?",
        "instructions": "You are a helpful assistant.",
        "stream": False,
    }


@pytest.fixture
def sample_message_list_request():
    """Sample request with message list input."""
    return {
        "input": [
            {"type": "message", "role": "user", "content": "Hello!"},
            {"type": "message", "role": "assistant", "content": "Hi there!"},
            {"type": "message", "role": "user", "content": "How are you?"},
        ],
        "stream": False,
    }


@pytest.fixture
def sample_function_call_request():
    """Sample request with function call."""
    return {
        "input": [
            {"type": "message", "role": "user", "content": "What's the weather?"},
            {
                "type": "function_call",
                "call_id": "call_123",
                "name": "get_weather",
                "arguments": '{"location": "Seattle"}',
            },
            {
                "type": "function_call_output",
                "call_id": "call_123",
                "output": "Sunny, 72F",
            },
        ],
        "stream": False,
    }
