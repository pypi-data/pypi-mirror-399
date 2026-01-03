"""Request converter for LlamaIndex Workflows.

Converts incoming OpenAI-style CreateResponse requests into keyword arguments
suitable for passing to workflow.run(**kwargs).
"""

import json
import logging
from typing import Any, Dict, List

from azure.ai.agentserver.core.models import CreateResponse, openai as openai_models, projects as project_models

logger = logging.getLogger(__name__)


class LlamaIndexWorkflowRequestConverter:
    """
    Converts CreateResponse requests to LlamaIndex Workflow input format.

    The converter extracts:
    - input: The main user input (string or structured messages)
    - instructions: System instructions to be included
    - Additional parameters from the request
    """

    def __init__(self, data: CreateResponse):
        self.data: CreateResponse = data

    def convert(self) -> Dict[str, Any]:
        """
        Convert the CreateResponse input to a format suitable for LlamaIndex Workflow.

        The output dict can be passed directly to workflow.run(**output).

        Returns:
            Dictionary of keyword arguments for the workflow.

        Raises:
            ValueError: If the input type is not supported.
        """
        workflow_input: Dict[str, Any] = {}

        # Handle instructions (system message)
        instructions = self.data.get("instructions")
        if instructions and isinstance(instructions, str):
            workflow_input["instructions"] = instructions

        # Handle main input
        input_data = self.data.get("input")
        if isinstance(input_data, str):
            workflow_input["input"] = input_data
        elif isinstance(input_data, list):
            messages = self._convert_message_list(input_data)
            workflow_input["messages"] = messages
            last_user_input = self._extract_last_user_input(input_data)
            if last_user_input:
                workflow_input["input"] = last_user_input
        elif input_data is not None:
            raise ValueError(f"Unsupported input type: {type(input_data)}, {input_data}")

        # Include any additional metadata
        metadata = self.data.get("metadata")
        if metadata:
            workflow_input["metadata"] = metadata

        return workflow_input

    def _convert_message_list(self, items: List[Dict]) -> List[Dict[str, Any]]:
        """Convert a list of ResponseInputItemParam to workflow-compatible messages."""
        messages = []
        for item in items:
            converted = self._convert_input_item(item)
            if converted:
                messages.append(converted)
        return messages

    def _convert_input_item(self, item: Dict) -> Dict[str, Any]:
        """Convert a single ResponseInputItemParam to a workflow message."""
        item_type = item.get("type", project_models.ItemType.MESSAGE)

        if item_type == project_models.ItemType.MESSAGE:
            return self._convert_message(item)
        elif item_type == project_models.ItemType.FUNCTION_CALL:
            return self._convert_function_call(item)
        elif item_type == project_models.ItemType.FUNCTION_CALL_OUTPUT:
            return self._convert_function_call_output(item)
        else:
            logger.warning(f"Unsupported item type: {item_type}, skipping")
            return {}

    def _convert_message(self, message: Dict) -> Dict[str, Any]:
        """Convert a message dict to workflow format."""
        content = message.get("content")
        role = message.get("role", project_models.ResponsesMessageRole.USER)

        if not content:
            raise ValueError(f"Message missing content: {message}")

        role_mapping = {
            project_models.ResponsesMessageRole.USER: "user",
            project_models.ResponsesMessageRole.SYSTEM: "system",
            project_models.ResponsesMessageRole.ASSISTANT: "assistant",
        }
        mapped_role = role_mapping.get(role, str(role))

        if isinstance(content, str):
            return {"role": mapped_role, "content": content}
        elif isinstance(content, list):
            converted_content = self._convert_content_list(content)
            return {"role": mapped_role, "content": converted_content}
        else:
            raise ValueError(f"Unsupported content type: {type(content)}")

    def _convert_function_call(self, item: Dict) -> Dict[str, Any]:
        """Convert a function call item to workflow format."""
        try:
            func_call = openai_models.ResponseFunctionToolCallParam(**item)
            argument = func_call.get("arguments", None)
            args = json.loads(argument) if argument else {}
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON in function call arguments: {item}") from e
        except Exception as e:
            raise ValueError(f"Invalid function call item: {item}") from e

        return {
            "type": "function_call",
            "role": "assistant",
            "call_id": func_call.get("call_id"),
            "name": func_call.get("name"),
            "arguments": args,
        }

    def _convert_function_call_output(self, item: Dict) -> Dict[str, Any]:
        """Convert a function call output item to workflow format."""
        try:
            func_output = openai_models.response_input_item_param.FunctionCallOutput(**item)
        except Exception as e:
            raise ValueError(f"Invalid function call output item: {item}") from e

        output = func_output.get("output", "")
        if isinstance(output, list):
            output = self._convert_content_list(output)

        return {
            "type": "function_call_output",
            "role": "tool",
            "call_id": func_output.get("call_id"),
            "output": output,
        }

    def _convert_content_list(self, content: List[Dict]) -> List[Dict]:
        """Convert a list of content items."""
        result = []
        for item in content:
            converted = self._convert_content_item(item)
            result.append(converted)
        return result

    def _convert_content_item(self, content: Dict) -> Dict:
        """Convert a single content item."""
        content_type_mapping = {
            project_models.ItemContentType.INPUT_TEXT: "text",
            project_models.ItemContentType.INPUT_AUDIO: "audio",
            project_models.ItemContentType.INPUT_IMAGE: "image",
            project_models.ItemContentType.INPUT_FILE: "file",
            project_models.ItemContentType.OUTPUT_TEXT: "text",
            project_models.ItemContentType.OUTPUT_AUDIO: "audio",
        }

        res = content.copy()
        content_type = content.get("type")
        res["type"] = content_type_mapping.get(content_type, content_type)
        return res

    def _extract_last_user_input(self, items: List[Dict]) -> str:
        """Extract the last user message content from a list of items."""
        for item in reversed(items):
            item_type = item.get("type", project_models.ItemType.MESSAGE)
            if item_type == project_models.ItemType.MESSAGE:
                role = item.get("role", project_models.ResponsesMessageRole.USER)
                if role == project_models.ResponsesMessageRole.USER:
                    content = item.get("content", "")
                    if isinstance(content, str):
                        return content
                    elif isinstance(content, list):
                        for c in content:
                            if c.get("type") in ("text", project_models.ItemContentType.INPUT_TEXT):
                                return c.get("text", "")
        return ""
