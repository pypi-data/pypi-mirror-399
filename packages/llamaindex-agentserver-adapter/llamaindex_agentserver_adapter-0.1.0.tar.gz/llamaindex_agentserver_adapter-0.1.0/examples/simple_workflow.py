"""Simple LlamaIndex Workflow example for Azure AI Agent Server.

This example demonstrates a basic workflow that uses an LLM to process
user input and generate a response.

To run this example:
1. Install dependencies: pip install llamaindex-agentserver-adapter[openai]
2. Set environment variable: export OPENAI_API_KEY=your-key
3. Run: python simple_workflow.py
"""

import os
from typing import Annotated

from llama_index.core.llms import LLM
from llama_index.llms.openai import OpenAI
from workflows import Context, Workflow, step
from workflows.events import StartEvent, StopEvent
from workflows.resource import Resource

from llamaindex_agentserver import from_workflow


def get_llm(*args, **kwargs) -> LLM:
    """Factory function to create the LLM instance."""
    return OpenAI(
        model=os.environ.get("OPENAI_MODEL", "gpt-4o-mini"),
        api_key=os.environ.get("OPENAI_API_KEY"),
    )


class SimpleChatWorkflow(Workflow):
    """A simple chat workflow that responds to user input using an LLM."""

    @step
    async def process_input(
        self,
        ev: StartEvent,
        ctx: Context,
        llm: Annotated[LLM, Resource(get_llm)],
    ) -> StopEvent:
        """Process the user input and generate a response."""
        user_input = ev.input if hasattr(ev, "input") else str(ev)

        instructions = getattr(ev, "instructions", None)
        if instructions:
            system_prompt = instructions
        else:
            system_prompt = "You are a helpful AI assistant. Respond to the user's message."

        prompt = f"System: {system_prompt}\n\nUser: {user_input}\n\nAssistant:"
        response = await llm.acomplete(prompt)

        return StopEvent(result=str(response))


def main():
    """Run the workflow as an Azure AI hosted agent."""
    workflow = SimpleChatWorkflow(timeout=60, verbose=True)
    adapter = from_workflow(workflow)

    print("Starting server on http://localhost:8088")
    print("Test with: curl -X POST http://localhost:8088/runs -H 'Content-Type: application/json' -d '{\"input\": \"Hello!\"}'")

    adapter.run(port=8088)


if __name__ == "__main__":
    main()
