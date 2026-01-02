"""Tool Aggregator for MCP server tool management.

This module collects and normalizes tool schemas from all MCP servers.
"""

from typing import Any


class ToolAggregator:
    """Aggregates and manages tools from multiple MCP servers.

    Collects tool schemas from all MCP servers and provides unified tool definitions
    for the orchestrator.
    """

    def __init__(self) -> None:
        """Initialize the tool aggregator."""
        self.tools: dict[str, dict[str, Any]] = {}  # tool_name -> tool_info

    def register_tool(self, tool_name: str, server_name: str, schema: dict[str, Any]) -> None:
        """Register a tool from an MCP server.

        Args:
            tool_name: Name of the tool
            server_name: Name of the MCP server providing the tool
            schema: Tool schema definition
        """
        raise NotImplementedError

    def unregister_server_tools(self, server_name: str) -> None:
        """Remove all tools from a specific MCP server.

        Args:
            server_name: Name of the MCP server
        """
        raise NotImplementedError

    def get_tool(self, tool_name: str) -> dict[str, Any] | None:
        """Retrieve tool information by name.

        Args:
            tool_name: Name of the tool

        Returns:
            Tool information or None if not found
        """
        raise NotImplementedError

    def list_tools(self, server_name: str | None = None) -> list[dict[str, Any]]:
        """List all registered tools.

        Args:
            server_name: Optional server name to filter tools

        Returns:
            List of tool schemas
        """
        raise NotImplementedError

    def to_langchain_tools(self) -> list[Any]:
        """Convert MCP tool schemas to LangChain tool format.

        Returns:
            List of LangChain-compatible tool definitions
        """
        raise NotImplementedError
