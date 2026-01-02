"""Quick test to verify orchestrator is being used correctly."""

import asyncio

from dotenv import load_dotenv

from fluxibly import WorkflowEngine

load_dotenv("local.env")


async def main() -> None:
    """Test that travel_assistant profile creates OrchestratorAgent."""
    print("=" * 70)
    print("Orchestrator Fix Verification")
    print("=" * 70)
    print()

    # Test 1: Verify agent type from profile
    print("[Test 1] Creating engine from travel_assistant profile...")
    engine = WorkflowEngine.from_profile("travel_assistant")

    try:
        await engine.initialize()

        # Check agent type
        agent_type = type(engine.agent).__name__
        print(f"✓ Engine initialized")
        print(f"✓ Agent type: {agent_type}")

        if agent_type == "OrchestratorAgent":
            print("✓ SUCCESS: Orchestrator is being used!")
        else:
            print(f"✗ FAIL: Expected OrchestratorAgent, got {agent_type}")

        # Check MCP tools
        if engine.mcp_manager:
            tools = engine.mcp_manager.get_all_tools()
            airbnb_tools = [t for t in tools if t.get("server") == "airbnb"]
            print(f"✓ Found {len(airbnb_tools)} Airbnb tools")

    finally:
        await engine.shutdown()

    print()
    print("=" * 70)
    print("Test complete!")


if __name__ == "__main__":
    asyncio.run(main())
