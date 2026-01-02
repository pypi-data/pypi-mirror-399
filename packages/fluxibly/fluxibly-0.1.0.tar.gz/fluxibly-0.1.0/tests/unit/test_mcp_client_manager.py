"""Unit tests for MCP Client Manager."""

import os
from unittest.mock import AsyncMock, Mock, patch

import pytest
import yaml

from fluxibly.mcp_client.manager import MCPClientManager


@pytest.fixture
def temp_config_file(tmp_path):
    """Create a temporary MCP configuration file."""
    config_path = tmp_path / "mcp_servers.yaml"
    config_data = {
        "mcp_servers": {
            "test_server": {
                "command": "python",
                "args": ["-m", "test_server"],
                "env": {"API_KEY": "test_key"},
                "enabled": True,
                "priority": 1,
            },
            "disabled_server": {
                "command": "python",
                "args": ["-m", "disabled"],
                "enabled": False,
            },
        }
    }

    with config_path.open("w") as f:
        yaml.dump(config_data, f)

    return str(config_path)


@pytest.fixture
def temp_config_with_env_vars(tmp_path):
    """Create a config file with environment variable expansion."""
    config_path = tmp_path / "mcp_servers_env.yaml"
    config_data = {
        "mcp_servers": {
            "env_server": {
                "command": "python",
                "args": ["-m", "env_server"],
                "env": {"EXPANDED_KEY": "${TEST_ENV_VAR}", "STATIC_KEY": "static_value"},
                "enabled": True,
            }
        }
    }

    with config_path.open("w") as f:
        yaml.dump(config_data, f)

    return str(config_path)


@pytest.fixture
def mock_session():
    """Create a mock MCP session."""
    session = AsyncMock()
    session.initialize = AsyncMock()
    session.list_tools = AsyncMock()
    session.call_tool = AsyncMock()
    session.__aenter__ = AsyncMock(return_value=session)
    session.__aexit__ = AsyncMock()
    return session


@pytest.fixture
def mock_stdio_client():
    """Create a mock stdio client."""
    mock_read = Mock()
    mock_write = Mock()
    stdio_mock = AsyncMock()
    stdio_mock.__aenter__ = AsyncMock(return_value=(mock_read, mock_write))
    stdio_mock.__aexit__ = AsyncMock()
    return stdio_mock, mock_read, mock_write


class TestMCPClientManagerInitialization:
    """Tests for MCPClientManager initialization."""

    def test_init_basic(self, temp_config_file):
        """Test basic initialization."""
        manager = MCPClientManager(temp_config_file)

        assert manager.config_path == temp_config_file
        assert manager.servers == {}
        assert manager.tools == {}
        assert manager.config == {}

    def test_init_with_invalid_path(self):
        """Test initialization with invalid config path."""
        manager = MCPClientManager("/nonexistent/path.yaml")
        assert manager.config_path == "/nonexistent/path.yaml"


class TestConfigurationLoading:
    """Tests for configuration loading."""

    def test_load_config_success(self, temp_config_file):
        """Test successful configuration loading."""
        manager = MCPClientManager(temp_config_file)
        config = manager._load_config(temp_config_file)

        assert "mcp_servers" in config
        assert "test_server" in config["mcp_servers"]
        assert config["mcp_servers"]["test_server"]["command"] == "python"

    def test_load_config_file_not_found(self):
        """Test loading non-existent config file."""
        manager = MCPClientManager("/nonexistent/config.yaml")

        with pytest.raises(FileNotFoundError, match="MCP configuration file not found"):
            manager._load_config("/nonexistent/config.yaml")

    def test_load_config_invalid_yaml(self, tmp_path):
        """Test loading invalid YAML."""
        invalid_yaml = tmp_path / "invalid.yaml"
        invalid_yaml.write_text("invalid: yaml: content: [")

        manager = MCPClientManager(str(invalid_yaml))

        with pytest.raises(ValueError, match="Invalid YAML in configuration file"):
            manager._load_config(str(invalid_yaml))

    def test_load_config_not_dict(self, tmp_path):
        """Test loading config that's not a dictionary."""
        list_yaml = tmp_path / "list.yaml"
        list_yaml.write_text("- item1\n- item2\n")

        manager = MCPClientManager(str(list_yaml))

        with pytest.raises(ValueError, match="Invalid MCP configuration: expected dict"):
            manager._load_config(str(list_yaml))


class TestServerConnection:
    """Tests for server connection logic."""

    @pytest.mark.anyio
    async def test_connect_server_basic(self, temp_config_file, mock_session, mock_stdio_client):
        """Test basic server connection."""
        manager = MCPClientManager(temp_config_file)
        config = manager._load_config(temp_config_file)
        server_config = config["mcp_servers"]["test_server"]

        stdio_mock, mock_read, mock_write = mock_stdio_client

        with patch("fluxibly.mcp_client.manager.stdio_client", return_value=stdio_mock):
            with patch("fluxibly.mcp_client.manager.ClientSession", return_value=mock_session):
                await manager._connect_server("test_server", server_config)

        assert "test_server" in manager.servers
        assert manager.servers["test_server"]["session"] == mock_session
        mock_session.initialize.assert_called_once()

    @pytest.mark.anyio
    async def test_connect_server_missing_command(self, temp_config_file):
        """Test connection with missing command field."""
        manager = MCPClientManager(temp_config_file)
        invalid_config = {"args": ["-m", "test"], "enabled": True}

        with pytest.raises(ValueError, match="missing required 'command' field"):
            await manager._connect_server("bad_server", invalid_config)

    @pytest.mark.anyio
    async def test_connect_server_env_expansion(self, temp_config_with_env_vars, mock_session, mock_stdio_client):
        """Test environment variable expansion."""
        os.environ["TEST_ENV_VAR"] = "expanded_value"

        manager = MCPClientManager(temp_config_with_env_vars)
        config = manager._load_config(temp_config_with_env_vars)
        server_config = config["mcp_servers"]["env_server"]

        stdio_mock, mock_read, mock_write = mock_stdio_client

        with patch("fluxibly.mcp_client.manager.stdio_client", return_value=stdio_mock):
            with patch("fluxibly.mcp_client.manager.ClientSession", return_value=mock_session):
                await manager._connect_server("env_server", server_config)

        # Verify environment was properly expanded
        assert "env_server" in manager.servers
        stored_params = manager.servers["env_server"]["params"]
        assert stored_params.env["EXPANDED_KEY"] == "expanded_value"
        assert stored_params.env["STATIC_KEY"] == "static_value"

        # Cleanup
        del os.environ["TEST_ENV_VAR"]

    @pytest.mark.anyio
    async def test_connect_server_connection_failure(self, temp_config_file):
        """Test handling of connection failures."""
        manager = MCPClientManager(temp_config_file)
        config = manager._load_config(temp_config_file)
        server_config = config["mcp_servers"]["test_server"]

        with patch("fluxibly.mcp_client.manager.stdio_client", side_effect=Exception("Connection failed")):
            with pytest.raises(Exception, match="Connection failed"):
                await manager._connect_server("test_server", server_config)


class TestToolAggregation:
    """Tests for tool aggregation from servers."""

    @pytest.mark.anyio
    async def test_aggregate_tools_basic(self):
        """Test basic tool aggregation."""
        manager = MCPClientManager("dummy_path")

        # Create mock tool
        mock_tool = Mock()
        mock_tool.name = "test_tool"
        mock_tool.description = "A test tool"
        mock_tool.inputSchema = {"type": "object"}

        # Create mock session with tools
        mock_session = AsyncMock()
        tools_result = Mock()
        tools_result.tools = [mock_tool]
        mock_session.list_tools.return_value = tools_result

        # Add server to manager
        manager.servers["test_server"] = {
            "session": mock_session,
            "config": {},
        }

        await manager._aggregate_tools()

        assert "test_tool" in manager.tools
        assert manager.tools["test_tool"]["name"] == "test_tool"
        assert manager.tools["test_tool"]["description"] == "A test tool"
        assert manager.tools["test_tool"]["server"] == "test_server"
        assert manager.tools["test_tool"]["schema"] == {"type": "object"}

    @pytest.mark.anyio
    async def test_aggregate_tools_multiple_servers(self):
        """Test aggregating tools from multiple servers."""
        manager = MCPClientManager("dummy_path")

        # Server 1 tools
        tool1 = Mock()
        tool1.name = "tool1"
        tool1.description = "Tool from server 1"
        tool1.inputSchema = {"type": "object"}

        # Server 2 tools
        tool2 = Mock()
        tool2.name = "tool2"
        tool2.description = "Tool from server 2"
        tool2.inputSchema = {"type": "object"}

        # Setup mock sessions
        session1 = AsyncMock()
        result1 = Mock()
        result1.tools = [tool1]
        session1.list_tools.return_value = result1

        session2 = AsyncMock()
        result2 = Mock()
        result2.tools = [tool2]
        session2.list_tools.return_value = result2

        manager.servers["server1"] = {"session": session1, "config": {}}
        manager.servers["server2"] = {"session": session2, "config": {}}

        await manager._aggregate_tools()

        assert len(manager.tools) == 2
        assert manager.tools["tool1"]["server"] == "server1"
        assert manager.tools["tool2"]["server"] == "server2"

    @pytest.mark.anyio
    async def test_aggregate_tools_name_conflict(self):
        """Test handling of tool name conflicts."""
        manager = MCPClientManager("dummy_path")

        # Both servers have a tool with the same name
        tool1 = Mock()
        tool1.name = "duplicate_tool"
        tool1.description = "From server 1"
        tool1.inputSchema = {"type": "object"}

        tool2 = Mock()
        tool2.name = "duplicate_tool"
        tool2.description = "From server 2"
        tool2.inputSchema = {"type": "object"}

        session1 = AsyncMock()
        result1 = Mock()
        result1.tools = [tool1]
        session1.list_tools.return_value = result1

        session2 = AsyncMock()
        result2 = Mock()
        result2.tools = [tool2]
        session2.list_tools.return_value = result2

        manager.servers["server1"] = {"session": session1, "config": {}}
        manager.servers["server2"] = {"session": session2, "config": {}}

        await manager._aggregate_tools()

        # Should only have one tool (from server1, processed first)
        assert len(manager.tools) == 1
        assert manager.tools["duplicate_tool"]["server"] == "server1"
        assert manager.tools["duplicate_tool"]["description"] == "From server 1"

    @pytest.mark.anyio
    async def test_aggregate_tools_server_failure(self):
        """Test aggregation continues even if one server fails."""
        manager = MCPClientManager("dummy_path")

        # Successful server
        tool1 = Mock()
        tool1.name = "working_tool"
        tool1.description = "Working tool"
        tool1.inputSchema = {"type": "object"}

        session1 = AsyncMock()
        result1 = Mock()
        result1.tools = [tool1]
        session1.list_tools.return_value = result1

        # Failing server
        session2 = AsyncMock()
        session2.list_tools.side_effect = Exception("Server error")

        manager.servers["working_server"] = {"session": session1, "config": {}}
        manager.servers["failing_server"] = {"session": session2, "config": {}}

        # Should not raise, just log the error
        await manager._aggregate_tools()

        # Should still have tool from working server
        assert "working_tool" in manager.tools
        assert manager.tools["working_tool"]["server"] == "working_server"


class TestInitializeAndShutdown:
    """Tests for initialize and shutdown methods."""

    @pytest.mark.anyio
    async def test_initialize_success(self, temp_config_file, mock_session, mock_stdio_client):
        """Test successful initialization."""
        manager = MCPClientManager(temp_config_file)

        stdio_mock, mock_read, mock_write = mock_stdio_client

        # Mock tool for aggregation
        mock_tool = Mock()
        mock_tool.name = "test_tool"
        mock_tool.description = "Test tool"
        mock_tool.inputSchema = {"type": "object"}

        tools_result = Mock()
        tools_result.tools = [mock_tool]
        mock_session.list_tools.return_value = tools_result

        with patch("fluxibly.mcp_client.manager.stdio_client", return_value=stdio_mock):
            with patch("fluxibly.mcp_client.manager.ClientSession", return_value=mock_session):
                await manager.initialize()

        assert len(manager.servers) == 1  # Only enabled server
        assert "test_server" in manager.servers
        assert "disabled_server" not in manager.servers
        assert len(manager.tools) == 1
        assert "test_tool" in manager.tools

    @pytest.mark.anyio
    async def test_initialize_no_enabled_servers(self, tmp_path):
        """Test initialization with no enabled servers."""
        config_path = tmp_path / "no_enabled.yaml"
        config_data = {
            "mcp_servers": {
                "disabled1": {"command": "python", "enabled": False},
                "disabled2": {"command": "python", "enabled": False},
            }
        }
        with config_path.open("w") as f:
            yaml.dump(config_data, f)

        manager = MCPClientManager(str(config_path))
        await manager.initialize()

        assert len(manager.servers) == 0
        assert len(manager.tools) == 0

    @pytest.mark.anyio
    async def test_initialize_partial_failure(self, tmp_path, mock_session, mock_stdio_client):
        """Test initialization continues even if one server fails."""
        # Create config with two servers where one will fail
        config_path = tmp_path / "two_servers.yaml"
        config_data = {
            "mcp_servers": {
                "working_server": {
                    "command": "python",
                    "args": ["-m", "working"],
                    "enabled": True,
                },
                "failing_server": {
                    "command": "python",
                    "args": ["-m", "failing"],
                    "enabled": True,
                },
            }
        }
        with config_path.open("w") as f:
            yaml.dump(config_data, f)

        manager = MCPClientManager(str(config_path))

        stdio_mock, mock_read, mock_write = mock_stdio_client

        # Mock tools
        mock_tool = Mock()
        mock_tool.name = "test_tool"
        mock_tool.description = "Test tool"
        mock_tool.inputSchema = {"type": "object"}
        tools_result = Mock()
        tools_result.tools = [mock_tool]
        mock_session.list_tools.return_value = tools_result

        # Track which server is being connected
        servers_attempted = []

        def stdio_side_effect(params):
            servers_attempted.append(params.args[1])  # Get server module name
            if params.args[1] == "failing":
                raise Exception("Connection failed")
            return stdio_mock

        with patch("fluxibly.mcp_client.manager.stdio_client", side_effect=stdio_side_effect):
            with patch("fluxibly.mcp_client.manager.ClientSession", return_value=mock_session):
                await manager.initialize()

        # Should have one successful connection
        assert len(manager.servers) == 1
        assert "working_server" in manager.servers
        # Both servers should have been attempted
        assert len(servers_attempted) == 2

    @pytest.mark.anyio
    async def test_shutdown_success(self):
        """Test successful shutdown."""
        manager = MCPClientManager("dummy_path")

        # Create mock contexts
        session_context = AsyncMock()
        session_context.__aexit__ = AsyncMock()

        stdio_context = AsyncMock()
        stdio_context.__aexit__ = AsyncMock()

        manager.servers["test_server"] = {
            "session_context": session_context,
            "stdio_context": stdio_context,
        }
        manager.tools["test_tool"] = {"name": "test_tool", "server": "test_server"}

        await manager.shutdown()

        # Verify contexts were exited
        session_context.__aexit__.assert_called_once_with(None, None, None)
        stdio_context.__aexit__.assert_called_once_with(None, None, None)

        # Verify cleanup
        assert len(manager.servers) == 0
        assert len(manager.tools) == 0

    @pytest.mark.anyio
    async def test_shutdown_with_errors(self):
        """Test shutdown continues even if one server fails."""
        manager = MCPClientManager("dummy_path")

        # Server 1: normal shutdown
        session_context1 = AsyncMock()
        session_context1.__aexit__ = AsyncMock()
        stdio_context1 = AsyncMock()
        stdio_context1.__aexit__ = AsyncMock()

        # Server 2: fails during shutdown
        session_context2 = AsyncMock()
        session_context2.__aexit__ = AsyncMock(side_effect=Exception("Shutdown error"))
        stdio_context2 = AsyncMock()
        stdio_context2.__aexit__ = AsyncMock()

        manager.servers["server1"] = {
            "session_context": session_context1,
            "stdio_context": stdio_context1,
        }
        manager.servers["server2"] = {
            "session_context": session_context2,
            "stdio_context": stdio_context2,
        }

        # Should not raise, just log errors
        await manager.shutdown()

        # Both servers should be cleaned up despite error
        assert len(manager.servers) == 0


class TestToolInvocation:
    """Tests for tool invocation."""

    @pytest.mark.anyio
    async def test_invoke_tool_success(self):
        """Test successful tool invocation."""
        manager = MCPClientManager("dummy_path")

        # Setup mock session
        mock_session = AsyncMock()
        mock_session.call_tool = AsyncMock(return_value={"result": "success"})

        manager.servers["test_server"] = {
            "session": mock_session,
            "config": {},
        }
        manager.tools["test_tool"] = {
            "name": "test_tool",
            "server": "test_server",
            "description": "Test tool",
        }

        result = await manager.invoke_tool("test_tool", {"arg1": "value1"})

        assert result == {"result": "success"}
        mock_session.call_tool.assert_called_once_with("test_tool", arguments={"arg1": "value1"})

    @pytest.mark.anyio
    async def test_invoke_tool_not_found(self):
        """Test invoking non-existent tool."""
        manager = MCPClientManager("dummy_path")
        manager.tools["existing_tool"] = {
            "name": "existing_tool",
            "server": "test_server",
        }

        with pytest.raises(ValueError, match="Tool 'nonexistent' not found"):
            await manager.invoke_tool("nonexistent", {})

    @pytest.mark.anyio
    async def test_invoke_tool_server_not_connected(self):
        """Test invoking tool when server is not connected."""
        manager = MCPClientManager("dummy_path")

        manager.tools["orphan_tool"] = {
            "name": "orphan_tool",
            "server": "disconnected_server",
        }

        with pytest.raises(ValueError, match="Server 'disconnected_server' not connected"):
            await manager.invoke_tool("orphan_tool", {})

    @pytest.mark.anyio
    async def test_invoke_tool_execution_failure(self):
        """Test handling of tool execution failure."""
        manager = MCPClientManager("dummy_path")

        mock_session = AsyncMock()
        mock_session.call_tool = AsyncMock(side_effect=Exception("Execution failed"))

        manager.servers["test_server"] = {
            "session": mock_session,
            "config": {},
        }
        manager.tools["failing_tool"] = {
            "name": "failing_tool",
            "server": "test_server",
        }

        with pytest.raises(Exception, match="Execution failed"):
            await manager.invoke_tool("failing_tool", {"arg": "value"})


class TestGetAllTools:
    """Tests for get_all_tools method."""

    def test_get_all_tools_empty(self):
        """Test getting tools when none are registered."""
        manager = MCPClientManager("dummy_path")
        tools = manager.get_all_tools()

        assert tools == []

    def test_get_all_tools_with_tools(self):
        """Test getting all registered tools."""
        manager = MCPClientManager("dummy_path")

        manager.tools = {
            "tool1": {
                "name": "tool1",
                "description": "First tool",
                "server": "server1",
            },
            "tool2": {
                "name": "tool2",
                "description": "Second tool",
                "server": "server2",
            },
        }

        tools = manager.get_all_tools()

        assert len(tools) == 2
        assert any(t["name"] == "tool1" for t in tools)
        assert any(t["name"] == "tool2" for t in tools)

    def test_get_all_tools_returns_copy(self):
        """Test that get_all_tools returns a new list."""
        manager = MCPClientManager("dummy_path")
        manager.tools = {
            "tool1": {"name": "tool1", "server": "server1"},
        }

        tools1 = manager.get_all_tools()
        tools2 = manager.get_all_tools()

        # Should be equal but not the same object
        assert tools1 == tools2
        assert tools1 is not tools2
