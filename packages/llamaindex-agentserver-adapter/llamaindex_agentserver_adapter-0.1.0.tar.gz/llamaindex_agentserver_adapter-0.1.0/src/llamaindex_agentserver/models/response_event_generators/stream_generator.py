"""Root-level response stream event generator."""

import time
from typing import Any, List

from azure.ai.agentserver.core.models import projects as project_models
from azure.ai.agentserver.core.server.common.agent_run_context import AgentRunContext

from .base import ResponseEventGenerator, StreamEventState
from .output_item_generator import ResponseOutputItemEventGenerator


class ResponseStreamEventGenerator(ResponseEventGenerator):
    """Root-level response stream event generator."""

    def __init__(self, logger, parent):
        super().__init__(logger, parent)
        self.aggregated_contents: List[project_models.ItemResource] = []
        self.output_index = 0

    def on_start(
        self, context: AgentRunContext, stream_state: StreamEventState
    ) -> tuple[bool, List[project_models.ResponseStreamEvent]]:
        """Generate response created and in_progress events."""
        if self.started:
            return True, []

        agent_id = context.get_agent_id_object()
        conversation = context.get_conversation_object()

        response_dict = {
            "object": "response",
            "agent_id": agent_id,
            "conversation": conversation,
            "id": context.response_id,
            "status": "in_progress",
            "created_at": int(time.time()),
        }
        created_event = project_models.ResponseCreatedEvent(
            response=project_models.Response(response_dict),
            sequence_number=stream_state.sequence_number,
        )
        stream_state.sequence_number += 1

        response_dict = {
            "object": "response",
            "agent_id": agent_id,
            "conversation": conversation,
            "id": context.response_id,
            "status": "in_progress",
            "created_at": int(time.time()),
        }
        in_progress_event = project_models.ResponseInProgressEvent(
            response=project_models.Response(response_dict),
            sequence_number=stream_state.sequence_number,
        )
        stream_state.sequence_number += 1

        self.started = True
        return True, [created_event, in_progress_event]

    def should_end(self, event: Any) -> bool:
        """Determine if the event indicates end of the stream."""
        if event is None:
            return True
        if hasattr(event, "__class__") and event.__class__.__name__ == "StopEvent":
            return True
        return False

    def try_process_event(
        self, event: Any, context: AgentRunContext, stream_state: StreamEventState
    ) -> tuple[bool, ResponseEventGenerator, List[project_models.ResponseStreamEvent]]:
        """Process incoming workflow event."""
        is_processed = False
        next_processor = self
        events = []

        if not self.started:
            self.started, start_events = self.on_start(context, stream_state)
            events.extend(start_events)

        if event is not None and not self.should_end(event):
            next_processor = ResponseOutputItemEventGenerator(
                self.logger,
                self,
                self.output_index,
                getattr(event, "id", None) or str(id(event))
            )
            self.output_index += 1
            return is_processed, next_processor, events

        if self.should_end(event):
            done_events = self.on_end(event, context, stream_state)
            events.extend(done_events)
            is_processed = True
            next_processor = None

        return is_processed, next_processor, events

    def on_end(
        self, event: Any, context: AgentRunContext, stream_state: StreamEventState
    ) -> List[project_models.ResponseStreamEvent]:
        """Generate response completed event."""
        agent_id = context.get_agent_id_object()
        conversation = context.get_conversation_object()

        response_dict = {
            "object": "response",
            "agent_id": agent_id,
            "conversation": conversation,
            "id": context.response_id,
            "status": "completed",
            "created_at": int(time.time()),
            "output": self.aggregated_contents,
        }
        done_event = project_models.ResponseCompletedEvent(
            response=project_models.Response(response_dict),
            sequence_number=stream_state.sequence_number,
        )
        stream_state.sequence_number += 1

        if self.parent:
            self.parent.aggregate_content(self.aggregated_contents)

        return [done_event]

    def aggregate_content(self, content):
        """Aggregate content from child generators."""
        if isinstance(content, list):
            for c in content:
                self.aggregate_content(c)
        elif isinstance(content, project_models.ItemResource):
            self.aggregated_contents.append(content)
        else:
            raise ValueError(f"Invalid content type: {type(content)}")
