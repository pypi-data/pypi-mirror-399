"""Test MCP Client Manager with a Real MCP Server.

This example demonstrates how to:
1. Start a real MCP server (simple math server)
2. Connect to it using MCPClientManager
3. Discover tools
4. Invoke tools
5. Cleanup

Run this script to validate the MCP client implementation works with real servers.
"""

import asyncio
from pathlib import Path

from fluxibly.mcp_client.manager import MCPClientManager


async def main():
    """Main function to test MCP client with real server."""
    print("=" * 70)
    print("Testing MCP Client Manager with Real MCP Server")
    print("=" * 70)

    # Get path to test configuration
    config_path = Path(__file__).parent.parent / "config" / "test_mcp_servers.yaml"

    if not config_path.exists():
        print(f"\nError: Configuration file not found at {config_path}")
        return

    print(f"\nConfiguration: {config_path}")

    # Create MCP Client Manager
    manager = MCPClientManager(str(config_path))

    try:
        # Step 1: Initialize and connect to servers
        print("\n" + "=" * 70)
        print("STEP 1: Initializing MCP Client Manager")
        print("=" * 70)
        await manager.initialize()
        print(f"✓ Successfully connected to {len(manager.servers)} server(s)")

        # Display connected servers
        for server_name in manager.servers.keys():
            print(f"  - {server_name}")

        # Step 2: Discover available tools
        print("\n" + "=" * 70)
        print("STEP 2: Discovering Available Tools")
        print("=" * 70)
        tools = manager.get_all_tools()
        print(f"✓ Discovered {len(tools)} tool(s)\n")

        for tool in tools:
            print(f"Tool: {tool['name']}")
            print(f"  Description: {tool['description']}")
            print(f"  Server: {tool['server']}")
            print(f"  Schema: {tool['schema']}")
            print()

        # Step 3: Invoke tools
        print("=" * 70)
        print("STEP 3: Invoking Tools")
        print("=" * 70)

        # Test 1: Add two numbers
        print("\n[Test 1] Invoking 'add' tool: 15 + 27")
        result = await manager.invoke_tool("add", {"a": 15, "b": 27})
        print(f"✓ Result: {result}")

        # Test 2: Multiply two numbers
        print("\n[Test 2] Invoking 'multiply' tool: 8 × 12")
        result = await manager.invoke_tool("multiply", {"a": 8, "b": 12})
        print(f"✓ Result: {result}")

        # Test 3: Power operation
        print("\n[Test 3] Invoking 'power' tool: 2^10")
        result = await manager.invoke_tool("power", {"base": 2, "exponent": 10})
        print(f"✓ Result: {result}")

        # Test 4: Multiple operations
        print("\n[Test 4] Performing multiple operations")
        operations = [
            ("add", {"a": 100, "b": 200}),
            ("multiply", {"a": 3, "b": 14}),
            ("power", {"base": 5, "exponent": 3}),
        ]

        for tool_name, args in operations:
            result = await manager.invoke_tool(tool_name, args)
            print(f"  {tool_name}{args} = {result}")

        print("\n✓ All tool invocations completed successfully!")

        # Step 4: Test error handling
        print("\n" + "=" * 70)
        print("STEP 4: Testing Error Handling")
        print("=" * 70)

        print("\n[Test] Invoking non-existent tool")
        try:
            await manager.invoke_tool("nonexistent_tool", {})
            print("✗ Should have raised ValueError")
        except ValueError as e:
            print(f"✓ Correctly raised ValueError: {e}")

        print("\n[Test] Invoking with invalid arguments")
        try:
            # Missing required argument 'b'
            await manager.invoke_tool("add", {"a": 5})
            print("✗ Should have raised an error")
        except Exception as e:
            print(f"✓ Correctly raised error: {type(e).__name__}: {e}")

    except Exception as e:
        print(f"\n✗ Error occurred: {type(e).__name__}: {e}")
        import traceback

        traceback.print_exc()

    finally:
        # Step 5: Cleanup
        print("\n" + "=" * 70)
        print("STEP 5: Shutting Down")
        print("=" * 70)
        await manager.shutdown()
        print("✓ MCP Client Manager shutdown complete")

    print("\n" + "=" * 70)
    print("Test Complete!")
    print("=" * 70)


if __name__ == "__main__":
    print("\n")
    print("╔════════════════════════════════════════════════════════════════════╗")
    print("║         MCP Client Manager - Real Server Integration Test         ║")
    print("╚════════════════════════════════════════════════════════════════════╝")
    print()

    asyncio.run(main())
