# miu-examples

Example applications demonstrating miu-core capabilities.

## Installation

```bash
# Basic installation
uv add miu-examples

# With RAG support (includes qdrant-client)
uv add "miu-examples[rag]"
```

## Examples

### 1. Simple Agent (`simple_agent.py`)

Basic agent usage with a single LLM query.

```bash
export ANTHROPIC_API_KEY="your-key"
python -m miu_examples.simple_agent
```

### 2. Multi-Provider (`multi_provider.py`)

Compare responses from different LLM providers.

```bash
export ANTHROPIC_API_KEY="your-key"
export OPENAI_API_KEY="your-key"      # optional
export GOOGLE_API_KEY="your-key"      # optional
python -m miu_examples.multi_provider
```

### 3. Custom Tools (`tool_usage.py`)

Create and use custom tools with agents.

```bash
python -m miu_examples.tool_usage
```

### 4. MCP Integration (`mcp_client.py`)

Connect to MCP servers for external tool access.

```bash
# Requires npx and MCP server
python -m miu_examples.mcp_client
```

### 5. RAG Agent (`rag_agent.py`)

Retrieval-augmented generation with document search.

```bash
python -m miu_examples.rag_agent
```

### 6. Multi-Agent (`multi_agent.py`)

Orchestrate multiple specialized agents.

```bash
python -m miu_examples.multi_agent
```

## Requirements

- Python 3.11+
- miu-core with provider dependencies
- API keys for chosen providers

## License

MIT
