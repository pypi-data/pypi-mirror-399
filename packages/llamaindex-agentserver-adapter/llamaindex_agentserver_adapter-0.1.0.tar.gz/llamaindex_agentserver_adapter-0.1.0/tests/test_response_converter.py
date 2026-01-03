"""Unit tests for LlamaIndexWorkflowResponseConverter."""

from unittest.mock import MagicMock

import pytest

from llamaindex_agentserver.models.response_converter import (
    LlamaIndexWorkflowResponseConverter,
)


class MockIdGenerator:
    """Mock ID generator for testing."""

    def __init__(self):
        self.counter = 0

    def generate_message_id(self):
        self.counter += 1
        return f"msg_{self.counter:03d}"

    def generate_function_call_id(self):
        self.counter += 1
        return f"call_{self.counter:03d}"

    def generate_function_output_id(self):
        self.counter += 1
        return f"output_{self.counter:03d}"


@pytest.fixture
def mock_context():
    """Create a mock AgentRunContext."""
    context = MagicMock()
    context.id_generator = MockIdGenerator()
    return context


class TestLlamaIndexWorkflowResponseConverter:
    """Tests for LlamaIndexWorkflowResponseConverter."""

    def test_convert_string_result(self, mock_context):
        """Test conversion of simple string result."""
        result = "Hello, I'm doing great!"
        converter = LlamaIndexWorkflowResponseConverter(mock_context, result)
        output = converter.convert()

        assert len(output) == 1
        assert output[0].status == "completed"
        assert len(output[0].content) == 1
        assert output[0].content[0]["text"] == "Hello, I'm doing great!"

    def test_convert_none_result(self, mock_context):
        """Test conversion of None result."""
        converter = LlamaIndexWorkflowResponseConverter(mock_context, None)
        output = converter.convert()

        assert len(output) == 0

    def test_convert_dict_with_response_key(self, mock_context):
        """Test conversion of dict result with 'response' key."""
        result = {"response": "This is the response"}
        converter = LlamaIndexWorkflowResponseConverter(mock_context, result)
        output = converter.convert()

        assert len(output) == 1
        assert output[0].content[0]["text"] == "This is the response"

    def test_convert_dict_with_text_key(self, mock_context):
        """Test conversion of dict result with 'text' key."""
        result = {"text": "This is the text"}
        converter = LlamaIndexWorkflowResponseConverter(mock_context, result)
        output = converter.convert()

        assert len(output) == 1
        assert output[0].content[0]["text"] == "This is the text"

    def test_convert_stop_event_like_object(self, mock_context):
        """Test conversion of StopEvent-like object with result attribute."""

        class MockStopEvent:
            def __init__(self, result):
                self.result = result

        stop_event = MockStopEvent("Workflow completed successfully")
        converter = LlamaIndexWorkflowResponseConverter(mock_context, stop_event)
        output = converter.convert()

        assert len(output) == 1
        assert output[0].content[0]["text"] == "Workflow completed successfully"

    def test_convert_list_result(self, mock_context):
        """Test conversion of list result."""
        result = ["First message", "Second message"]
        converter = LlamaIndexWorkflowResponseConverter(mock_context, result)
        output = converter.convert()

        assert len(output) == 2
        assert output[0].content[0]["text"] == "First message"
        assert output[1].content[0]["text"] == "Second message"
