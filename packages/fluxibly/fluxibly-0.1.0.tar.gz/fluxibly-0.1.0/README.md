# Fluxibly

**MCP-Native Agentic Framework for General-Purpose Task Automation**

[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

Fluxibly is a modular, extensible agentic framework with native support for the Model Context Protocol (MCP). It enables developers to create sophisticated AI agents that can interact with external tools and services through MCP servers.

## Features

- **MCP-Native Architecture**: First-class support for Model Context Protocol servers
- **Flexible Workflow Engine**: Execute single tasks or batch operations with ease
- **Stateful Conversations**: Maintain context across multiple interactions
- **Profile-Based Configuration**: Easy setup with YAML-based configuration profiles
- **Async-First Design**: Fully asynchronous API for high performance

## Installation

Install Fluxibly using pip:

```bash
pip install fluxibly
```

Or using uv (recommended):

```bash
uv add fluxibly
```

## Quick Start

### Simple One-Shot Execution

```python
import asyncio
from fluxibly import run_workflow

async def main():
    response = await run_workflow(
        "What is the capital of France?",
        profile="default"
    )
    print(response)

asyncio.run(main())
```

### Using the Workflow Engine

```python
import asyncio
from fluxibly import WorkflowEngine, WorkflowConfig

async def main():
    # Configure the workflow
    config = WorkflowConfig(
        name="my_workflow",
        agent_type="orchestrator",
        profile="default",
        stateful=False
    )

    # Create and initialize engine
    engine = WorkflowEngine(config=config)
    try:
        await engine.initialize()
        response = await engine.execute("Your task here")
        print(response)
    finally:
        await engine.shutdown()

asyncio.run(main())
```

### Batch Processing

```python
import asyncio
from fluxibly import run_batch_workflow

async def main():
    tasks = [
        "Explain async/await in Python",
        "What are Python decorators?",
        "How does the GIL work?"
    ]

    responses = await run_batch_workflow(
        tasks,
        profile="development_assistant"
    )

    for task, response in zip(tasks, responses):
        print(f"Q: {task}")
        print(f"A: {response}\n")

asyncio.run(main())
```

## Configuration

Fluxibly uses YAML-based configuration profiles. You can use built-in profiles or create custom ones.

### Using Custom Profile Files

You can also load profiles from custom file paths:

```python
# Load by absolute path
engine = WorkflowEngine.from_profile("/path/to/my_profile.yaml")

# Load by relative path
engine = WorkflowEngine.from_profile("../custom_profiles/special.yaml")

# Also works with convenience functions
response = await run_workflow(
    "Your task",
    profile="/path/to/my_profile.yaml"
)
```

### Profile Format

Here's an example profile structure:

```yaml
name: default
description: Default configuration profile

llm:
  provider: anthropic
  model: claude-sonnet-4-5-20250929
  temperature: 0.7
  max_tokens: 4096

mcp:
  enabled: true
  servers_config: config/mcp_servers.yaml
```

## MCP Server Integration

Fluxibly provides seamless integration with MCP servers. Configure your MCP servers in `config/mcp_servers.yaml`:

```yaml
servers:
  filesystem:
    command: npx
    args:
      - -y
      - "@modelcontextprotocol/server-filesystem"
      - "/path/to/allowed/directory"
    env:
      NODE_OPTIONS: "--max-old-space-size=4096"
```

Then use the MCP client manager in your code:

```python
from fluxibly import MCPClientManager

async def main():
    manager = MCPClientManager()
    await manager.initialize()

    # MCP tools are now available to your agents
    # ...

    await manager.cleanup()
```

## Advanced Features

### Stateful Conversations

```python
config = WorkflowConfig(
    name="stateful_workflow",
    agent_type="agent",
    profile="default",
    stateful=True  # Enable state persistence
)

engine = WorkflowEngine(config=config)
await engine.initialize()

# First interaction
response1 = await engine.execute("My name is Alice")

# Context is preserved
response2 = await engine.execute("What's my name?")
# Response will remember "Alice"
```

## Development

### Setting Up Development Environment

```bash
# Clone the repository
git clone https://github.com/Lavaflux/fluxibly.git
cd fluxibly

# Install dependencies
uv sync

# Run tests
uv run --frozen pytest

# Format code
uv run --frozen ruff format .

# Type checking
uv run --frozen pyright
```

## Requirements

- Python 3.11 or higher
- API keys for LLM providers (e.g., Anthropic, OpenAI)
- Optional: Node.js for MCP server support

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## Links

- **GitHub**: https://github.com/Lavaflux/fluxibly
- **Issues**: https://github.com/Lavaflux/fluxibly/issues
- **Documentation**: https://github.com/Lavaflux/fluxibly#readme

## Acknowledgments

Built with:
- [LangChain](https://github.com/langchain-ai/langchain) - LLM application framework
- [Model Context Protocol](https://modelcontextprotocol.io/) - Tool integration protocol
