"""RAG agent example demonstrating retrieval-augmented generation.

Run with:
    python -m miu_examples.rag_agent

Requires:
    pip install miu-examples[rag]
    ANTHROPIC_API_KEY environment variable
    Qdrant server running (optional - uses in-memory by default)

This example demonstrates:
    1. Indexing documents into a vector store
    2. Retrieving relevant context for queries
    3. Using retrieved context to answer questions
"""

import asyncio
from typing import Any

from pydantic import BaseModel, Field

from miu_core.agents import AgentConfig, ReActAgent
from miu_core.providers import create_provider
from miu_core.tools import Tool, ToolContext, ToolRegistry, ToolResult

# Sample documents to index
DOCUMENTS = [
    {
        "id": "doc1",
        "title": "miu Framework Overview",
        "content": "miu is an AI agent framework built in Python. "
        "It supports multiple LLM providers including Anthropic, OpenAI, and Google. "
        "The framework uses a ReAct pattern for agent reasoning.",
    },
    {
        "id": "doc2",
        "title": "miu Tools System",
        "content": "miu provides a tool system that allows agents to perform actions. "
        "Tools are defined using Pydantic models for input validation. "
        "The framework supports both synchronous and asynchronous tool execution.",
    },
    {
        "id": "doc3",
        "title": "miu MCP Integration",
        "content": "miu supports the Model Context Protocol (MCP) for connecting to external tools. "
        "MCP servers can be started using stdio transport. "
        "The client automatically handles JSON-RPC communication.",
    },
]


class SearchInput(BaseModel):
    """Input for document search."""

    query: str = Field(description="Search query to find relevant documents")


class DocumentSearchTool(Tool):
    """Simple document search tool (mock vector search)."""

    name = "search_documents"
    description = "Search the document database for relevant information."

    def __init__(self, documents: list[dict[str, str]]) -> None:
        """Initialize with documents."""
        self.documents = documents

    def get_input_schema(self) -> type[BaseModel]:
        """Return input schema."""
        return SearchInput

    async def execute(self, ctx: ToolContext, **kwargs: Any) -> ToolResult:
        """Search documents (simple keyword matching for demo)."""
        query = kwargs.get("query", "").lower()

        # Simple keyword matching (production would use vector similarity)
        results = []
        for doc in self.documents:
            content = doc["content"].lower()
            title = doc["title"].lower()

            # Score based on keyword matches
            query_words = query.split()
            matches = sum(1 for word in query_words if word in content or word in title)

            if matches > 0:
                results.append((matches, doc))

        # Sort by relevance and take top 2
        results.sort(key=lambda x: x[0], reverse=True)
        top_results = results[:2]

        if not top_results:
            return ToolResult(output="No relevant documents found.")

        # Format results
        output_parts = ["Relevant documents found:\n"]
        for _, doc in top_results:
            output_parts.append(f"**{doc['title']}**\n{doc['content']}\n")

        return ToolResult(output="\n".join(output_parts))


async def main() -> None:
    """Run RAG agent example."""
    print("RAG Agent Example")
    print("=" * 40)

    # Create provider
    provider = create_provider("anthropic:claude-sonnet-4-20250514")

    # Create tool registry with document search
    registry = ToolRegistry()
    registry.register(DocumentSearchTool(DOCUMENTS))

    # Create RAG agent
    agent = ReActAgent(
        provider=provider,
        tools=registry,
        config=AgentConfig(
            name="rag-agent",
            system_prompt=(
                "You are a helpful assistant with access to a document database. "
                "When answering questions, search the documents first to find relevant information. "
                "Base your answers on the retrieved documents."
            ),
        ),
    )

    # Example queries
    queries = [
        "What LLM providers does miu support?",
        "How do tools work in miu?",
        "What is MCP and how does miu use it?",
    ]

    for query in queries:
        print(f"\nQuery: {query}")
        response = await agent.run(query)
        print(f"Answer: {response.get_text()}")
        print("-" * 40)


if __name__ == "__main__":
    asyncio.run(main())
