"""Simple agent example demonstrating basic miu-core usage.

Run with:
    python -m miu_examples.simple_agent

Requires:
    ANTHROPIC_API_KEY environment variable
"""

import asyncio

from miu_core.agents import AgentConfig, ReActAgent
from miu_core.providers import create_provider


async def main() -> None:
    """Run a simple agent query."""
    # Create provider - uses ANTHROPIC_API_KEY from environment
    provider = create_provider("anthropic:claude-sonnet-4-20250514")

    # Create agent with custom config
    agent = ReActAgent(
        provider=provider,
        config=AgentConfig(
            name="simple-agent",
            system_prompt="You are a helpful assistant. Be concise.",
            max_iterations=5,
        ),
    )

    # Run query
    print("Query: What is the capital of France?")
    response = await agent.run("What is the capital of France?")
    print(f"Response: {response.get_text()}")


if __name__ == "__main__":
    asyncio.run(main())
