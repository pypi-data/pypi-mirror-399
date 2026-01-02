# Maintainer Guide

Quick reference for understanding the Fluxibly codebase structure and maintenance workflows.

## Project Structure

```
fluxibly/
├── fluxibly/              # Core framework package
├── config/                # Configuration files (YAML)
├── mcp_servers/          # MCP server implementations
├── examples/             # Usage examples & demos
├── tests/                # Test suite (unit + integration)
├── docs/                 # Documentation
├── pyproject.toml        # Package metadata & dependencies
└── CLAUDE.md             # Development guidelines
```

## Core Package (`fluxibly/`)

The main framework implementation.

### Directory Structure

```
fluxibly/
├── __init__.py           # Public API exports (WorkflowSession, run_workflow, etc.)
├── agent/                # Base agent implementations
├── orchestrator/         # Orchestrator agent (planning + execution)
├── workflow/             # Workflow engine & session management
├── mcp_client/          # MCP server connection & tool management
├── llm/                 # LLM provider abstractions
├── config/              # Configuration loaders
```

### Key Modules

**[`workflow/`](fluxibly/workflow/)** - Entry point for users
- `WorkflowSession` - Context manager for workflow execution
- `WorkflowEngine` - Core execution engine
- `WorkflowConfig` - Configuration schema

**[`orchestrator/`](fluxibly/orchestrator/)** - Intelligent agent orchestration
- `OrchestratorAgent` - Planning, execution, and synthesis agent
- Multi-step reasoning with MCP tool usage
- Query rewriting, plan refinement, result synthesis

**[`agent/`](fluxibly/agent/)** - Base agent abstractions
- `Agent` - Base class for all agents
- `AgentConfig` - Agent configuration schema

**[`llm/`](fluxibly/llm/)** - LLM integrations
- Provider-agnostic LLM interface
- Supports OpenAI, Anthropic via LangChain

## Configuration (`config/`)

YAML-based configuration system.

```
config/
├── mcp_servers.yaml           # MCP server definitions
├── framework.yaml             # Framework-level settings
├── profiles/                  # Pre-built workflow profiles
│   ├── default.yaml
│   ├── rag_assistant.yaml
└── orchestrator/              # Orchestrator-specific configs
```

### Configuration Files

**`mcp_servers.yaml`** - Define available MCP servers
- Server command, args, environment variables
- Enable/disable servers
- Priority ordering

**`profiles/*.yaml`** - Workflow profiles
- Agent type selection
- MCP server selection
- Model parameters (temperature, max_tokens)
- System prompts
- Execution settings

**Profile structure:**
```yaml
profile:
  name: "profile_name"
  description: "What this profile does"

workflow:
  agent_type: "orchestrator"  # or "agent"
  stateful: true/false

enabled_servers:
  - server_name_1
  - server_name_2

orchestrator:  # Agent-specific config
  model: "gpt-4o"
  temperature: 0.7
  max_tokens: 4000
  system_prompt: |
    Your instructions here...
  mcp_servers:
    - server_name_1
  max_iterations: 5
  plan_refinement_enabled: true
```

## MCP Servers (`mcp_servers/`)

Capability extensions via Model Context Protocol.

```
mcp_servers/
├── README.md                  # Overview & how to add servers
├── custom_rag/               # ✅ RAG search & indexing (READY)
│   ├── server.py
│   ├── config.py
│   └── README.md
```

### Active Servers

**`custom_rag/`** - RAG integration
- Tools: `rag-search`, `rag-index-gcs`
- Connects to existing RAG API
- See [mcp_servers/custom_rag/README.md](mcp_servers/custom_rag/README.md)

### Adding New Servers

1. Create directory: `mcp_servers/your_server/`
2. Implement: `server.py` using MCP SDK
3. Register: Add to `config/mcp_servers.yaml`
4. Document: Create `README.md`
5. Test: Create test example

See [mcp_servers/README.md](mcp_servers/README.md) for details.

## Examples (`examples/`)

Working examples demonstrating framework usage.

### Key Examples

**[`rag_template_filling.py`](examples/rag_template_filling.py)** - RAG workflow
- Shows profile-based configuration
- Template filling with semantic search
- See [README_RAG_TEMPLATE_FILLING.md](examples/README_RAG_TEMPLATE_FILLING.md)

## Common Maintenance Tasks

### Adding a New Profile

1. Create `config/profiles/your_profile.yaml`
2. Define agent type, servers, settings
3. Add example to `examples/`
4. Update profile table in docs

### Adding a New MCP Server

1. Implement in `mcp_servers/your_server/`
2. Add to `config/mcp_servers.yaml`
3. Create profile that uses it
4. Add tests and examples

### Updating Dependencies

```bash
# Update a package
uv add package-name --upgrade-package package-name

# Update dev dependency
uv add --dev package-name --upgrade-package package-name
```

### Code Quality Checks

```bash
# Format code
uv run --frozen ruff format .

# Lint code
uv run --frozen ruff check .

# Fix linting issues
uv run --frozen ruff check . --fix

# Type checking
uv run --frozen pyright
```

### Release Workflow

1. Update version in `pyproject.toml`
2. Run full test suite
3. Update CHANGELOG
4. Create git tag
5. Build and publish

## Architecture Patterns

### Configuration-First Design

- Behavior defined in YAML, not code
- Profiles enable instant workflow switching
- MCP servers add capabilities declaratively

### MCP-Native

- Tools are first-class citizens
- Auto-discovery and aggregation
- Protocol-level compatibility

### Async-First

- All I/O operations are async
- Use `async with` for resource management
- Event loop per session

### Type-Safe

- Pydantic for all data structures
- Type hints required
- Runtime validation

## Debugging Tips

### Enable Debug Logging

```python
import logging
logging.basicConfig(level=logging.DEBUG)
orchestrator_logger = logging.getLogger("fluxibly.orchestrator")
orchestrator_logger.setLevel(logging.DEBUG)
```

### Inspect MCP Tools

```python
manager = MCPClientManager("config/mcp_servers.yaml")
await manager.initialize()
tools = manager.get_all_tools()
print([t["name"] for t in tools])
```

### Verify Profile Loading

```bash
python -c "from fluxibly.workflow import WorkflowEngine; print(WorkflowEngine.from_profile('rag_assistant').config)"
```

### Check Server Connections

```bash
# Test MCP server directly
python -m mcp_servers.custom_rag.server

# Check API connectivity
curl http://localhost:8000/health
```

## Development Workflow

1. **Branch**: Create feature branch (`feat/`, `fix/`, `chore/`)
2. **Code**: Follow CLAUDE.md guidelines
3. **Test**: Add tests for new features
4. **Format**: Run ruff format + check
5. **Type Check**: Run pyright
6. **Commit**: Conventional commit messages
7. **PR**: Open pull request to `main`