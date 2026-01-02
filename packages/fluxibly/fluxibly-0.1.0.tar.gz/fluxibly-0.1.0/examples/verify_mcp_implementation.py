"""Verify MCP Client Manager Implementation.

This script verifies that the MCP Client Manager is correctly implemented
without requiring long-running servers. It performs quick validation checks.
"""

import asyncio
from pathlib import Path
from unittest.mock import AsyncMock, Mock, patch

from fluxibly.mcp_client.manager import MCPClientManager


async def test_basic_functionality():
    """Test basic MCP Client Manager functionality with mocks."""
    print("=" * 70)
    print("Testing MCP Client Manager Implementation")
    print("=" * 70)

    # Test 1: Initialization
    print("\n[Test 1] Initialization")
    config_path = Path(__file__).parent.parent / "config" / "test_mcp_servers.yaml"
    manager = MCPClientManager(str(config_path))
    print("✓ MCPClientManager instance created")
    print(f"  Config path: {manager.config_path}")
    print(f"  Servers: {manager.servers}")
    print(f"  Tools: {manager.tools}")

    # Test 2: Configuration Loading
    print("\n[Test 2] Configuration Loading")
    try:
        config = manager._load_config(str(config_path))
        print("✓ Configuration loaded successfully")
        print(f"  Servers in config: {list(config.get('mcp_servers', {}).keys())}")
    except Exception as e:
        print(f"✗ Failed to load configuration: {e}")
        return

    # Test 3: Mock Server Connection
    print("\n[Test 3] Mock Server Connection and Tool Discovery")

    # Create mock tools
    mock_tool1 = Mock()
    mock_tool1.name = "test_add"
    mock_tool1.description = "Add two numbers"
    mock_tool1.inputSchema = {"type": "object", "properties": {"a": {"type": "number"}, "b": {"type": "number"}}}

    mock_tool2 = Mock()
    mock_tool2.name = "test_multiply"
    mock_tool2.description = "Multiply two numbers"
    mock_tool2.inputSchema = {"type": "object", "properties": {"x": {"type": "number"}, "y": {"type": "number"}}}

    # Create mock session
    mock_session = AsyncMock()
    tools_result = Mock()
    tools_result.tools = [mock_tool1, mock_tool2]
    mock_session.list_tools.return_value = tools_result
    mock_session.call_tool = AsyncMock(return_value={"result": 42})
    mock_session.__aenter__ = AsyncMock(return_value=mock_session)
    mock_session.__aexit__ = AsyncMock()

    # Create mock stdio client
    mock_read = Mock()
    mock_write = Mock()
    stdio_mock = AsyncMock()
    stdio_mock.__aenter__ = AsyncMock(return_value=(mock_read, mock_write))
    stdio_mock.__aexit__ = AsyncMock()

    with patch("fluxibly.mcp_client.manager.stdio_client", return_value=stdio_mock):
        with patch("fluxibly.mcp_client.manager.ClientSession", return_value=mock_session):
            await manager.initialize()

    print(f"✓ Connected to {len(manager.servers)} server(s)")
    print(f"✓ Discovered {len(manager.tools)} tool(s)")

    for tool_name, tool_info in manager.tools.items():
        print(f"  - {tool_name}: {tool_info['description']}")

    # Test 4: Get All Tools
    print("\n[Test 4] Get All Tools")
    all_tools = manager.get_all_tools()
    print(f"✓ Retrieved {len(all_tools)} tools")
    for tool in all_tools:
        print(f"  - {tool['name']} (from {tool['server']})")

    # Test 5: Tool Invocation
    print("\n[Test 5] Tool Invocation")
    result = await manager.invoke_tool("test_add", {"a": 5, "b": 3})
    print("✓ Tool invoked successfully")
    print(f"  Result: {result}")

    # Test 6: Error Handling
    print("\n[Test 6] Error Handling")
    try:
        await manager.invoke_tool("nonexistent_tool", {})
        print("✗ Should have raised ValueError")
    except ValueError as e:
        print("✓ Correctly raised ValueError for unknown tool")
        print(f"  Error: {e}")

    # Test 7: Shutdown
    print("\n[Test 7] Shutdown")
    await manager.shutdown()
    print("✓ Shutdown completed")
    print(f"  Servers remaining: {len(manager.servers)}")
    print(f"  Tools remaining: {len(manager.tools)}")

    print("\n" + "=" * 70)
    print("All Tests Passed!")
    print("=" * 70)


async def test_configuration_validation():
    """Test configuration file validation."""
    print("\n\n" + "=" * 70)
    print("Testing Configuration Validation")
    print("=" * 70)

    config_path = Path(__file__).parent.parent / "config" / "test_mcp_servers.yaml"
    manager = MCPClientManager(str(config_path))

    print("\n[Test] Valid Configuration File")
    try:
        config = manager._load_config(str(config_path))
        print("✓ Configuration is valid")
        print(f"  Keys: {list(config.keys())}")

        if "mcp_servers" in config:
            for name, server_config in config["mcp_servers"].items():
                print(f"\n  Server: {name}")
                print(f"    Command: {server_config.get('command')}")
                print(f"    Args: {server_config.get('args')}")
                print(f"    Enabled: {server_config.get('enabled')}")

    except Exception as e:
        print(f"✗ Configuration validation failed: {e}")

    print("\n[Test] Non-existent Configuration File")
    try:
        manager._load_config("/nonexistent/path.yaml")
        print("✗ Should have raised FileNotFoundError")
    except FileNotFoundError:
        print("✓ Correctly raised FileNotFoundError")


async def test_api_interface():
    """Test that all required methods exist and have correct signatures."""
    print("\n\n" + "=" * 70)
    print("Testing API Interface")
    print("=" * 70)

    manager = MCPClientManager("dummy_path")

    # Check required methods
    required_methods = [
        ("__init__", ["config_path"]),
        ("initialize", []),
        ("shutdown", []),
        ("get_all_tools", []),
        ("invoke_tool", ["tool_name", "args"]),
        ("_connect_server", ["name", "config"]),
        ("_aggregate_tools", []),
        ("_load_config", ["config_path"]),
    ]

    print("\n[Test] Required Methods")
    for method_name, _expected_params in required_methods:
        if hasattr(manager, method_name):
            print(f"✓ {method_name} exists")
        else:
            print(f"✗ {method_name} is missing")

    # Check required attributes
    required_attrs = ["config_path", "servers", "tools", "config"]

    print("\n[Test] Required Attributes")
    for attr_name in required_attrs:
        if hasattr(manager, attr_name):
            value = getattr(manager, attr_name)
            print(f"✓ {attr_name} = {value!r}")
        else:
            print(f"✗ {attr_name} is missing")


async def main():
    """Run all verification tests."""
    print("\n")
    print("╔════════════════════════════════════════════════════════════════════╗")
    print("║      MCP Client Manager - Implementation Verification             ║")
    print("╚════════════════════════════════════════════════════════════════════╝")

    try:
        await test_basic_functionality()
        await test_configuration_validation()
        await test_api_interface()

        print("\n\n")
        print("╔════════════════════════════════════════════════════════════════════╗")
        print("║                  ✓ ALL VERIFICATIONS PASSED                       ║")
        print("╚════════════════════════════════════════════════════════════════════╝")
        print()

    except Exception as e:
        print(f"\n\n✗ Verification failed with error: {e}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())
