"""Base interface for converting between LlamaIndex Workflow state and OpenAI-style responses.

A LlamaIndexWorkflowStateConverter implementation bridges:
  1. Incoming CreateResponse (wrapped in AgentRunContext) -> workflow input (StartEvent kwargs)
  2. Workflow StopEvent result -> final non-streaming Response
  3. Streaming workflow events -> ResponseStreamEvent sequence
  4. Declares whether streaming is supported for a given run context
"""

from __future__ import annotations

import time
from abc import ABC, abstractmethod
from typing import Any, AsyncGenerator, AsyncIterator, Dict

from azure.ai.agentserver.core.models import Response, ResponseStreamEvent
from azure.ai.agentserver.core.server.common.agent_run_context import AgentRunContext

from .request_converter import LlamaIndexWorkflowRequestConverter
from .response_converter import LlamaIndexWorkflowResponseConverter
from .stream_response_converter import LlamaIndexWorkflowStreamResponseConverter


class LlamaIndexWorkflowStateConverter(ABC):
    """
    Abstract base class for LlamaIndex Workflow input/output <-> response conversion.

    Implement this class to customize how requests are converted to workflow inputs
    and how workflow outputs are converted to responses.
    """

    @abstractmethod
    def supports_streaming(self, context: AgentRunContext) -> bool:
        """
        Return whether this converter supports streaming for the given context.

        Args:
            context: The context for the agent run.

        Returns:
            True if streaming is supported, False otherwise.
        """

    @abstractmethod
    def request_to_workflow_input(self, context: AgentRunContext) -> Dict[str, Any]:
        """
        Convert the incoming request to workflow input kwargs.

        Return a dict of keyword arguments that will be passed to workflow.run(**kwargs).

        Args:
            context: The context for the agent run.

        Returns:
            The workflow input as a dictionary of keyword arguments.

        Raises:
            ValueError: If the input is invalid.
        """

    @abstractmethod
    def result_to_response(self, result: Any, context: AgentRunContext) -> Response:
        """
        Convert a completed workflow result into a final non-streaming Response.

        Args:
            result: The completed workflow result (StopEvent.result).
            context: The context for the agent run.

        Returns:
            The final non-streaming Response object.
        """

    @abstractmethod
    async def stream_to_response_stream(
        self, event_stream: AsyncIterator[Any], context: AgentRunContext
    ) -> AsyncGenerator[ResponseStreamEvent, None]:
        """
        Convert an async iterator of workflow events into stream events.

        Yield ResponseStreamEvent objects in the correct order for the
        OpenAI Responses streaming contract.

        Args:
            event_stream: An async iterator of workflow events.
            context: The context for the agent run.

        Yields:
            ResponseStreamEvent objects.
        """


class LlamaIndexWorkflowDefaultStateConverter(LlamaIndexWorkflowStateConverter):
    """
    Default converter implementation for LlamaIndex Workflows.

    This converter handles:
    - Simple string input passed as 'input' to the workflow
    - List-based message input converted to appropriate format
    - StopEvent results converted to assistant messages
    - Streaming events from workflow.stream_events()
    """

    def supports_streaming(self, context: AgentRunContext) -> bool:
        """Check if streaming is requested and supported."""
        return context.request.get("stream", False)

    def request_to_workflow_input(self, context: AgentRunContext) -> Dict[str, Any]:
        """Convert request to workflow input kwargs."""
        converter = LlamaIndexWorkflowRequestConverter(context.request)
        return converter.convert()

    def result_to_response(self, result: Any, context: AgentRunContext) -> Response:
        """Convert workflow result to Response."""
        converter = LlamaIndexWorkflowResponseConverter(context, result)
        output = converter.convert()

        agent_id = context.get_agent_id_object()
        conversation = context.get_conversation_object()
        response = Response(
            object="response",
            id=context.response_id,
            agent=agent_id,
            conversation=conversation,
            metadata=context.request.get("metadata"),
            created_at=int(time.time()),
            output=output,
        )
        return response

    async def stream_to_response_stream(
        self, event_stream: AsyncIterator[Any], context: AgentRunContext
    ) -> AsyncGenerator[ResponseStreamEvent, None]:
        """Convert workflow event stream to response stream."""
        response_converter = LlamaIndexWorkflowStreamResponseConverter(event_stream, context)
        async for result in response_converter.convert():
            yield result
