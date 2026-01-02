# Fluxibly Examples

This directory contains examples demonstrating various capabilities of the Fluxibly agent framework.

## Example Categories

- **[RAG (Retrieval-Augmented Generation)](#rag-examples)** - Semantic search with Qdrant
- **[MCP Client Manager](#mcp-client-manager-examples)** - MCP server integration
- **[Workflow Examples](#workflow-examples)** - Basic to advanced workflows

---

## RAG Examples

**See [RAG_EXAMPLES.md](RAG_EXAMPLES.md) for detailed documentation.**

Retrieval-Augmented Generation using Qdrant vector database for semantic search and knowledge retrieval.

### Prerequisites
- Qdrant running on `localhost:6333`
- Collection: `rag_documents` (automatically created by setup scripts)
- Embedding model: `all-MiniLM-L6-v2`

**Note:** The examples use a separate `rag_documents` collection to avoid conflicts with any existing `documents` collection you may have in Qdrant.

### Examples

| Example | Description | Run Time |
|---------|-------------|----------|
| [workflow_rag_basic.py](workflow_rag_basic.py) | Simple Q&A with semantic retrieval | ~10-30s |
| [workflow_rag_conversational.py](workflow_rag_conversational.py) | Multi-turn context-aware conversations | ~30-60s |
| [workflow_rag_advanced.py](workflow_rag_advanced.py) | Multi-hop reasoning and synthesis | ~60-120s |
| [workflow_rag_hybrid.py](workflow_rag_hybrid.py) | Hybrid RAG with multiple tools | ~60-180s |
| [workflow_rag_academic.py](workflow_rag_academic.py) | Academic course syllabus queries | ~30-90s |

**Quick start:**
```bash
# Basic RAG
uv run python examples/workflow_rag_basic.py

# Conversational RAG
uv run python examples/workflow_rag_conversational.py

# Advanced multi-hop reasoning
uv run python examples/workflow_rag_advanced.py

# Hybrid RAG workflows
uv run python examples/workflow_rag_hybrid.py

# Academic RAG (with course syllabus)
uv run python examples/setup_qdrant_academic.py  # Setup first
uv run python examples/workflow_rag_academic.py
```

**Use cases:**
- Technical documentation search
- Research paper analysis
- Customer support knowledge base
- Enterprise Q&A systems
- Academic course information systems

---

## MCP Client Manager Examples

### 1. Verify Implementation (Fastest ⚡)
**File:** [verify_mcp_implementation.py](verify_mcp_implementation.py)

**Run time:** ~2 seconds
**Requirements:** None (uses mocks)

```bash
uv run python examples/verify_mcp_implementation.py
```

**What it does:**
- Validates all MCP Client Manager functionality
- Uses mocks (no real servers needed)
- Perfect for CI/CD pipelines

### 2. Test with Custom Server
**File:** [test_real_mcp_server.py](test_real_mcp_server.py)

**Run time:** ~5-10 seconds
**Requirements:** Simple math server (included)

```bash
uv run python examples/test_real_mcp_server.py
```

**What it does:**
- Tests with our custom simple math MCP server
- Demonstrates tool invocation
- Shows error handling

### 3. Test with Public Servers
**File:** [test_public_mcp_servers.py](test_public_mcp_servers.py)

**Run time:** ~10-30 seconds (first run)
**Requirements:** Node.js/npx

```bash
uv run python examples/test_public_mcp_servers.py
```

**What it does:**
- Tests with official MCP filesystem server
- Validates compatibility with real-world servers
- Demonstrates production usage

### 4. Basic Usage Template
**File:** [mcp_client_usage.py](mcp_client_usage.py)

**Run time:** Depends on servers
**Requirements:** Configured MCP servers

```bash
uv run python examples/mcp_client_usage.py
```

**What it does:**
- Shows basic usage patterns
- Template for your own code
- Integration guide

## Example Comparison

| Example | Speed | Requirements | Best For |
|---------|-------|--------------|----------|
| verify_mcp_implementation.py | ⚡⚡⚡ | None | Quick validation, CI/CD |
| test_real_mcp_server.py | ⚡⚡ | Python | Testing implementation |
| test_public_mcp_servers.py | ⚡ | Node.js | Production validation |
| mcp_client_usage.py | Varies | Servers | Learning, templates |

## When to Use Each Example

### Use `verify_mcp_implementation.py` when:
- ✓ You want fast validation
- ✓ You're running in CI/CD
- ✓ You don't have servers available
- ✓ You want to check API compliance

### Use `test_real_mcp_server.py` when:
- ✓ You want to test with a real server
- ✓ You're developing new features
- ✓ You need to see actual tool results
- ✓ You're debugging issues

### Use `test_public_mcp_servers.py` when:
- ✓ You want production validation
- ✓ You're testing compatibility
- ✓ You have Node.js installed
- ✓ You're evaluating for real use

### Use `mcp_client_usage.py` when:
- ✓ You're learning the API
- ✓ You need a code template
- ✓ You're integrating into your project
- ✓ You want basic examples

## Configuration Files

Examples use different configuration files:

```
config/
├── mcp_servers.yaml         # Production servers
├── test_mcp_servers.yaml    # Custom test server
└── public_mcp_servers.yaml  # Public/official servers
```

## Running All Examples

```bash
# Quick validation (2s)
uv run python examples/verify_mcp_implementation.py

# Test with custom server (5-10s)
uv run python examples/test_real_mcp_server.py

# Test with public server (10-30s first run)
uv run python examples/test_public_mcp_servers.py
```

## Troubleshooting

### Common Issues

**"ImportError: No module named 'fluxibly'"**
```bash
# Install dependencies
uv sync
```

**"FileNotFoundError: config file not found"**
```bash
# Make sure you're in the project root
cd /path/to/fluxibly
```

**"npx: command not found" (for public servers)**
```bash
# Install Node.js
brew install node  # macOS
# or download from nodejs.org
```

**"Connection timeout"**
- Check server is configured correctly
- Verify network connection
- Look at server logs for errors

## Example Output

### Successful Verification
```
╔════════════════════════════════════════════════════════════════════╗
║      MCP Client Manager - Implementation Verification             ║
╚════════════════════════════════════════════════════════════════════╝
======================================================================
Testing MCP Client Manager Implementation
======================================================================

[Test 1] Initialization
✓ MCPClientManager instance created

[Test 2] Configuration Loading
✓ Configuration loaded successfully

[Test 3] Mock Server Connection and Tool Discovery
✓ Connected to 1 server(s)
✓ Discovered 2 tool(s)

...

╔════════════════════════════════════════════════════════════════════╗
║                  ✓ ALL VERIFICATIONS PASSED                       ║
╚════════════════════════════════════════════════════════════════════╝
```

## Additional Resources

- **Testing Guide:** [README_TESTING.md](README_TESTING.md)
- **Public Servers:** [../docs/public_mcp_testing.md](../docs/public_mcp_testing.md)
- **API Documentation:** [../fluxibly/mcp_client/README.md](../fluxibly/mcp_client/README.md)

## Contributing Examples

When adding new examples:

1. Follow the naming pattern: `verb_object.py`
2. Include comprehensive docstrings
3. Add error handling
4. Update this README
5. Test before committing

## Example Template

```python
"""Brief description of what this example does.

Longer description with requirements and purpose.
"""

import asyncio
from pathlib import Path
from fluxibly.mcp_client.manager import MCPClientManager


async def main():
    """Main function with descriptive docstring."""
    config_path = Path(__file__).parent.parent / "config" / "your_config.yaml"
    manager = MCPClientManager(str(config_path))

    try:
        await manager.initialize()

        # Your code here

    finally:
        await manager.shutdown()


if __name__ == "__main__":
    asyncio.run(main())
```

---

## Workflow Examples

General workflow patterns demonstrating the Fluxibly framework capabilities.

| Example | Description | Features |
|---------|-------------|----------|
| [workflow_basic.py](workflow_basic.py) | Simple single-task execution | Basic workflow, no state |
| [workflow_stateful_session.py](workflow_stateful_session.py) | Multi-turn conversations | Context persistence |
| [workflow_batch.py](workflow_batch.py) | Batch processing multiple tasks | Parallel execution |
| [workflow_advanced.py](workflow_advanced.py) | Complex orchestration patterns | Multi-agent coordination |

**Quick start:**
```bash
# Basic workflow
uv run python examples/workflow_basic.py

# Stateful conversation
uv run python examples/workflow_stateful_session.py

# Batch processing
uv run python examples/workflow_batch.py
```

---

## Questions?

- Check the [Testing Guide](README_TESTING.md)
- Review [API Documentation](../fluxibly/mcp_client/README.md)
- See [Public MCP Testing](../docs/public_mcp_testing.md)
- See [RAG Examples](RAG_EXAMPLES.md) for vector search workflows
- Run `uv run python examples/verify_mcp_implementation.py` to validate setup
