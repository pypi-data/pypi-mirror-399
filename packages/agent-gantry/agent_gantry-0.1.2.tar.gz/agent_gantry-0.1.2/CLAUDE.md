# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Agent-Gantry is a **Universal Tool Orchestration Platform** for LLM-based agent systems that solves three key problems:

1. **Context Window Tax**: Reduces token costs by ~90% through semantic routing instead of sending all tools in every prompt
2. **Tool/Protocol Fragmentation**: Write Once, Run Anywhere - supports OpenAI, Claude, Gemini, A2A agents, and MCP clients
3. **Operational Blindness**: Zero-trust security with policies, capabilities, and circuit breakers

**Core Philosophy**: *Context is precious. Execution is sacred. Trust is earned.*

## Development Commands

### Environment Setup

```bash
# Preferred: uv for reproducible environments
pip install uv
uv sync --extra dev

# Or use pip directly
pip install -e ".[dev]"

# Install all optional dependencies
pip install -e ".[all]"
```

### Testing

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=agent_gantry

# Run specific test file
pytest tests/test_tool.py

# Run specific test
pytest tests/test_tool.py::TestToolDefinition::test_create_minimal_tool

# Run with verbose output
pytest -v
```

### Code Quality

```bash
# Run linter
ruff check agent_gantry/

# Auto-fix linting issues
ruff check --fix agent_gantry/

# Run type checker (strict mode enabled)
mypy agent_gantry/

# Format code
ruff format agent_gantry/
```

### Building

```bash
# Build package
pip install build
python -m build
```

## Architecture

### Core Components

The architecture follows a layered pattern with clear separation of concerns:

```
┌─────────────────────────────────────────────────────────────────┐
│                        AGENT LAYER                              │
│  (LangChain / AutoGen / LlamaIndex / CrewAI / Custom Agents)    │
└─────────────────────────┬───────────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────────────┐
│                       AGENT-GANTRY                              │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  ┌────────┐ │
│  │  Semantic   │  │  Execution  │  │ Observability│ │ Policy │ │
│  │   Router    │  │   Engine    │  │  / Telemetry │ │ Engine │ │
│  └─────────────┘  └─────────────┘  └─────────────┘  └────────┘ │
└─────────────────────────┬───────────────────────────────────────┘
                          │
          ┌───────────────┼───────────────┬───────────────┐
          ▼               ▼               ▼               ▼
    ┌──────────┐   ┌──────────┐   ┌──────────┐   ┌──────────┐
    │  Python  │   │   MCP    │   │   REST   │   │   A2A    │
    │Functions │   │ Servers  │   │   APIs   │   │  Agents  │
    └──────────┘   └──────────┘   └──────────┘   └──────────┘
```

### Directory Structure

```
agent_gantry/
├── core/                 # Main facade (AgentGantry), registry, router, executor
├── schema/               # Pydantic v2 data models (tools, queries, events, config)
├── adapters/             # Protocol adapters (adapter pattern for extensibility)
│   ├── vector_stores/    # Qdrant, Chroma, In-Memory, LanceDB
│   ├── embedders/        # OpenAI, SentenceTransformers, Nomic, Simple
│   ├── rerankers/        # Cohere, CrossEncoder
│   └── executors/        # Direct, Sandbox, MCP, HTTP, A2A
├── providers/            # Tool import from various sources
├── servers/              # MCP and A2A server implementations
├── integrations/         # Framework wrappers (LangChain, AutoGen, etc.)
├── observability/        # Telemetry, metrics, structured logging
├── metrics/              # Performance metrics
└── cli/                  # Command-line interface
```

## Key Patterns and Principles

### 1. Async-First Design

All core operations are async. Use `async def` and `await` throughout:

```python
async def retrieve_tools(self, query: str) -> list[ToolDefinition]:
    """Async operations are the default."""
    ...
```

### 2. Schema-First with Pydantic v2

Define data models using Pydantic v2 before implementation. All schemas live in `agent_gantry/schema/`:

```python
from pydantic import BaseModel, Field

class ToolDefinition(BaseModel):
    name: str
    description: str
    parameters: dict[str, Any]
    # ... fields defined in schema/tool.py
```

### 3. Adapter Pattern for Extensibility

All external integrations use adapters. This allows swapping implementations without changing core logic:

- **Vector Stores**: `InMemoryVectorStore`, `LanceDBVectorStore`, `QdrantVectorStore`, `ChromaVectorStore`
- **Embedders**: `SimpleEmbedder`, `NomicEmbedder`, `OpenAIEmbedder`
- **Executors**: `DirectExecutor`, `MCPExecutor`, `A2AExecutor`

When adding a new adapter, follow existing patterns in the respective `adapters/` subdirectory.

### 4. Context-Local State with ContextVars

The `set_default_gantry()` function uses `contextvars` for thread-safe and async-safe state management. This provides proper isolation between concurrent operations.

### 5. Semantic Routing Core

The platform's key innovation is semantic tool selection using embeddings + vector search. Tools are embedded and retrieved based on similarity to user queries, dramatically reducing context window usage.

The `@with_semantic_tools` decorator automatically injects relevant tools into LLM function calls.

### 6. Dialect Transcoding

Tools are stored in a canonical format and transcoded to different LLM provider formats:
- `openai` - OpenAI function calling format (also used by Mistral, Groq)
- `anthropic` - Anthropic tool format
- `gemini` - Google Gemini tool format

See `adapters/tool_spec/providers.py` for transcoding logic.

## Common Development Tasks

### Adding a New Vector Store Adapter

1. Create new file in `agent_gantry/adapters/vector_stores/`
2. Implement the `VectorStore` protocol interface
3. Add optional dependency in `pyproject.toml` under `[project.optional-dependencies]`
4. Add tests in `tests/`
5. Update documentation

### Adding a New LLM Provider Dialect

1. Add transcoding logic in `agent_gantry/adapters/tool_spec/providers.py`
2. Update the `with_semantic_tools` decorator to support the new dialect
3. Add tests with the provider's SDK
4. Create example in `examples/llm_integration/`
5. Update `docs/llm_sdk_compatibility.md`

### Modifying Tool Schema

1. Update Pydantic model in `agent_gantry/schema/tool.py`
2. Consider backward compatibility - add migration logic if needed
3. Update all tests that create `ToolDefinition` instances
4. Update documentation and examples

### Adding Framework Integration

1. Create new module in `agent_gantry/integrations/`
2. Follow the pattern of wrapping `AgentGantry` for the framework's API
3. Add integration tests in `tests/`
4. Create comprehensive example in `examples/agent_frameworks/`
5. Update README with usage example

## Testing Requirements

- **Framework**: pytest with `pytest-asyncio` for async tests
- **Fixtures**: Shared fixtures defined in `tests/conftest.py` (e.g., `gantry`, `sample_tools`)
- **Coverage**: Aim for high coverage on core functionality (>80%)
- **Async Tests**: Use `@pytest.mark.asyncio` decorator
- **Test Naming**: `test_<function>_<scenario>_<expected_outcome>`

Example:
```python
import pytest

@pytest.mark.asyncio
async def test_retrieve_tools_returns_relevant_results(gantry, sample_tools):
    """Test that retrieve_tools returns semantically relevant tools."""
    query = "calculate sum of numbers"
    tools = await gantry.retrieve_tools(query, limit=5)
    assert len(tools) > 0
    assert any("sum" in tool.name.lower() for tool in tools)
```

## Code Style

### Type Hints (Strict Mode)

Type hints are **required** everywhere. The project uses strict mypy settings:

```python
from typing import Any

def my_function(param: str) -> dict[str, Any]:
    """Always use type hints."""
    return {"result": param}
```

### Imports

Follow ruff ordering (configured in `pyproject.toml`):

```python
from __future__ import annotations  # For forward references

# Standard library
import asyncio
from typing import Any

# Third-party
from pydantic import BaseModel

# Local
from agent_gantry.schema.tool import ToolDefinition
```

### Naming Conventions

- **Classes**: `PascalCase` (e.g., `AgentGantry`, `ToolDefinition`)
- **Functions/Methods**: `snake_case` (e.g., `retrieve_tools`, `execute_tool`)
- **Constants**: `UPPER_SNAKE_CASE` (e.g., `DEFAULT_LIMIT`, `MAX_RETRIES`)
- **Private**: Prefix with `_` (e.g., `_internal_method`)

### Docstrings

Use Google-style docstrings with clear descriptions, args, returns, and raises:

```python
async def retrieve_tools(self, query: str, limit: int = 10) -> list[ToolDefinition]:
    """
    Retrieve semantically relevant tools for a query.

    Args:
        query: The user query or task description
        limit: Maximum number of tools to return

    Returns:
        List of relevant tool definitions, ordered by relevance

    Raises:
        ValueError: If query is empty or limit is invalid
    """
    ...
```

## Important Configuration

### pyproject.toml Settings

- **Python Version**: 3.10+ required
- **Line Length**: 100 characters max
- **Linter**: ruff with E, F, I, N, W, UP rules
- **Type Checker**: mypy in strict mode
- **Test Framework**: pytest with `asyncio_mode = "auto"`

### Optional Dependencies

The project has modular dependencies:
- `dev` - Development tools (pytest, ruff, mypy)
- `openai`, `anthropic`, `google-genai`, etc. - Individual LLM providers
- `llm-providers` - All LLM providers combined
- `vector-stores` - Qdrant, Chroma, pgvector
- `lancedb` - Local persistence with LanceDB
- `nomic` - Nomic embeddings (Matryoshka)
- `mcp` - Model Context Protocol support
- `a2a` - Agent-to-Agent protocol support
- `agent-frameworks` - LangChain, AutoGen, CrewAI, etc.
- `all` - Everything

## Security Considerations

This is a **security-critical** library that executes arbitrary tool code. Always:

1. **Validate Tool Arguments**: Check against tool schemas before execution
2. **Respect Capabilities**: Honor `ToolCapability` and permission systems
3. **Circuit Breaker States**: Don't execute tools with open circuit breakers
4. **Input Sanitization**: Never trust external input to tool execution
5. **No Secrets**: Never commit API keys, tokens, or credentials

## Semantic Tool Decorator

The `@with_semantic_tools` decorator is the primary user-facing API. It automatically:
1. Extracts the user prompt from the wrapped function's arguments
2. Performs semantic tool retrieval via the Gantry instance
3. Converts tools to the target LLM provider format (dialect)
4. Injects tools into the function call

Example usage:
```python
from agent_gantry import set_default_gantry, with_semantic_tools

set_default_gantry(gantry)  # Set once at startup

@with_semantic_tools(limit=3, dialect="openai")
async def generate(prompt: str, *, tools=None):
    return await client.chat.completions.create(
        model="gpt-4o",
        messages=[{"role": "user", "content": prompt}],
        tools=tools  # Automatically injected by decorator
    )
```

## MCP and A2A Integration

### MCP (Model Context Protocol)

- **Server Mode**: `await gantry.serve_mcp(transport="stdio", mode="dynamic")`
- **Client Mode**: `await gantry.add_mcp_server(config)` to consume external MCP servers
- **Dynamic Mode**: Exposes 2 meta-tools (`find_relevant_tools`, `execute_tool`) instead of all tools

### A2A (Agent-to-Agent)

- **Server Mode**: `gantry.serve_a2a(host="0.0.0.0", port=8080)` - exposes Agent Card
- **Client Mode**: `await gantry.add_a2a_agent(config)` to consume external A2A agents
- **Skills Mapping**: External agent skills are registered as local tools

## Examples Directory

The `examples/` directory contains comprehensive demonstrations:

- `basics/` - Simple usage patterns
- `llm_integration/` - Per-provider examples (OpenAI, Anthropic, Google, Mistral, Groq)
- `protocols/` - MCP and A2A demonstrations
- `testing_limits/` - Stress tests and benchmarks
- `tool_vector_db/` - Smart vectorization and persistence examples
- `project_demo/` - Full project structure with persistent storage

Always check examples when implementing new features or fixing bugs - they serve as integration tests.

## Git Workflow

- Work on feature branches
- Keep commits focused and atomic
- Write descriptive commit messages
- Run tests and linting before committing (`pytest && ruff check . && mypy agent_gantry/`)
- Update CHANGELOG.md for user-facing changes

## Additional Resources

- **README.md** - High-level architecture and quick start guide
- **CONTRIBUTING.md** - Detailed contribution guidelines and workflow
- **QUICK_REFERENCE.md** - Summary of recent API improvements
- **docs/** - Detailed documentation on specific features
- **.github/copilot-instructions.md** - Extended development guidelines
