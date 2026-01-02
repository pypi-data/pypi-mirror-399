"""Integration tests with real MCP servers.

This module tests the MCP Client Manager with actual MCP servers to validate
end-to-end functionality.
"""

from pathlib import Path

import pytest

from fluxibly.mcp_client.manager import MCPClientManager


@pytest.fixture
def test_config_path():
    """Get path to test MCP server configuration."""
    config_path = Path(__file__).parent.parent.parent / "config" / "test_mcp_servers.yaml"
    return str(config_path)


class TestRealMCPServerIntegration:
    """Integration tests with real MCP servers."""

    @pytest.mark.anyio
    @pytest.mark.integration
    async def test_connect_to_simple_math_server(self, test_config_path):
        """Test connecting to a real simple math MCP server."""
        manager = MCPClientManager(test_config_path)

        try:
            # Initialize and connect
            await manager.initialize()

            # Verify server connected
            assert "simple_math" in manager.servers
            assert len(manager.servers) == 1

            # Verify tools discovered
            tools = manager.get_all_tools()
            assert len(tools) > 0

            # Check for expected tools
            tool_names = {tool["name"] for tool in tools}
            assert "add" in tool_names
            assert "multiply" in tool_names
            assert "power" in tool_names

        finally:
            await manager.shutdown()

    @pytest.mark.anyio
    @pytest.mark.integration
    async def test_invoke_add_tool(self, test_config_path):
        """Test invoking the add tool on real MCP server."""
        manager = MCPClientManager(test_config_path)

        try:
            await manager.initialize()

            # Invoke the add tool
            result = await manager.invoke_tool("add", {"a": 5, "b": 3})

            # Verify result
            assert result is not None
            # The result structure depends on MCP server implementation
            # It should contain the sum in some form

        finally:
            await manager.shutdown()

    @pytest.mark.anyio
    @pytest.mark.integration
    async def test_invoke_multiply_tool(self, test_config_path):
        """Test invoking the multiply tool on real MCP server."""
        manager = MCPClientManager(test_config_path)

        try:
            await manager.initialize()

            # Invoke the multiply tool
            result = await manager.invoke_tool("multiply", {"a": 4, "b": 7})

            # Verify result exists
            assert result is not None

        finally:
            await manager.shutdown()

    @pytest.mark.anyio
    @pytest.mark.integration
    async def test_invoke_power_tool(self, test_config_path):
        """Test invoking the power tool on real MCP server."""
        manager = MCPClientManager(test_config_path)

        try:
            await manager.initialize()

            # Invoke the power tool
            result = await manager.invoke_tool("power", {"base": 2, "exponent": 8})

            # Verify result exists
            assert result is not None

        finally:
            await manager.shutdown()

    @pytest.mark.anyio
    @pytest.mark.integration
    async def test_multiple_tool_invocations(self, test_config_path):
        """Test multiple tool invocations on the same connection."""
        manager = MCPClientManager(test_config_path)

        try:
            await manager.initialize()

            # Invoke multiple tools
            result1 = await manager.invoke_tool("add", {"a": 10, "b": 20})
            result2 = await manager.invoke_tool("multiply", {"a": 5, "b": 6})
            result3 = await manager.invoke_tool("power", {"base": 3, "exponent": 3})

            # All should succeed
            assert result1 is not None
            assert result2 is not None
            assert result3 is not None

        finally:
            await manager.shutdown()

    @pytest.mark.anyio
    @pytest.mark.integration
    async def test_tool_schema_structure(self, test_config_path):
        """Test that tool schemas have correct structure."""
        manager = MCPClientManager(test_config_path)

        try:
            await manager.initialize()

            tools = manager.get_all_tools()

            for tool in tools:
                # Verify required fields
                assert "name" in tool
                assert "description" in tool
                assert "schema" in tool
                assert "server" in tool

                # Verify schema structure
                schema = tool["schema"]
                assert "type" in schema
                assert schema["type"] == "object"
                assert "properties" in schema
                assert "required" in schema

                # Verify server name
                assert tool["server"] == "simple_math"

        finally:
            await manager.shutdown()

    @pytest.mark.anyio
    @pytest.mark.integration
    async def test_graceful_shutdown(self, test_config_path):
        """Test that shutdown properly closes connections."""
        manager = MCPClientManager(test_config_path)

        await manager.initialize()
        assert len(manager.servers) == 1
        assert len(manager.tools) > 0

        await manager.shutdown()

        # After shutdown, servers and tools should be cleared
        assert len(manager.servers) == 0
        assert len(manager.tools) == 0

    @pytest.mark.anyio
    @pytest.mark.integration
    async def test_reinitialize_after_shutdown(self, test_config_path):
        """Test that manager can be reinitialized after shutdown."""
        manager = MCPClientManager(test_config_path)

        # First cycle
        await manager.initialize()
        tools_count_first = len(manager.tools)
        await manager.shutdown()

        # Second cycle
        await manager.initialize()
        tools_count_second = len(manager.tools)
        await manager.shutdown()

        # Should have same number of tools both times
        assert tools_count_first == tools_count_second
        assert tools_count_first > 0
