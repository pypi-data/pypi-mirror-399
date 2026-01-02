"""Quick test script to verify Airbnb MCP server integration.

This script tests:
1. MCP server connection
2. Tool discovery
3. Basic search functionality
"""

import asyncio

from dotenv import load_dotenv

from fluxibly import WorkflowConfig, WorkflowEngine

# Load environment variables
load_dotenv("local.env")


async def main() -> None:
    """Test Airbnb MCP server integration."""
    print("=" * 70)
    print("Airbnb MCP Server Integration Test")
    print("=" * 70)
    print()

    # Create config with travel assistant profile
    config = WorkflowConfig(
        name="airbnb_test",
        agent_type="orchestrator",
        profile="travel_assistant",
        stateful=False,
    )

    engine = WorkflowEngine(config=config)

    try:
        # Test 1: Connection
        print("[Test 1] Connecting to Airbnb MCP server...")
        await engine.initialize()
        print("✓ Successfully connected to Airbnb MCP server")
        print()

        # Test 2: Tool Discovery
        print("[Test 2] Discovering available tools...")
        if engine.mcp_client_manager:
            tools = engine.mcp_client_manager.get_all_tools()
            airbnb_tools = [t for t in tools if t.get("server") == "airbnb"]

            if airbnb_tools:
                print(f"✓ Found {len(airbnb_tools)} Airbnb tools:")
                for tool in airbnb_tools:
                    tool_name = tool.get("name", "unknown")
                    tool_desc = tool.get("description", "No description")
                    print(f"  - {tool_name}: {tool_desc}")
            else:
                print("✗ No Airbnb tools found")
                return
        else:
            print("✗ MCP client manager not available")
            return
        print()

        # Test 3: Simple Search
        print("[Test 3] Testing search functionality...")
        print("Query: Find accommodation in Tokyo for 2 adults, Feb 20-27, 2025")
        print()

        response = await engine.execute(
            "Find one Airbnb accommodation in Tokyo, Japan for 2 adults "
            "from February 20 to February 27, 2025. Just show me one option."
        )

        print("Response:")
        print("-" * 70)
        print(response)
        print("-" * 70)
        print()

        print("✓ All tests passed!")

    except Exception as e:
        print(f"✗ Test failed: {e}")
        import traceback

        traceback.print_exc()

    finally:
        await engine.shutdown()
        print()
        print("=" * 70)
        print("Test complete!")


if __name__ == "__main__":
    asyncio.run(main())
