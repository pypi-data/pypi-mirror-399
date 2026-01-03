"""Base classes for response event generation in streaming mode."""

from typing import Any, List

from azure.ai.agentserver.core.models import projects as project_models
from azure.ai.agentserver.core.server.common.agent_run_context import AgentRunContext


class StreamEventState:
    """State information for the stream event processing."""

    sequence_number: int = 0


class ResponseEventGenerator:
    """Abstract base class for response event generators."""

    started: bool = False

    def __init__(self, logger, parent):
        self.logger = logger
        self.parent = parent

    def try_process_event(
        self,
        event: Any,
        context: AgentRunContext,
        stream_state: StreamEventState
    ):
        """
        Try to process the incoming workflow event.

        Args:
            event: The incoming workflow event to process.
            context: The agent run context.
            stream_state: The current stream event state.

        Returns:
            tuple of (is_processed, next_processor, events)
        """
        pass

    def on_start(self) -> tuple[bool, List[project_models.ResponseStreamEvent]]:
        """Generate the starting events for this layer."""
        return False, []

    def on_end(
        self, event: Any, context: AgentRunContext, stream_state: StreamEventState
    ) -> tuple[bool, List[project_models.ResponseStreamEvent]]:
        """Generate the ending events for this layer."""
        return False, []

    def aggregate_content(self, content: Any):
        """Aggregate content from child processors."""
        pass
