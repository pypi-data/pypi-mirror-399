# RAG Template Filling Example

**Build a production RAG application in ~30 lines of code using Fluxibly's plug-and-play configuration system.**

## What It Does

Creates complete, structured lectures by:
1. Loading template structure and one-shot example
2. Retrieving relevant content from Qdrant vector database
3. Generating comprehensive output following the template format

**Zero boilerplate. Pure configuration.**

## Quick Start

```bash
# Prerequisites
uv add fluxibly
cp .env.example local.env  # Add your OPENAI_API_KEY

# Ensure Qdrant is running
docker run -p 6333:6333 qdrant/qdrant

# Run
uv run python examples/rag_template_filling.py
```

## The Complete Code

```python
async def test_template_filling():
    # 1. Load resources
    with open("./examples/resources/outline.md", encoding="utf-8") as f:
        template_content = f.read()
    with open("./examples/resources/example_oneshot.md", encoding="utf-8") as f:
        example_content = f.read()

    # 2. Define task
    task_description = f"""
    Create a complete lecture on "Internal Communication Strategy"

    TEMPLATE: {template_content}
    EXAMPLE: {example_content}

    Source documents:
    - "Current Trends in Internal Communication.pdf"
    - "Internal Communications Manual.pdf"
    """

    # 3. Execute - that's it!
    async with WorkflowSession(profile="rag_assistant") as session:
        response = await session.execute(task_description)
```

**Everything else is configuration.**

## How It Works: The 3-Layer System

```
┌─────────────────────────────────────────────────────────┐
│ 1. Your Code (Python)                                   │
│    - Define task                                        │
│    - Select profile                                     │
└─────────────────────┬───────────────────────────────────┘
                      │
┌─────────────────────▼───────────────────────────────────┐
│ 2. Profile Config (YAML)                                │
│    - Agent behavior & prompts                           │
│    - MCP server selection                               │
│    - Execution parameters                               │
└─────────────────────┬───────────────────────────────────┘
                      │
┌─────────────────────▼───────────────────────────────────┐
│ 3. MCP Servers (Tools)                                  │
│    - RAG search, file ops, APIs                         │
│    - Auto-wired by framework                            │
└─────────────────────────────────────────────────────────┘
```

## Profile Configuration

[`config/profiles/rag_assistant.yaml`](../config/profiles/rag_assistant.yaml):

```yaml
profile:
  name: "rag_assistant"

workflow:
  agent_type: "orchestrator"
  stateful: true

enabled_servers:
  - custom_rag  # Enable RAG capabilities

orchestrator:
  model: "gpt-4.1"
  temperature: 0.1
  max_tokens: 16000

  system_prompt: |
    You are a teaching assistant specializing in [domain].
    Retrieve information and synthesize into structured lectures.

  mcp_servers:
    - custom_rag
  max_mcp_calls: 15
  max_iterations: 5
```

MCP server config [`config/mcp_servers.yaml`](../config/mcp_servers.yaml):

```yaml
mcp_servers:
  custom_rag:
    command: "python"
    args: ["-m", "mcp_servers.custom_rag.server"]
    env:
      RAG_API_URL: "http://localhost:8000"
    enabled: true
```

## Customization

### Create Your Own Profile

```yaml
# config/profiles/my_assistant.yaml
profile:
  name: "my_assistant"

workflow:
  agent_type: "orchestrator"

enabled_servers:
  - custom_rag
  - filesystem  # Add file operations
  - github      # Add code search

orchestrator:
  model: "gpt-4o"
  temperature: 0.3
  system_prompt: |
    Your custom instructions here...
```

Use it:

```python
async with WorkflowSession(profile="my_assistant") as session:
    response = await session.execute("Your task")
```

### Switch Profiles Instantly

```python
# RAG workflow
await WorkflowSession(profile="rag_assistant").execute(task)

# Travel planning
await WorkflowSession(profile="travel_assistant").execute(task)

# Code generation
await WorkflowSession(profile="development_assistant").execute(task)
```

**Same code. Different capabilities. Zero refactoring.**

## Advanced Usage

**Stateful conversations:**

```python
async with WorkflowSession(profile="rag_assistant") as session:
    r1 = await session.execute("Find info on strategic planning")
    r2 = await session.execute("Show me case studies")  # Remembers context
```

**Batch processing:**

```python
from fluxibly import run_batch_workflow

responses = await run_batch_workflow(
    ["Task 1", "Task 2", "Task 3"],
    profile="rag_assistant"
)
```

**Custom context:**

```python
context = {
    "collection_name": "my_docs",
    "filter": {"topic": "internal_comms"}
}

async with WorkflowSession(profile="rag_assistant") as session:
    response = await session.execute(task, context=context)
```
