"""Stream response converter for LlamaIndex Workflows.

Converts workflow event streams to OpenAI-style response stream events.
"""

import logging
from typing import Any, AsyncIterator, List

from azure.ai.agentserver.core.models import ResponseStreamEvent
from azure.ai.agentserver.core.server.common.agent_run_context import AgentRunContext

from .response_event_generators import (
    ResponseEventGenerator,
    ResponseStreamEventGenerator,
    StreamEventState,
)

logger = logging.getLogger(__name__)


class LlamaIndexWorkflowStreamResponseConverter:
    """
    Converts LlamaIndex Workflow event streams to response stream events.

    Handles various workflow event types:
    - StopEvent: Final result event, ends the stream
    - Custom Event subclasses: Intermediate workflow events
    - InputRequiredEvent: Human-in-the-loop events
    """

    def __init__(self, stream: AsyncIterator[Any], context: AgentRunContext):
        self.stream = stream
        self.context = context
        self.stream_state = StreamEventState()
        self.current_generator: ResponseEventGenerator = None

    async def convert(self):
        """
        Convert the workflow event stream to response stream events.

        Yields:
            ResponseStreamEvent objects in the correct order.
        """
        try:
            async for event in self.stream:
                try:
                    if self.current_generator is None:
                        self.current_generator = ResponseStreamEventGenerator(logger, None)

                    if self._should_skip_event(event):
                        continue

                    converted = self._try_process_event(event, self.context)
                    for response_event in converted:
                        yield response_event
                except Exception as e:
                    logger.error(f"Error converting event {type(event).__name__}: {e}")
                    raise ValueError(f"Error converting event {type(event).__name__}") from e

        except StopAsyncIteration:
            pass

        logger.info("Stream ended, finalizing response.")
        converted = self._try_process_event(None, self.context)
        for response_event in converted:
            yield response_event

    def _should_skip_event(self, event: Any) -> bool:
        """Check if the event should be skipped."""
        if event is None:
            return False

        event_type = type(event).__name__

        if event_type == "StartEvent":
            return True

        if event_type in ("Event",):
            if not self._has_content(event):
                return True

        return False

    def _has_content(self, event: Any) -> bool:
        """Check if an event has meaningful content to output."""
        for attr in ("content", "text", "result", "message", "data", "output"):
            if hasattr(event, attr):
                value = getattr(event, attr)
                if value is not None and value != "":
                    return True
        return False

    def _try_process_event(
        self, event: Any, context: AgentRunContext
    ) -> List[ResponseStreamEvent]:
        """Try to process an event through the generator hierarchy."""
        if event is not None and not self.current_generator:
            self.current_generator = ResponseStreamEventGenerator(logger, None)

        is_processed = False
        next_processor = self.current_generator
        returned_events = []

        while not is_processed and next_processor is not None:
            is_processed, next_processor, processed_events = self.current_generator.try_process_event(
                event, context, self.stream_state
            )
            returned_events.extend(processed_events)

            if not is_processed and next_processor == self.current_generator:
                logger.warning(
                    f"Event cannot be processed by current generator "
                    f"{type(self.current_generator).__name__}: {type(event).__name__ if event else 'None'}"
                )
                break

            if next_processor != self.current_generator:
                logger.debug(
                    f"Switching processor from {type(self.current_generator).__name__} "
                    f"to {type(next_processor).__name__ if next_processor else 'None'}"
                )
                self.current_generator = next_processor

        return returned_events
