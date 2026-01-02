"""Multi-agent example demonstrating orchestration patterns.

Run with:
    python -m miu_examples.multi_agent

Requires:
    ANTHROPIC_API_KEY environment variable

This example demonstrates:
    1. Orchestrator pattern - coordinating agents with dependencies
    2. Pipeline pattern - sequential agent processing
    3. Router pattern - routing requests to specialized agents
"""

import asyncio
from typing import Any

from pydantic import BaseModel, Field

from miu_core.agents import AgentConfig, ReActAgent
from miu_core.patterns import Orchestrator, Pipeline, Router
from miu_core.providers import create_provider
from miu_core.tools import Tool, ToolContext, ToolRegistry, ToolResult

# ============================================================================
# Mock Tools for Examples
# ============================================================================


class ResearchInput(BaseModel):
    """Input for research agent."""

    topic: str = Field(description="Topic to research")


class WriteInput(BaseModel):
    """Input for writer agent."""

    topic: str = Field(description="Topic to write about")
    context: str = Field(description="Research context to use")


class ResearchTool(Tool):
    """Mock research tool that simulates gathering information."""

    name = "research"
    description = "Research a topic and gather relevant information."

    def get_input_schema(self) -> type[BaseModel]:
        """Return input schema."""
        return ResearchInput

    async def execute(self, ctx: ToolContext, **kwargs: Any) -> ToolResult:
        """Simulate research (mock implementation)."""
        topic = kwargs.get("topic", "")

        research_data = {
            "ai": "AI is transforming industries. Key trends: LLMs, agents, multimodal.",
            "python": "Python is popular for ML/AI. Key libraries: PyTorch, TensorFlow.",
            "agents": "AI agents use LLMs for reasoning. Patterns: ReAct, tool use.",
            "code": "Modern software: microservices, containers, CI/CD, cloud-native.",
        }

        topic_lower = topic.lower()
        for key, data in research_data.items():
            if key in topic_lower:
                return ToolResult(output=f"Research findings: {data}")

        return ToolResult(output=f"Research on '{topic}': General information gathered.")


class WriterTool(Tool):
    """Mock writer tool that generates content."""

    name = "write_article"
    description = "Write an article based on research."

    def get_input_schema(self) -> type[BaseModel]:
        """Return input schema."""
        return WriteInput

    async def execute(self, ctx: ToolContext, **kwargs: Any) -> ToolResult:
        """Generate article (mock implementation)."""
        topic = kwargs.get("topic", "Unknown")
        context = kwargs.get("context", "")

        article = f"""# {topic.title()}

{context[:200]}

## Summary
An overview of {topic} and its applications."""
        return ToolResult(output=article.strip())


# ============================================================================
# Agent Creation Helpers
# ============================================================================


def create_agent(name: str, system_prompt: str, tool: Tool | None = None) -> ReActAgent:
    """Create an agent with optional tool."""
    provider = create_provider("anthropic:claude-sonnet-4-20250514")
    registry = ToolRegistry()
    if tool:
        registry.register(tool)

    return ReActAgent(
        provider=provider,
        tools=registry,
        config=AgentConfig(name=name, system_prompt=system_prompt, max_iterations=3),
    )


# ============================================================================
# Orchestrator Example
# ============================================================================


async def demo_orchestrator() -> None:
    """Demonstrate Orchestrator pattern with task dependencies."""
    print("\n" + "=" * 50)
    print("ORCHESTRATOR PATTERN")
    print("=" * 50)

    orchestrator = Orchestrator()

    # Add agents
    orchestrator.add_agent(
        "researcher",
        create_agent(
            "researcher",
            "You are a research specialist. Use the research tool.",
            ResearchTool(),
        ),
    )
    orchestrator.add_agent(
        "writer",
        create_agent(
            "writer",
            "You are a content writer. Use the write_article tool.",
            WriterTool(),
        ),
    )

    # Add tasks with dependencies
    orchestrator.add_task("research", "researcher", "Research the topic: AI Agents")
    orchestrator.add_task(
        "write",
        "writer",
        lambda ctx: f"Write article about AI Agents using: {ctx['research'].response.get_text()[:100] if ctx['research'].response else 'no context'}",
        depends_on=["research"],
    )

    print("Running orchestrator with dependency: research -> write")
    results = await orchestrator.run()

    for name, result in results.items():
        status = "SUCCESS" if result.success else f"FAILED: {result.error}"
        print(f"  [{name}] {status}")
        if result.response:
            print(f"    Output: {result.response.get_text()[:100]}...")


# ============================================================================
# Pipeline Example
# ============================================================================


async def demo_pipeline() -> None:
    """Demonstrate Pipeline pattern with sequential processing."""
    print("\n" + "=" * 50)
    print("PIPELINE PATTERN")
    print("=" * 50)

    pipeline = Pipeline()

    # Create pipeline stages
    pipeline.add_stage(
        "research",
        create_agent("researcher", "Research the given topic briefly.", ResearchTool()),
    )
    pipeline.add_stage(
        "summarize",
        create_agent("summarizer", "Summarize the given text in 2 sentences."),
        transform=lambda q, r: f"Summarize this research: {r.get_text()[:200]}",
    )

    print(f"Pipeline stages: {pipeline.stages}")
    print("Running pipeline: research -> summarize")

    result = await pipeline.run("Research Python programming")

    print(f"  Completed stages: {result.stages_completed}/{len(pipeline)}")
    print(f"  Success: {result.success}")
    if result.final_response:
        print(f"  Final output: {result.final_response.get_text()[:150]}...")


# ============================================================================
# Router Example
# ============================================================================


async def demo_router() -> None:
    """Demonstrate Router pattern with keyword-based routing."""
    print("\n" + "=" * 50)
    print("ROUTER PATTERN")
    print("=" * 50)

    router = Router()

    # Add routes with keyword matching
    router.add_route(
        "code",
        create_agent("coder", "You help with coding questions. Be concise."),
        keywords=["code", "programming", "debug", "python", "function"],
        priority=10,
    )
    router.add_route(
        "writing",
        create_agent("writer", "You help with writing. Be concise."),
        keywords=["write", "essay", "article", "blog"],
        priority=10,
    )
    router.add_route(
        "general",
        create_agent("assistant", "You are a helpful assistant. Be concise."),
        condition=lambda q: True,  # Catch-all
        priority=0,
    )

    print(f"Available routes: {router.routes}")

    # Test different queries
    queries = [
        "Help me debug this Python function",
        "Write a short blog intro",
        "What is the weather today?",
    ]

    for query in queries:
        expected = router.get_route(query)
        print(f"\nQuery: '{query}'")
        print(f"  Expected route: {expected}")

        result = await router.route(query)
        print(f"  Actual route: {result.agent_name}")
        print(f"  Response: {result.response.get_text()[:100]}...")


# ============================================================================
# Main
# ============================================================================


async def main() -> None:
    """Run all pattern demonstrations."""
    print("Multi-Agent Pattern Examples")
    print("=" * 50)
    print("\nThis example demonstrates three patterns:")
    print("1. Orchestrator - coordinate agents with dependencies")
    print("2. Pipeline - sequential agent processing chain")
    print("3. Router - route requests to specialized agents")

    await demo_orchestrator()
    await demo_pipeline()
    await demo_router()

    print("\n" + "=" * 50)
    print("All patterns demonstrated!")


if __name__ == "__main__":
    asyncio.run(main())
