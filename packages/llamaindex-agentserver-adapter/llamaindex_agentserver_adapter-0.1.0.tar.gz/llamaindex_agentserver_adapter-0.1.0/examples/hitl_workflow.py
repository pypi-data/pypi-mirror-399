"""Human-in-the-loop LlamaIndex Workflow example for Azure AI Agent Server.

This example demonstrates a workflow that requires human approval before
completing an action, using InputRequiredEvent and HumanResponseEvent.

To run this example:
1. Install dependencies: pip install llamaindex-agentserver-adapter[openai]
2. Set environment variable: export OPENAI_API_KEY=your-key
3. Run: python hitl_workflow.py
"""

import os
from typing import Annotated

from llama_index.core.llms import LLM
from llama_index.llms.openai import OpenAI
from workflows import Context, Workflow, step
from workflows.events import Event, HumanResponseEvent, InputRequiredEvent, StartEvent, StopEvent
from workflows.resource import Resource

from llamaindex_agentserver import from_workflow


def get_llm(*args, **kwargs) -> LLM:
    """Factory function to create the LLM instance."""
    return OpenAI(
        model=os.environ.get("OPENAI_MODEL", "gpt-4o-mini"),
        api_key=os.environ.get("OPENAI_API_KEY"),
    )


class ProposalEvent(Event):
    """Event containing a proposed action for human approval."""
    proposal: str
    action_type: str


class ApprovedEvent(Event):
    """Event indicating the action was approved."""
    proposal: str
    action_type: str


class HumanApprovalWorkflow(Workflow):
    """
    A workflow that generates proposals and requires human approval.

    This demonstrates the human-in-the-loop pattern where:
    1. An LLM generates a proposal based on user input
    2. The proposal is presented to the user for approval
    3. If approved, the action is executed
    4. If rejected, the workflow ends with a rejection message
    """

    @step
    async def generate_proposal(
        self,
        ev: StartEvent,
        ctx: Context,
        llm: Annotated[LLM, Resource(get_llm)],
    ) -> ProposalEvent:
        """Generate a proposal based on user input."""
        user_input = ev.input if hasattr(ev, "input") else str(ev)

        prompt = f"""Based on the following user request, generate a detailed proposal for an action to take.
Be specific about what will be done.

User Request: {user_input}

Generate a proposal in the following format:
Action Type: [type of action]
Proposal: [detailed description of what will be done]"""

        response = await llm.acomplete(prompt)
        response_text = str(response)

        lines = response_text.strip().split("\n")
        action_type = "general"
        proposal = response_text

        for line in lines:
            if line.startswith("Action Type:"):
                action_type = line.replace("Action Type:", "").strip()
            elif line.startswith("Proposal:"):
                proposal = line.replace("Proposal:", "").strip()

        return ProposalEvent(proposal=proposal, action_type=action_type)

    @step
    async def request_approval(
        self,
        ev: ProposalEvent,
        ctx: Context,
    ) -> InputRequiredEvent:
        """Request human approval for the proposal."""
        async with ctx.store.edit_state() as state:
            state.proposal = ev.proposal
            state.action_type = ev.action_type

        approval_message = f"""
Please review the following proposal:

Action Type: {ev.action_type}
Proposal: {ev.proposal}

Do you approve this action? (yes/no)
"""
        return InputRequiredEvent(prefix=approval_message)

    @step
    async def process_response(
        self,
        ev: HumanResponseEvent,
        ctx: Context,
    ) -> ApprovedEvent | StopEvent:
        """Process the human response."""
        response = ev.response.lower().strip()
        state = await ctx.store.get_state()

        if response in ("yes", "y", "approve", "approved"):
            return ApprovedEvent(
                proposal=state.proposal,
                action_type=state.action_type,
            )
        else:
            return StopEvent(
                result=f"Action rejected by user. Original proposal: {state.proposal}"
            )

    @step
    async def execute_action(
        self,
        ev: ApprovedEvent,
        ctx: Context,
        llm: Annotated[LLM, Resource(get_llm)],
    ) -> StopEvent:
        """Execute the approved action."""
        prompt = f"""The following action has been approved and executed:

Action Type: {ev.action_type}
Proposal: {ev.proposal}

Generate a confirmation message summarizing what was done."""

        response = await llm.acomplete(prompt)

        return StopEvent(result=str(response))


def main():
    """Run the workflow as an Azure AI hosted agent."""
    workflow = HumanApprovalWorkflow(timeout=300, verbose=True)
    adapter = from_workflow(workflow)

    print("Starting HITL workflow server on http://localhost:8088")
    print("This workflow requires streaming to handle the approval flow.")

    adapter.run(port=8088)


if __name__ == "__main__":
    main()
