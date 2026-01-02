"""MCP Client Manager for unified server communication.

This module handles all communication with MCP servers including server lifecycle,
tool discovery, and unified invocation interface.
"""

import os
from pathlib import Path
from typing import Any

import yaml
from loguru import logger
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client


class MCPClientManager:
    """Central manager for all MCP server communication.

    Provides server lifecycle management, tool discovery, and unified invocation interface.
    """

    def __init__(self, config_path: str) -> None:
        """Initialize the MCP client manager.

        Args:
            config_path: Path to MCP server configuration file
        """
        self.config_path = config_path
        self.servers: dict[str, dict[str, Any]] = {}
        self.tools: dict[str, dict[str, Any]] = {}  # tool_name -> {server, schema}
        self.config: dict[str, Any] = {}
        self._logger = logger.bind(component="mcp_client_manager")

    async def initialize(self) -> None:
        """Connect to all configured MCP servers and discover tools.

        Establishes connections and aggregates tool schemas from all servers.
        """
        try:
            # Load configuration
            self.config = self._load_config(self.config_path)
            self._logger.info(f"Loaded MCP configuration from {self.config_path}")

            # Get list of enabled servers
            mcp_servers = self.config.get("mcp_servers", {})
            enabled_servers = {name: cfg for name, cfg in mcp_servers.items() if cfg.get("enabled", True)}

            if not enabled_servers:
                self._logger.warning("No enabled MCP servers found in configuration")
                return

            # Connect to each server
            self._logger.info(f"Connecting to {len(enabled_servers)} MCP servers")
            for name, server_config in enabled_servers.items():
                try:
                    await self._connect_server(name, server_config)
                    self._logger.info(f"Successfully connected to MCP server: {name}")
                except Exception:
                    self._logger.exception(f"Failed to connect to MCP server: {name}")
                    # Continue with other servers even if one fails

            # Aggregate tools from all connected servers
            await self._aggregate_tools()
            self._logger.info(f"Discovered {len(self.tools)} tools across {len(self.servers)} servers")

        except Exception:
            self._logger.exception("Failed to initialize MCP client manager")
            raise

    async def shutdown(self) -> None:
        """Gracefully shutdown all MCP server connections.

        Properly closes all connections and drains pending requests.
        """
        self._logger.info("Shutting down MCP client manager")

        for name, server_info in list(self.servers.items()):
            try:
                # Exit the session context first
                session_context = server_info.get("session_context")
                if session_context:
                    await session_context.__aexit__(None, None, None)
                    self._logger.debug(f"Closed session for server: {name}")

                # Then exit the stdio context
                stdio_context = server_info.get("stdio_context")
                if stdio_context:
                    await stdio_context.__aexit__(None, None, None)
                    self._logger.debug(f"Closed stdio connection for server: {name}")

            except Exception:
                self._logger.exception(f"Error shutting down server: {name}")

        self.servers.clear()
        self.tools.clear()
        self._logger.info("MCP client manager shutdown complete")

    def get_all_tools(self) -> list[dict[str, Any]]:
        """Return aggregated tool schemas for orchestrator.

        Returns:
            List of tool schemas from all connected MCP servers
        """
        return list(self.tools.values())

    async def invoke_tool(self, tool_name: str, args: dict[str, Any]) -> Any:
        """Execute a tool through the appropriate MCP server.

        Args:
            tool_name: Name of the tool to invoke
            args: Tool arguments

        Returns:
            Tool execution result

        Raises:
            ValueError: If tool not found
            Exception: If tool execution fails
        """
        if tool_name not in self.tools:
            available_tools = list(self.tools.keys())
            raise ValueError(f"Tool '{tool_name}' not found. Available tools: {available_tools}")

        tool_info = self.tools[tool_name]
        server_name = tool_info["server"]
        server_info = self.servers.get(server_name)

        if not server_info:
            raise ValueError(f"Server '{server_name}' not connected")

        session: ClientSession = server_info["session"]

        try:
            self._logger.debug(f"Invoking tool '{tool_name}' on server '{server_name}' with args: {args}")

            # Call the tool through MCP
            result = await session.call_tool(tool_name, arguments=args)

            self._logger.debug(f"Tool '{tool_name}' execution completed successfully")
            return result

        except Exception:
            self._logger.exception(f"Failed to invoke tool '{tool_name}'")
            raise

    async def _connect_server(self, name: str, config: dict[str, Any]) -> None:
        """Connect to an MCP server.

        Args:
            name: Server name
            config: Server configuration
        """
        command = config.get("command")
        args = config.get("args", [])
        env = config.get("env", {})

        if not command:
            raise ValueError(f"Server '{name}' missing required 'command' field")

        # Expand environment variables in env values
        expanded_env = {}
        for key, value in env.items():
            if isinstance(value, str) and value.startswith("${") and value.endswith("}"):
                env_var = value[2:-1]
                expanded_env[key] = os.environ.get(env_var, "")
            else:
                expanded_env[key] = str(value)

        # Merge with current environment
        server_env = os.environ.copy()
        server_env.update(expanded_env)

        # Create server parameters
        server_params = StdioServerParameters(command=command, args=args, env=server_env)

        try:
            # Connect to the server using stdio transport
            # We need to keep these context managers alive for the lifetime of the manager
            stdio_context = stdio_client(server_params)
            read, write = await stdio_context.__aenter__()

            session_context = ClientSession(read, write)
            session = await session_context.__aenter__()

            # Initialize the session
            await session.initialize()

            # Store connection info with context managers to properly close later
            self.servers[name] = {
                "config": config,
                "session": session,
                "session_context": session_context,
                "stdio_context": stdio_context,
                "params": server_params,
            }

            self._logger.debug(f"Initialized session for server: {name}")

        except Exception:
            self._logger.exception(f"Failed to connect to server: {name}")
            raise

    async def _aggregate_tools(self) -> None:
        """Aggregate tool schemas from all connected servers."""
        self.tools.clear()

        for server_name, server_info in self.servers.items():
            try:
                session: ClientSession = server_info["session"]

                # List available tools from this server
                tools_result = await session.list_tools()

                # Store each tool with its server reference
                for tool in tools_result.tools:
                    tool_schema = {
                        "name": tool.name,
                        "description": tool.description,
                        "schema": tool.inputSchema,
                        "server": server_name,
                    }

                    # Check for name conflicts
                    if tool.name in self.tools:
                        existing_server = self.tools[tool.name]["server"]
                        self._logger.warning(
                            f"Tool name conflict: '{tool.name}' exists in both "
                            f"'{existing_server}' and '{server_name}'. Using '{existing_server}'."
                        )
                        continue

                    self.tools[tool.name] = tool_schema
                    self._logger.debug(f"Registered tool '{tool.name}' from server '{server_name}'")

            except Exception:
                self._logger.exception(f"Failed to aggregate tools from server: {server_name}")

    def _load_config(self, config_path: str) -> dict[str, Any]:
        """Load MCP server configuration from file.

        Args:
            config_path: Path to configuration file

        Returns:
            Configuration dictionary

        Raises:
            FileNotFoundError: If config file doesn't exist
            ValueError: If config file is invalid
        """
        path = Path(config_path)

        if not path.exists():
            raise FileNotFoundError(f"MCP configuration file not found: {config_path}")

        try:
            with path.open("r") as f:
                config = yaml.safe_load(f)

            if not isinstance(config, dict):
                raise ValueError(f"Invalid MCP configuration: expected dict, got {type(config)}")

            return config

        except yaml.YAMLError as e:
            self._logger.exception(f"Failed to parse YAML configuration: {config_path}")
            raise ValueError(f"Invalid YAML in configuration file: {config_path}") from e
        except Exception:
            self._logger.exception(f"Failed to load MCP configuration: {config_path}")
            raise
