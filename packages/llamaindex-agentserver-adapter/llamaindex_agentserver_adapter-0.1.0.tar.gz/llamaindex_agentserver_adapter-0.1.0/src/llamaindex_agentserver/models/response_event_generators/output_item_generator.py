"""Output item level event generator."""

from typing import Any, List

from azure.ai.agentserver.core.models import projects as project_models
from azure.ai.agentserver.core.server.common.agent_run_context import AgentRunContext

from .base import ResponseEventGenerator, StreamEventState


class ResponseOutputItemEventGenerator(ResponseEventGenerator):
    """Output item level event generator."""

    def __init__(self, logger, parent, output_index: int, event_id: str):
        super().__init__(logger, parent)
        self.output_index = output_index
        self.event_id = event_id
        self.content_parts: List[project_models.ItemContent] = []
        self.accumulated_text = ""
        self.item_resource = None

    def on_start(
        self, context: AgentRunContext, stream_state: StreamEventState
    ) -> tuple[bool, List[project_models.ResponseStreamEvent]]:
        """Generate output item added event."""
        if self.started:
            return True, []

        self.item_resource = project_models.ResponsesAssistantMessageItemResource(
            content=[],
            id=context.id_generator.generate_message_id(),
            status="in_progress",
        )

        added_event = project_models.ResponseOutputItemAddedEvent(
            item=self.item_resource,
            output_index=self.output_index,
            sequence_number=stream_state.sequence_number,
        )
        stream_state.sequence_number += 1

        self.started = True
        return True, [added_event]

    def try_process_event(
        self, event: Any, context: AgentRunContext, stream_state: StreamEventState
    ) -> tuple[bool, ResponseEventGenerator, List[project_models.ResponseStreamEvent]]:
        """Process event and generate streaming events."""
        events = []

        if not self.started:
            self.started, start_events = self.on_start(context, stream_state)
            events.extend(start_events)

        content = self._extract_content(event)

        if content:
            delta_events = self._create_text_delta_events(content, context, stream_state)
            events.extend(delta_events)

        done_events = self.on_end(event, context, stream_state)
        events.extend(done_events)

        return True, self.parent, events

    def _extract_content(self, event: Any) -> str:
        """Extract text content from workflow event."""
        if event is None:
            return ""

        if hasattr(event, "content"):
            content = event.content
            if isinstance(content, str):
                return content
            elif hasattr(content, "text"):
                return content.text

        if hasattr(event, "text"):
            return event.text

        if hasattr(event, "result"):
            result = event.result
            if isinstance(result, str):
                return result
            elif isinstance(result, dict):
                return result.get("text", result.get("content", str(result)))

        if hasattr(event, "delta"):
            delta = event.delta
            if isinstance(delta, str):
                return delta
            elif hasattr(delta, "text"):
                return delta.text

        if hasattr(event, "message"):
            msg = event.message
            if isinstance(msg, str):
                return msg
            elif hasattr(msg, "content"):
                return msg.content if isinstance(msg.content, str) else str(msg.content)

        return ""

    def _create_text_delta_events(
        self, text: str, context: AgentRunContext, stream_state: StreamEventState
    ) -> List[project_models.ResponseStreamEvent]:
        """Create text delta streaming events."""
        events = []

        if not text:
            return events

        if not self.content_parts:
            content_part = project_models.ItemContent({
                "type": project_models.ItemContentType.OUTPUT_TEXT,
                "text": "",
                "annotations": [],
            })
            self.content_parts.append(content_part)

            part_added_event = project_models.ResponseContentPartAddedEvent(
                content_index=0,
                item_id=self.item_resource.id if self.item_resource else "",
                output_index=self.output_index,
                part=content_part,
                sequence_number=stream_state.sequence_number,
            )
            stream_state.sequence_number += 1
            events.append(part_added_event)

        delta_event = project_models.ResponseTextDeltaEvent(
            content_index=0,
            delta=text,
            item_id=self.item_resource.id if self.item_resource else "",
            output_index=self.output_index,
            sequence_number=stream_state.sequence_number,
        )
        stream_state.sequence_number += 1
        events.append(delta_event)

        self.accumulated_text += text

        return events

    def on_end(
        self, event: Any, context: AgentRunContext, stream_state: StreamEventState
    ) -> List[project_models.ResponseStreamEvent]:
        """Generate output item done event."""
        events = []

        if self.accumulated_text and self.content_parts:
            self.content_parts[0] = project_models.ItemContent({
                "type": project_models.ItemContentType.OUTPUT_TEXT,
                "text": self.accumulated_text,
                "annotations": [],
            })

            text_done_event = project_models.ResponseTextDoneEvent(
                content_index=0,
                item_id=self.item_resource.id if self.item_resource else "",
                output_index=self.output_index,
                text=self.accumulated_text,
                sequence_number=stream_state.sequence_number,
            )
            stream_state.sequence_number += 1
            events.append(text_done_event)

            part_done_event = project_models.ResponseContentPartDoneEvent(
                content_index=0,
                item_id=self.item_resource.id if self.item_resource else "",
                output_index=self.output_index,
                part=self.content_parts[0],
                sequence_number=stream_state.sequence_number,
            )
            stream_state.sequence_number += 1
            events.append(part_done_event)

        if self.item_resource:
            final_item = project_models.ResponsesAssistantMessageItemResource(
                content=self.content_parts if self.content_parts else [],
                id=self.item_resource.id,
                status="completed",
            )

            done_event = project_models.ResponseOutputItemDoneEvent(
                item=final_item,
                output_index=self.output_index,
                sequence_number=stream_state.sequence_number,
            )
            stream_state.sequence_number += 1
            events.append(done_event)

            if self.parent:
                self.parent.aggregate_content(final_item)

        return events
