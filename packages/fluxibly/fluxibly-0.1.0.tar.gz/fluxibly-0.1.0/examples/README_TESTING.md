# MCP Client Manager Testing Guide

This directory contains examples and tests for validating the MCP Client Manager implementation.

## Quick Start

### 1. Verify Implementation (No Server Required)

Run the verification script to test the MCP client without needing a running server:

```bash
uv run python examples/verify_mcp_implementation.py
```

This tests:
- ✓ Basic initialization
- ✓ Configuration loading
- ✓ Mock server connections
- ✓ Tool discovery
- ✓ Tool invocation
- ✓ Error handling
- ✓ Graceful shutdown
- ✓ API interface compliance

**Expected Output:**
```
╔════════════════════════════════════════════════════════════════════╗
║                  ✓ ALL VERIFICATIONS PASSED                       ║
╚════════════════════════════════════════════════════════════════════╝
```

### 2. Test with Real MCP Server

The project includes a simple math MCP server for integration testing.

**Running the test manually:**

```bash
# Run the verification example
uv run python examples/test_real_mcp_server.py
```

This demonstrates:
- Connecting to a real MCP server
- Discovering tools from the server
- Invoking tools (add, multiply, power)
- Multiple operations
- Error handling
- Graceful shutdown

### 3. Run Integration Tests

Integration tests use pytest markers:

```bash
# Run all integration tests
PYTEST_DISABLE_PLUGIN_AUTOLOAD="" uv run --frozen pytest tests/integration/test_mcp_real_server.py -v -m integration

# Run specific test
PYTEST_DISABLE_PLUGIN_AUTOLOAD="" uv run --frozen pytest tests/integration/test_mcp_real_server.py::TestRealMCPServerIntegration::test_connect_to_simple_math_server -v
```

## Test Files

### Examples

1. **[verify_mcp_implementation.py](verify_mcp_implementation.py)**
   - Comprehensive verification without real servers
   - Uses mocks to test all functionality
   - Best for quick validation

2. **[test_real_mcp_server.py](test_real_mcp_server.py)**
   - Full integration test with real server
   - Demonstrates practical usage
   - Shows error handling

3. **[mcp_client_usage.py](mcp_client_usage.py)**
   - Basic usage example
   - Template for integration

### Test MCP Server

**[mcp_servers/simple_math/server.py](../mcp_servers/simple_math/server.py)**

A minimal MCP server providing:
- `add(a, b)` - Add two numbers
- `multiply(a, b)` - Multiply two numbers
- `power(base, exponent)` - Raise to power

**Configuration:** `config/test_mcp_servers.yaml`

### Integration Tests

**[tests/integration/test_mcp_real_server.py](../tests/integration/test_mcp_real_server.py)**

Comprehensive integration tests:
- Server connection
- Tool discovery
- Tool invocation (single and multiple)
- Schema validation
- Shutdown and cleanup
- Re-initialization

## Test Coverage

### Unit Tests (98% coverage)

Run unit tests:
```bash
PYTEST_DISABLE_PLUGIN_AUTOLOAD="" uv run --frozen pytest tests/unit/test_mcp_client_manager.py -v
```

**Test Categories:**
- Initialization (2 tests)
- Configuration loading (4 tests)
- Server connection (4 tests)
- Tool aggregation (4 tests)
- Initialize/shutdown (5 tests)
- Tool invocation (4 tests)
- Utility methods (3 tests)

Total: **26 unit tests**, **98% code coverage**

### Integration Tests

Run integration tests:
```bash
PYTEST_DISABLE_PLUGIN_AUTOLOAD="" uv run --frozen pytest tests/integration/ -v -m integration
```

**Test Categories:**
- Real server connection
- Tool discovery
- Tool invocation
- Error handling
- Lifecycle management

## Troubleshooting

### Issue: Import Errors

If you see import errors related to `mcp`:

```bash
# Ensure MCP package is installed
uv add mcp
```

### Issue: Pydantic Version Conflicts

If you see Pydantic-related errors during test collection:

```bash
# Use the PYTEST_DISABLE_PLUGIN_AUTOLOAD environment variable
PYTEST_DISABLE_PLUGIN_AUTOLOAD="" uv run --frozen pytest ...
```

### Issue: Server Connection Timeout

If the MCP server doesn't respond:

1. Check the server is configured correctly in `config/test_mcp_servers.yaml`
2. Verify the server module path is correct
3. Check server logs for errors
4. Increase timeout if needed

### Issue: Tool Not Found

If tools aren't discovered:

1. Verify server implements `list_tools()` correctly
2. Check server is connected (check logs)
3. Verify tool aggregation completed without errors

## Writing Your Own Tests

### Example: Testing a Custom MCP Server

```python
import asyncio
from fluxibly.mcp_client.manager import MCPClientManager

async def test_my_server():
    # Create configuration for your server
    config_path = "path/to/your/config.yaml"

    manager = MCPClientManager(config_path)

    try:
        # Initialize
        await manager.initialize()

        # Get tools
        tools = manager.get_all_tools()
        print(f"Found {len(tools)} tools")

        # Invoke a tool
        result = await manager.invoke_tool("your_tool", {"arg": "value"})
        print(f"Result: {result}")

    finally:
        await manager.shutdown()

asyncio.run(test_my_server())
```

### Example: Configuration File

```yaml
mcp_servers:
  my_server:
    command: "python"
    args: ["-m", "my_package.server"]
    env:
      API_KEY: "${MY_API_KEY}"  # Environment variable
      DEBUG: "true"
    enabled: true
    priority: 1
```

## Best Practices

1. **Always use try/finally for cleanup:**
   ```python
   try:
       await manager.initialize()
       # Your code
   finally:
       await manager.shutdown()
   ```

2. **Check tool availability before invocation:**
   ```python
   tools = manager.get_all_tools()
   tool_names = {t["name"] for t in tools}
   if "my_tool" in tool_names:
       result = await manager.invoke_tool("my_tool", args)
   ```

3. **Handle errors gracefully:**
   ```python
   try:
       result = await manager.invoke_tool(name, args)
   except ValueError as e:
       print(f"Tool not found: {e}")
   except Exception as e:
       print(f"Execution failed: {e}")
   ```

4. **Use configuration files for flexibility:**
   - Don't hardcode server paths
   - Use environment variables for secrets
   - Enable/disable servers as needed

## Performance Tips

1. **Reuse manager instances:** Initialize once, use multiple times
2. **Batch operations:** Make multiple tool calls before shutdown
3. **Handle errors:** One failed server shouldn't break everything
4. **Monitor logs:** Use loguru logs for debugging

## Additional Resources

- [MCP Client Manager Implementation](../fluxibly/mcp_client/README.md)
- [Unit Test Suite](../tests/unit/test_mcp_client_manager.py)
- [Integration Tests](../tests/integration/test_mcp_real_server.py)
- [MCP Protocol Documentation](https://modelcontextprotocol.io/)
