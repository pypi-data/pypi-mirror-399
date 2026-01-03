"""LlamaIndex Workflows adapter for Azure AI Agent Server.

This package provides an adapter for hosting LlamaIndex Workflows as Azure AI
Agent Server endpoints, enabling seamless integration with Azure AI infrastructure.

Example:
    from workflows import Workflow, step
    from workflows.events import StartEvent, StopEvent
    from llamaindex_agentserver import from_workflow

    class MyWorkflow(Workflow):
        @step
        async def process(self, ev: StartEvent) -> StopEvent:
            return StopEvent(result=f"Processed: {ev.input}")

    workflow = MyWorkflow(timeout=60)
    adapter = from_workflow(workflow)
    adapter.run(port=8088)
"""

from typing import TYPE_CHECKING, Optional

__version__ = "0.1.0"

if TYPE_CHECKING:
    from .models import LlamaIndexWorkflowStateConverter


def from_workflow(
    workflow,
    state_converter: Optional["LlamaIndexWorkflowStateConverter"] = None,
    timeout: Optional[float] = None,
):
    """
    Create a LlamaIndexWorkflowAdapter from a LlamaIndex Workflow.

    This is the main entry point for adapting LlamaIndex Workflows to run as
    Azure AI Agent Server endpoints.

    Args:
        workflow: The LlamaIndex Workflow instance to adapt.
        state_converter: Optional custom state converter for non-standard workflows.
            If not provided, uses the default converter which handles standard
            input/output formats.
        timeout: Optional timeout override for workflow execution in seconds.

    Returns:
        A LlamaIndexWorkflowAdapter instance that can be run as a server.

    Example:
        >>> from workflows import Workflow, step
        >>> from workflows.events import StartEvent, StopEvent
        >>> from llamaindex_agentserver import from_workflow
        >>>
        >>> class MyWorkflow(Workflow):
        ...     @step
        ...     async def process(self, ev: StartEvent) -> StopEvent:
        ...         return StopEvent(result=f"Hello, {ev.input}!")
        >>>
        >>> adapter = from_workflow(MyWorkflow())
        >>> adapter.run(port=8088)  # Starts server on http://localhost:8088
    """
    from .adapter import LlamaIndexWorkflowAdapter

    return LlamaIndexWorkflowAdapter(workflow, state_converter=state_converter, timeout=timeout)


# Convenience alias
from_llamaindex_workflow = from_workflow

__all__ = [
    "from_workflow",
    "from_llamaindex_workflow",
    "__version__",
]
