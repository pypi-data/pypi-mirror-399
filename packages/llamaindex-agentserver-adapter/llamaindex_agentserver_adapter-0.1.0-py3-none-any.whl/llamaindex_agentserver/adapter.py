"""LlamaIndex Workflow adapter for Azure AI Agent Server.

This module provides the main adapter class that bridges LlamaIndex Workflows
with the Azure AI Agent Server infrastructure.
"""

import os
from typing import Optional

from azure.ai.agentserver.core.constants import Constants
from azure.ai.agentserver.core.logger import get_logger
from azure.ai.agentserver.core.server.base import FoundryCBAgent
from azure.ai.agentserver.core.server.common.agent_run_context import AgentRunContext

from .models import (
    LlamaIndexWorkflowDefaultStateConverter,
    LlamaIndexWorkflowStateConverter,
)

logger = get_logger()


class LlamaIndexWorkflowAdapter(FoundryCBAgent):
    """
    Adapter for LlamaIndex Workflow agents.

    This adapter enables LlamaIndex Workflows to be hosted as Azure AI agents,
    providing HTTP endpoints for running workflows and streaming results.

    Attributes:
        workflow: The LlamaIndex Workflow instance being adapted.
        timeout: Timeout for workflow execution in seconds.
        state_converter: The state converter handling input/output transformation.

    Example:
        >>> from workflows import Workflow, step
        >>> from workflows.events import StartEvent, StopEvent
        >>> from llamaindex_agentserver import from_workflow
        >>>
        >>> class MyWorkflow(Workflow):
        ...     @step
        ...     async def process(self, ev: StartEvent) -> StopEvent:
        ...         return StopEvent(result=f"Processed: {ev.input}")
        >>>
        >>> workflow = MyWorkflow()
        >>> adapter = from_workflow(workflow)
        >>> adapter.run(port=8088)
    """

    def __init__(
        self,
        workflow,
        state_converter: Optional[LlamaIndexWorkflowStateConverter] = None,
        timeout: Optional[float] = None,
    ):
        """
        Initialize the LlamaIndexWorkflowAdapter with a Workflow instance.

        Args:
            workflow: The LlamaIndex Workflow to adapt.
            state_converter: Optional custom state converter. If not provided,
                uses the default converter which handles standard input/output formats.
            timeout: Optional timeout override for workflow execution.
        """
        super().__init__()
        self.workflow = workflow
        self.timeout = timeout or getattr(workflow, "timeout", None)
        self.azure_ai_tracer = None

        if state_converter:
            self.state_converter = state_converter
        else:
            self.state_converter = LlamaIndexWorkflowDefaultStateConverter()

    async def agent_run(self, context: AgentRunContext):
        """
        Execute the workflow based on the incoming request.

        Handles both streaming and non-streaming modes.

        Args:
            context: The agent run context containing the request.

        Returns:
            The response or async generator of stream events.
        """
        input_data = self.state_converter.request_to_workflow_input(context)
        logger.debug(f"Converted input data: {input_data}")

        if not context.stream or not self.state_converter.supports_streaming(context):
            response = await self._run_non_streaming(input_data, context)
            return response
        return self._run_streaming(input_data, context)

    async def _run_non_streaming(self, input_data: dict, context: AgentRunContext):
        """
        Run the workflow in non-streaming mode.

        Args:
            input_data: The workflow input keyword arguments.
            context: The agent run context.

        Returns:
            The complete response.
        """
        try:
            logger.info(f"Starting non-streaming workflow run {context.response_id}")

            # Run the workflow
            result = await self.workflow.run(**input_data)

            # Convert result to response
            output = self.state_converter.result_to_response(result, context)
            return output

        except Exception as e:
            logger.error(f"Error during workflow run: {e}")
            raise

    async def _run_streaming(self, input_data: dict, context: AgentRunContext):
        """
        Run the workflow in streaming mode.

        Args:
            input_data: The workflow input keyword arguments.
            context: The agent run context.

        Returns:
            An async generator yielding response stream events.
        """
        try:
            logger.info(f"Starting streaming workflow run {context.response_id}")

            # Get the workflow handler for streaming
            handler = self.workflow.run(**input_data)

            # Stream events
            async def event_stream():
                async for event in handler.stream_events():
                    yield event

            async for result in self.state_converter.stream_to_response_stream(
                event_stream(), context
            ):
                yield result

        except Exception as e:
            logger.error(f"Error during streaming workflow run: {e}")
            raise

    def init_tracing_internal(self, exporter_endpoint=None, app_insights_conn_str=None):
        """
        Initialize internal tracing for LlamaIndex observability.

        Args:
            exporter_endpoint: Optional OTLP exporter endpoint.
            app_insights_conn_str: Optional Application Insights connection string.
        """
        if app_insights_conn_str:
            try:
                logger.info("Setting up Application Insights tracing for LlamaIndex")
            except Exception as e:
                logger.warning(f"Failed to setup Application Insights for LlamaIndex: {e}")

    def get_trace_attributes(self):
        """
        Get trace attributes for this adapter.

        Returns:
            Dictionary of trace attributes.
        """
        attrs = super().get_trace_attributes()
        attrs["service.namespace"] = "llamaindex_agentserver"
        return attrs

    def get_agent_identifier(self) -> str:
        """
        Get the agent identifier for tracing.

        Returns:
            The agent identifier string.
        """
        agent_name = os.getenv(Constants.AGENT_NAME)
        if agent_name:
            return agent_name
        agent_id = os.getenv(Constants.AGENT_ID)
        if agent_id:
            return agent_id
        return "HostedAgent-LlamaIndexWorkflow"
