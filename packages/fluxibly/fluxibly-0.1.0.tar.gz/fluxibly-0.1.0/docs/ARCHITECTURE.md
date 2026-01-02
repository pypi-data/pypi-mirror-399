# Fluxibly Architecture

## Overview

Fluxibly is an MCP-native agentic framework built on a three-tier architecture:

1. **LLM Layer**: Direct language model interface
2. **Agent Layer**: Basic tool-calling agents with simple MCP selection
3. **Orchestrator Layer**: Advanced multi-step planning and coordination (optional)

The workflow follows: **User → Agent → (optional) Orchestrator Agent → MCPs**

## Core Components

### 1. LLM (Base Layer)

**Location**: `fluxibly/llm/base.py`

The LLM class provides a simple, unified interface to various language models (both proprietary and open source) via LiteLLM.

**Key Characteristics**:
- **Purpose**: Direct LLM interaction with minimal abstraction
- **Framework**: LiteLLM (supports OpenAI, Anthropic, HuggingFace, Ollama, vLLM, etc.)
- **Primary Method**: `forward(prompt: str) -> str`
- **Philosophy**: No complex logic—just forward prompts to the model

**Supported Models**:
- Proprietary: OpenAI (GPT-4, GPT-3.5), Anthropic (Claude 3.5, Claude 3), Cohere
- Open Source: Llama, Mistral, Mixtral (via HuggingFace, Ollama, vLLM)
- Custom: Any model with OpenAI-compatible API

**Configuration**:
```yaml
llm:
  model: "gpt-4o"  # or "claude-3-5-sonnet-20241022", "ollama/llama2"
  temperature: 0.7
  max_tokens: 4096
  timeout: 60
  max_retries: 3
```

**Usage**:
```python
from fluxibly.llm import LLM, LLMConfig

config = LLMConfig(model="gpt-4o", temperature=0.7)
llm = LLM(config=config)
response = llm.forward("What is machine learning?")
```

### 2. Agent (Middle Layer)

**Location**: `fluxibly/agent/base.py`

The Agent class combines an LLM with system prompts and MCP tools, providing basic tool-calling capabilities.

**Key Characteristics**:
- **Purpose**: Standard agent for simple-to-moderate tasks
- **Components**: LLM + System Prompt + MCP Server List
- **Primary Method**: `forward(user_prompt: str) -> str`
- **MCP Selection**: Basic keyword matching and relevance filtering
- **Use Case**: Single-step or straightforward multi-step tasks

**Workflow**:
1. User provides prompt
2. `prepare()` combines user prompt + system prompt + relevant MCP tools
3. `forward()` sends prepared prompt to LLM
4. LLM decides which MCP tools to call (if any)
5. Agent executes MCP tool calls
6. Returns response with tool results

**Configuration**:
```yaml
agent:
  name: "research_agent"
  llm:
    model: "gpt-4o"
    temperature: 0.7
  system_prompt: "You are a research assistant..."
  mcp_servers: ["web_search", "wikipedia"]
  max_mcp_calls: 5
  mcp_selection_strategy: "auto"  # "all", "auto", "none"
```

**Key Methods**:
- `prepare()`: Combine user prompt with system prompt and select MCPs
- `forward()`: Main execution with basic MCP tool calling
- `select_mcp_tools()`: Simple tool selection based on keywords

**Usage**:
```python
from fluxibly.agent import Agent, AgentConfig
from fluxibly.llm import LLMConfig

config = AgentConfig(
    name="research_agent",
    llm=LLMConfig(model="gpt-4o"),
    system_prompt="You are a research assistant.",
    mcp_servers=["web_search", "wikipedia"]
)
agent = Agent(config=config)
response = agent.forward("What are the latest AI trends?")
```

### 3. OrchestratorAgent (Top Layer - Optional)

**Location**: `fluxibly/orchestrator/agent.py`

The OrchestratorAgent is a specialized Agent subclass designed for complex, multi-step tasks requiring planning, coordination, and iteration.

**Key Characteristics**:
- **Purpose**: Complex task orchestration with advanced planning
- **Inheritance**: Extends `Agent` class
- **Primary Method**: `forward(user_prompt: str) -> str` (with orchestration loop)
- **MCP Selection**: Advanced semantic matching and dependency analysis
- **Use Case**: Complex workflows requiring planning and iteration

**Additional Capabilities**:
- Multi-step planning and plan refinement
- Advanced MCP selection algorithms
- Iterative execution with continuous plan upgrades
- Result synthesis from multiple tool calls
- Error recovery and plan adaptation
- Parallel execution of independent steps

**Workflow**:
1. User provides complex task
2. `prepare_system()` creates detailed orchestration prompt with MCP allocation
3. `forward()` initiates planning loop:
   - **Iteration 1-N** (up to `max_iterations`):
     - `analyze_task()`: Understand requirements
     - `generate_plan()` or `refine_plan()`: Create/update execution plan
     - `execute_plan()`: Run plan steps (with parallelization)
     - Evaluate: Are objectives met?
     - If not complete: refine plan and continue
     - If complete: exit loop
4. `synthesize_results()`: Combine all outputs into final response
5. Return comprehensive result

**Configuration**:
```yaml
orchestrator:
  name: "document_orchestrator"
  llm:
    model: "gpt-4o"
    temperature: 0.7
  system_prompt: "You are an expert orchestrator..."
  mcp_servers: ["ocr", "vision", "text_analysis"]
  max_mcp_calls: 20
  max_iterations: 5
  plan_refinement_enabled: true
  advanced_mcp_selection: true
  result_synthesis_strategy: "llm_synthesis"
  enable_parallel_execution: true
```

**Key Methods**:
- `prepare_system()`: Complex system prompt and advanced MCP allocation
- `forward()`: Orchestration loop with planning and iteration
- `analyze_task()`: Deep task analysis using LLM
- `generate_plan()`: Create structured execution plan
- `execute_plan()`: Execute with parallel execution support
- `refine_plan()`: Update plan based on results
- `synthesize_results()`: Intelligent result combination

**Usage**:
```python
from fluxibly.orchestrator import OrchestratorAgent, OrchestratorConfig
from fluxibly.llm import LLMConfig

config = OrchestratorConfig(
    name="doc_orchestrator",
    llm=LLMConfig(model="gpt-4o"),
    system_prompt="You are a document processing expert.",
    mcp_servers=["ocr", "vision", "analysis"],
    max_iterations=5
)
orchestrator = OrchestratorAgent(config=config)
response = orchestrator.forward(
    "Extract and analyze all data from this invoice",
    context={"document_path": "/path/to/invoice.pdf"}
)
```

## Decision Tree: Which Component to Use?

### Use LLM when:
- You need direct LLM access without tool calling
- Building custom workflows with manual prompt engineering
- Implementing specialized agents with custom logic

### Use Agent when:
- Task requires basic tool calling
- Simple MCP selection is sufficient
- Single-step or straightforward multi-step workflows
- No planning or iteration needed

### Use OrchestratorAgent when:
- Task requires multi-step planning and coordination
- Complex MCP tool selection and orchestration needed
- Iterative refinement necessary
- Multiple tool results need synthesis
- Task benefits from parallel execution

## Configuration System

All components are fully configurable via YAML files:

### Configuration Hierarchy

1. **Base Configuration**: `config/framework.yaml`
   - Default settings for LLM, Agent, Orchestrator
   - Framework-wide settings (logging, health checks, etc.)

2. **Profile Configurations**: `config/profiles/*.yaml`
   - Override base settings for specific use cases
   - Example: `document_processing.yaml`, `development_assistant.yaml`

3. **Runtime Overrides**: Programmatic configuration
   - Override any setting at runtime via code

### Configuration Loading

```python
from fluxibly.config.loader import ConfigLoader

# Load base config
config = ConfigLoader.load_framework_config()

# Load profile config (merges with base)
config = ConfigLoader.load_profile("document_processing")

# Access configuration
llm_config = config["llm"]
agent_config = config["agent"]
orchestrator_config = config["orchestrator"]
```

## MCP Integration

All components (Agent and OrchestratorAgent) integrate with MCP servers for tool calling:

### MCP Server Management

**Location**: `fluxibly/mcp_client/manager.py`

The MCPClientManager handles:
- Server lifecycle (start, stop, health monitoring)
- Tool discovery and aggregation
- Unified tool invocation
- Result routing

### MCP Tool Selection

**Basic Selection (Agent)**:
- Keyword matching between user prompt and tool capabilities
- Simple relevance filtering
- Configured via `mcp_selection_strategy`: "all", "auto", "none"

**Advanced Selection (OrchestratorAgent)**:
- Semantic similarity matching
- Dependency analysis (which tools depend on others)
- Priority assignment based on relevance
- Resource allocation (parallel vs sequential)

### MCP Configuration

```yaml
# config/mcp_servers.yaml
servers:
  ocr:
    command: "uvx"
    args: ["mcp-server-ocr"]
    enabled: true
    priority: 1

  vision:
    command: "uvx"
    args: ["mcp-server-vision"]
    enabled: true
    priority: 2
```

## Data Flow

### Simple Agent Flow
```
User Input
    ↓
Agent.prepare()
    ↓ (combines prompt + system prompt + basic MCP selection)
Agent.forward()
    ↓
LLM.forward(prepared_prompt)
    ↓
LLM Response (with tool calls)
    ↓
MCPClientManager.invoke_tool()
    ↓
Final Response
```

### Orchestrator Flow
```
User Input
    ↓
Orchestrator.prepare_system()
    ↓ (advanced MCP allocation + complex system prompt)
Orchestrator.forward()
    ↓
┌─────────────────────────────────┐
│   Orchestration Loop (1-N)      │
│                                 │
│  1. analyze_task()              │
│  2. generate_plan()/refine()    │
│  3. execute_plan()              │
│     ├─ Step 1 (MCP call)        │
│     ├─ Step 2 (MCP call)        │
│     └─ Step N (MCP call)        │
│  4. Evaluate results            │
│  5. Complete or refine?         │
└─────────────────────────────────┘
    ↓
synthesize_results()
    ↓
Final Comprehensive Response
```

## File Structure

```
fluxibly/
├── llm/
│   ├── __init__.py
│   └── base.py              # LLM base class
├── agent/
│   ├── __init__.py
│   └── base.py              # Agent base class
├── orchestrator/
│   ├── __init__.py
│   ├── agent.py             # OrchestratorAgent (extends Agent)
│   └── graph.py             # LangGraph workflow (if needed)
├── mcp_client/
│   └── manager.py           # MCP server management
├── registry/
│   ├── registry.py          # MCP server registry
│   └── models.py            # Server info models
├── tools/
│   └── aggregator.py        # Tool schema aggregation
├── config/
│   └── loader.py            # Configuration loading
└── schema/
    └── input.py             # Input/output schemas

config/
├── framework.yaml           # Base configuration
├── mcp_servers.yaml         # MCP server definitions
└── profiles/
    ├── document_processing.yaml
    └── development_assistant.yaml
```

## Implementation Status

### ✅ Completed (Skeleton)
- LLM base class with configuration
- Agent base class with configuration
- OrchestratorAgent extending Agent
- Configuration files (framework.yaml, profiles)
- Package structure and __init__ files

### 🚧 To Implement
- LLM.forward() with LiteLLM integration
- Agent.prepare() and Agent.forward()
- Agent.select_mcp_tools()
- OrchestratorAgent.prepare_system()
- OrchestratorAgent orchestration loop
- All Orchestrator planning methods
- MCPClientManager integration

## Design Principles

1. **Simplicity First**: Start with LLM, add Agent for tools, use Orchestrator only when needed
2. **Configuration-Driven**: All parameters configurable via YAML
3. **Provider-Agnostic**: Support any LLM provider via LiteLLM
4. **MCP-Native**: Built around MCP protocol for tool integration
5. **Incremental Complexity**: Each layer adds capabilities without breaking simplicity
6. **Composable**: Components can be mixed and matched for custom workflows

## Next Steps

1. Implement LLM.forward() with LiteLLM
2. Implement Agent basic MCP selection and execution
3. Implement Orchestrator planning and iteration logic
4. Add comprehensive tests for each component
5. Create example workflows and documentation
6. Add observability and monitoring
