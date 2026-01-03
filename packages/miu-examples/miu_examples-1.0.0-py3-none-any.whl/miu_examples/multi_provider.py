"""Multi-provider example demonstrating provider switching.

Run with:
    python -m miu_examples.multi_provider

Requires (at least one):
    ANTHROPIC_API_KEY
    OPENAI_API_KEY
    GOOGLE_API_KEY
"""

import asyncio
import os

from miu_core.agents import AgentConfig, ReActAgent
from miu_core.providers import create_provider

# Provider configurations with their specs
PROVIDERS = [
    ("anthropic:claude-sonnet-4-20250514", "ANTHROPIC_API_KEY"),
    ("openai:gpt-4o", "OPENAI_API_KEY"),
    ("google:gemini-2.0-flash", "GOOGLE_API_KEY"),
]


async def run_with_provider(provider_spec: str, query: str) -> str | None:
    """Run query with specified provider."""
    try:
        provider = create_provider(provider_spec)
        agent = ReActAgent(
            provider=provider,
            config=AgentConfig(
                name=f"{provider_spec.split(':')[0]}-agent",
                system_prompt="You are a helpful assistant. Be concise (1-2 sentences).",
            ),
        )
        response = await agent.run(query)
        return response.get_text()
    except Exception as e:
        return f"Error: {e}"


async def main() -> None:
    """Compare responses from multiple providers."""
    query = "What is the speed of light?"
    print(f"Query: {query}\n")

    for spec, env_var in PROVIDERS:
        provider_name = spec.split(":")[0]

        if not os.environ.get(env_var):
            print(f"[{provider_name}] Skipped - {env_var} not set")
            continue

        print(f"[{provider_name}] Running...")
        response = await run_with_provider(spec, query)
        print(f"[{provider_name}] {response}\n")


if __name__ == "__main__":
    asyncio.run(main())
