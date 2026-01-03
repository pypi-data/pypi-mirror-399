"""Response converter for LlamaIndex Workflows.

Converts workflow StopEvent results into OpenAI-style response output items.
"""

import json
import logging
from typing import Any, Dict, List, Union

from azure.ai.agentserver.core.models import projects as project_models
from azure.ai.agentserver.core.server.common.agent_run_context import AgentRunContext

logger = logging.getLogger(__name__)


class LlamaIndexWorkflowResponseConverter:
    """
    Converts LlamaIndex Workflow results to OpenAI-style response output.

    Handles various result types:
    - String results: Converted to assistant text message
    - Dict results: Inspected for structured output
    - List results: Converted to multiple output items
    - Pydantic models: Serialized to dict and processed
    """

    def __init__(self, context: AgentRunContext, result: Any):
        self.context = context
        self.result = result

    def convert(self) -> List[project_models.ItemResource]:
        """
        Convert the workflow result to a list of output items.

        Returns:
            List of ItemResource objects representing the output.
        """
        if self.result is None:
            return []

        result_value = self._extract_result_value(self.result)

        if result_value is None:
            return []

        if isinstance(result_value, str):
            return [self._convert_string_result(result_value)]
        elif isinstance(result_value, dict):
            return self._convert_dict_result(result_value)
        elif isinstance(result_value, list):
            return self._convert_list_result(result_value)
        else:
            try:
                str_result = str(result_value)
                return [self._convert_string_result(str_result)]
            except Exception as e:
                logger.error(f"Failed to convert result to string: {e}")
                return []

    def _extract_result_value(self, result: Any) -> Any:
        """Extract the actual result value from various result types."""
        if hasattr(result, "result"):
            return result.result

        if hasattr(result, "model_dump"):
            try:
                return result.model_dump()
            except Exception:
                pass

        if hasattr(result, "get"):
            return result.get("result", result)

        return result

    def _convert_string_result(self, text: str) -> project_models.ItemResource:
        """Convert a string result to an assistant message."""
        return project_models.ResponsesAssistantMessageItemResource(
            content=[
                project_models.ItemContent({
                    "type": project_models.ItemContentType.OUTPUT_TEXT,
                    "text": text,
                    "annotations": [],
                })
            ],
            id=self.context.id_generator.generate_message_id(),
            status="completed",
        )

    def _convert_dict_result(self, result: Dict[str, Any]) -> List[project_models.ItemResource]:
        """Convert a dict result to output items."""
        output_items = []

        if "response" in result:
            output_items.extend(self._convert_value_to_items(result["response"]))
        elif "output" in result:
            output_items.extend(self._convert_value_to_items(result["output"]))
        elif "text" in result:
            output_items.append(self._convert_string_result(result["text"]))
        elif "message" in result:
            output_items.extend(self._convert_value_to_items(result["message"]))
        elif "messages" in result:
            for msg in result["messages"]:
                output_items.extend(self._convert_message_to_items(msg))
        elif "tool_calls" in result or "function_call" in result:
            output_items.extend(self._convert_function_call_result(result))
        else:
            json_str = json.dumps(result, indent=2, default=str)
            output_items.append(self._convert_string_result(json_str))

        return output_items if output_items else [self._convert_string_result(json.dumps(result, default=str))]

    def _convert_list_result(self, result: List[Any]) -> List[project_models.ItemResource]:
        """Convert a list result to output items."""
        output_items = []
        for item in result:
            output_items.extend(self._convert_value_to_items(item))
        return output_items

    def _convert_value_to_items(self, value: Any) -> List[project_models.ItemResource]:
        """Convert any value to output items."""
        if isinstance(value, str):
            return [self._convert_string_result(value)]
        elif isinstance(value, dict):
            return self._convert_dict_result(value)
        elif isinstance(value, list):
            return self._convert_list_result(value)
        else:
            return [self._convert_string_result(str(value))]

    def _convert_message_to_items(self, message: Union[str, Dict]) -> List[project_models.ItemResource]:
        """Convert a message (string or dict) to output items."""
        if isinstance(message, str):
            return [self._convert_string_result(message)]
        elif isinstance(message, dict):
            role = message.get("role", "assistant")
            content = message.get("content", "")

            if role == "assistant":
                if isinstance(content, str):
                    return [self._convert_string_result(content)]
                elif isinstance(content, list):
                    content_items = []
                    for part in content:
                        if isinstance(part, str):
                            content_items.append(project_models.ItemContent({
                                "type": project_models.ItemContentType.OUTPUT_TEXT,
                                "text": part,
                                "annotations": [],
                            }))
                        elif isinstance(part, dict):
                            part_type = part.get("type", "text")
                            if part_type == "text":
                                content_items.append(project_models.ItemContent({
                                    "type": project_models.ItemContentType.OUTPUT_TEXT,
                                    "text": part.get("text", ""),
                                    "annotations": [],
                                }))
                    if content_items:
                        return [project_models.ResponsesAssistantMessageItemResource(
                            content=content_items,
                            id=self.context.id_generator.generate_message_id(),
                            status="completed",
                        )]
            elif role == "user":
                if isinstance(content, str):
                    return [project_models.ResponsesUserMessageItemResource(
                        content=[project_models.ItemContent({
                            "type": project_models.ItemContentType.INPUT_TEXT,
                            "text": content,
                        })],
                        id=self.context.id_generator.generate_message_id(),
                        status="completed",
                    )]
            elif role == "system":
                if isinstance(content, str):
                    return [project_models.ResponsesSystemMessageItemResource(
                        content=[project_models.ItemContent({
                            "type": project_models.ItemContentType.INPUT_TEXT,
                            "text": content,
                        })],
                        id=self.context.id_generator.generate_message_id(),
                        status="completed",
                    )]

        return [self._convert_string_result(str(message))]

    def _convert_function_call_result(self, result: Dict[str, Any]) -> List[project_models.ItemResource]:
        """Convert a function call result to output items."""
        output_items = []

        tool_calls = result.get("tool_calls", [])
        if not tool_calls and "function_call" in result:
            tool_calls = [result["function_call"]]

        for call in tool_calls:
            name = call.get("name", call.get("function", {}).get("name", ""))
            call_id = call.get("id", call.get("call_id", ""))
            arguments = call.get("arguments", call.get("function", {}).get("arguments", "{}"))

            if isinstance(arguments, dict):
                arguments = json.dumps(arguments)

            output_items.append(project_models.FunctionToolCallItemResource(
                call_id=call_id or self.context.id_generator.generate_function_call_id(),
                name=name,
                arguments=arguments,
                id=self.context.id_generator.generate_function_call_id(),
                status="completed",
            ))

        return output_items
