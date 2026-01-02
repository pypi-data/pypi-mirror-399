# MCP Client Manager

The MCP Client Manager provides a unified interface for managing connections to multiple MCP (Model Context Protocol) servers and invoking their tools.

## Features

- **Multi-server Management**: Connect to and manage multiple MCP servers simultaneously
- **Tool Discovery**: Automatically discover and aggregate tools from all connected servers
- **Unified Invocation**: Invoke tools across different servers through a single interface
- **Configuration-driven**: Configure servers via YAML files
- **Graceful Lifecycle**: Proper initialization and shutdown handling
- **Error Resilient**: Continues operation even if individual servers fail

## Architecture

The MCP Client Manager integrates seamlessly with the Agent and OrchestratorAgent classes:

```
┌─────────────────┐
│  Agent/Orch     │
│                 │
│  - prepare()    │
│  - forward()    │
└────────┬────────┘
         │
         │ uses
         ▼
┌─────────────────┐
│ MCPClientManager│
│                 │
│  - initialize() │
│  - get_tools()  │
│  - invoke_tool()│
│  - shutdown()   │
└────────┬────────┘
         │
         │ manages
         ▼
┌─────────────────┐
│  MCP Servers    │
│                 │
│  - OCR          │
│  - Vision       │
│  - Code         │
│  - Research     │
└─────────────────┘
```

## Configuration

MCP servers are configured via YAML files. See `config/mcp_servers.yaml` for the schema:

```yaml
mcp_servers:
  server_name:
    command: "python"                    # Command to start the server
    args: ["-m", "mcp_servers.module"]   # Command arguments
    env:                                 # Environment variables
      API_KEY: "${ENV_VAR}"              # Supports env var expansion
      CONFIG: "value"
    enabled: true                        # Whether to connect to this server
    priority: 1                          # Server priority (optional)
```

### Environment Variable Expansion

Environment variables in the format `${VAR_NAME}` are automatically expanded:

```yaml
env:
  API_KEY: "${OPENAI_API_KEY}"  # Expands to value of OPENAI_API_KEY
```

## Usage

### Basic Usage

```python
from fluxibly.mcp_client.manager import MCPClientManager

# Initialize manager
manager = MCPClientManager("config/mcp_servers.yaml")

# Connect to servers and discover tools
await manager.initialize()

# Get all available tools
tools = manager.get_all_tools()
for tool in tools:
    print(f"{tool['name']}: {tool['description']}")

# Invoke a tool
result = await manager.invoke_tool(
    tool_name="example_tool",
    args={"param": "value"}
)

# Cleanup
await manager.shutdown()
```

### Integration with Agent

```python
from fluxibly.agent.base import Agent, AgentConfig
from fluxibly.mcp_client.manager import MCPClientManager
from fluxibly.llm.base import LLMConfig

# Create MCP manager
mcp_manager = MCPClientManager("config/mcp_servers.yaml")
await mcp_manager.initialize()

# Create agent with MCP support
agent_config = AgentConfig(
    name="research_agent",
    llm=LLMConfig(model="gpt-4o", framework="langchain"),
    system_prompt="You are a research assistant.",
    mcp_servers=["web_search", "wikipedia"]
)

agent = Agent(config=agent_config, mcp_client_manager=mcp_manager)

# Use the agent
response = await agent.forward("What is the capital of France?")

# Cleanup
await mcp_manager.shutdown()
```

### Integration with OrchestratorAgent

```python
from fluxibly.orchestrator.agent import OrchestratorAgent, OrchestratorConfig
from fluxibly.mcp_client.manager import MCPClientManager
from fluxibly.llm.base import LLMConfig

# Create MCP manager
mcp_manager = MCPClientManager("config/mcp_servers.yaml")
await mcp_manager.initialize()

# Create orchestrator with MCP support
orchestrator_config = OrchestratorConfig(
    name="document_processor",
    llm=LLMConfig(model="gpt-4o", framework="langchain"),
    system_prompt="You are a document processing orchestrator.",
    mcp_servers=["ocr", "vision", "text_analysis"],
    max_iterations=5,
    plan_refinement_enabled=True
)

orchestrator = OrchestratorAgent(
    config=orchestrator_config,
    mcp_client_manager=mcp_manager
)

# Use the orchestrator
response = await orchestrator.forward(
    user_prompt="Extract and analyze all data from this PDF",
    context={"document_path": "/path/to/invoice.pdf"}
)

# Cleanup
await mcp_manager.shutdown()
```

## API Reference

### MCPClientManager

#### `__init__(config_path: str)`

Initialize the MCP Client Manager.

**Parameters:**
- `config_path`: Path to the YAML configuration file

#### `async initialize() -> None`

Connect to all enabled MCP servers and discover their tools.

**Raises:**
- `FileNotFoundError`: If config file doesn't exist
- `ValueError`: If config is invalid
- `Exception`: If initialization fails

#### `async shutdown() -> None`

Gracefully shutdown all MCP server connections.

#### `get_all_tools() -> list[dict[str, Any]]`

Get all available tools from connected servers.

**Returns:**
- List of tool schemas, each containing:
  - `name`: Tool name
  - `description`: Tool description
  - `schema`: Input schema (JSON Schema)
  - `server`: Server name providing this tool

#### `async invoke_tool(tool_name: str, args: dict[str, Any]) -> Any`

Execute a tool through the appropriate MCP server.

**Parameters:**
- `tool_name`: Name of the tool to invoke
- `args`: Tool arguments matching the tool's input schema

**Returns:**
- Tool execution result

**Raises:**
- `ValueError`: If tool not found or server not connected
- `Exception`: If tool execution fails

## Tool Name Conflicts

If multiple servers provide tools with the same name, the manager will use the first server's tool and log a warning. You can control which server's tool is used by ordering servers in the configuration file.

## Error Handling

The manager implements resilient error handling:

1. **Initialization**: If one server fails to connect, others continue
2. **Tool Discovery**: If one server fails, tools from other servers are still available
3. **Shutdown**: All servers are shut down even if some fail

All errors are logged for debugging.

## Testing

Comprehensive unit tests are available in `tests/unit/test_mcp_client_manager.py`:

```bash
# Run MCP client tests
uv run --frozen pytest tests/unit/test_mcp_client_manager.py -v

# Run with coverage
uv run --frozen pytest tests/unit/test_mcp_client_manager.py --cov=fluxibly.mcp_client
```

## Examples

See `examples/mcp_client_usage.py` for a complete working example.

## Implementation Details

### Connection Lifecycle

The manager keeps MCP server connections alive using context managers:

1. `stdio_client` provides the communication channel
2. `ClientSession` manages the MCP protocol session
3. Both are stored and properly cleaned up on shutdown

### Tool Aggregation

Tools are aggregated after all servers connect:

1. Query each server for its tool list
2. Build a unified tool registry
3. Detect and handle name conflicts
4. Make tools available via `get_all_tools()`

### Thread Safety

The manager is designed for async/await usage and is not thread-safe. Use it within a single async event loop.
