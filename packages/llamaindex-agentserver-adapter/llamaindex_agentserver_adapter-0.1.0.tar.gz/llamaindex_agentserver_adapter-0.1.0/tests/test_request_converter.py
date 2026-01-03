"""Unit tests for LlamaIndexWorkflowRequestConverter."""

import pytest

from llamaindex_agentserver.models.request_converter import (
    LlamaIndexWorkflowRequestConverter,
)


class TestLlamaIndexWorkflowRequestConverter:
    """Tests for LlamaIndexWorkflowRequestConverter."""

    def test_convert_string_input(self, sample_string_input_request):
        """Test conversion of simple string input."""
        converter = LlamaIndexWorkflowRequestConverter(sample_string_input_request)
        result = converter.convert()

        assert "input" in result
        assert result["input"] == "Hello, how are you?"
        assert "instructions" in result
        assert result["instructions"] == "You are a helpful assistant."

    def test_convert_message_list_input(self, sample_message_list_request):
        """Test conversion of message list input."""
        converter = LlamaIndexWorkflowRequestConverter(sample_message_list_request)
        result = converter.convert()

        assert "messages" in result
        assert len(result["messages"]) == 3

        assert result["messages"][0]["role"] == "user"
        assert result["messages"][0]["content"] == "Hello!"

        assert result["messages"][1]["role"] == "assistant"
        assert result["messages"][1]["content"] == "Hi there!"

        assert result["messages"][2]["role"] == "user"
        assert result["messages"][2]["content"] == "How are you?"

        assert "input" in result
        assert result["input"] == "How are you?"

    def test_convert_function_call_input(self, sample_function_call_request):
        """Test conversion of function call input."""
        converter = LlamaIndexWorkflowRequestConverter(sample_function_call_request)
        result = converter.convert()

        assert "messages" in result
        assert len(result["messages"]) == 3

        func_call = result["messages"][1]
        assert func_call["type"] == "function_call"
        assert func_call["name"] == "get_weather"
        assert func_call["call_id"] == "call_123"
        assert func_call["arguments"] == {"location": "Seattle"}

        func_output = result["messages"][2]
        assert func_output["type"] == "function_call_output"
        assert func_output["call_id"] == "call_123"
        assert func_output["output"] == "Sunny, 72F"

    def test_convert_with_metadata(self):
        """Test conversion preserves metadata."""
        request = {
            "input": "Test input",
            "metadata": {"key": "value", "number": 42},
        }
        converter = LlamaIndexWorkflowRequestConverter(request)
        result = converter.convert()

        assert "metadata" in result
        assert result["metadata"]["key"] == "value"
        assert result["metadata"]["number"] == 42
