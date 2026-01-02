"""Example usage of MCP Client Manager.

This example demonstrates how to:
1. Initialize the MCP Client Manager with a configuration file
2. Connect to MCP servers
3. Discover available tools
4. Invoke tools through the manager
5. Properly shutdown connections
"""

import asyncio
from pathlib import Path

from fluxibly.mcp_client.manager import MCPClientManager


async def main():
    """Main example function demonstrating MCP Client Manager usage."""
    # Path to MCP server configuration
    config_path = Path(__file__).parent.parent / "config" / "mcp_servers.yaml"

    # Create the MCP Client Manager
    manager = MCPClientManager(str(config_path))

    try:
        # Initialize and connect to all enabled MCP servers
        print("Initializing MCP Client Manager...")
        await manager.initialize()
        print(f"Successfully connected to {len(manager.servers)} servers")

        # Get all available tools
        tools = manager.get_all_tools()
        print(f"\nDiscovered {len(tools)} tools:")
        for tool in tools:
            print(f"  - {tool['name']}: {tool['description']}")
            print(f"    Server: {tool['server']}")

        # Example: Invoke a tool (if available)
        if tools:
            example_tool = tools[0]
            print(f"\n\nExample: Invoking tool '{example_tool['name']}'...")

            # Note: You would need to provide appropriate arguments based on the tool's schema
            # This is just a placeholder example
            try:
                # result = await manager.invoke_tool(
                #     tool_name=example_tool['name'],
                #     args={"example_arg": "example_value"}
                # )
                # print(f"Tool result: {result}")
                print("(Skipped - requires actual tool arguments)")
            except Exception as e:
                print(f"Error invoking tool: {e}")

    finally:
        # Always shutdown gracefully
        print("\n\nShutting down MCP Client Manager...")
        await manager.shutdown()
        print("Shutdown complete")


if __name__ == "__main__":
    asyncio.run(main())
