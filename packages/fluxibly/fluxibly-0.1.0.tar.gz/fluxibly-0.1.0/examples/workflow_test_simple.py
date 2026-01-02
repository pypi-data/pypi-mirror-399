"""Simple workflow test without MCP servers.

This test script verifies the workflow engine works correctly
without needing any MCP servers enabled.
"""

import asyncio

from dotenv import load_dotenv

from fluxibly import WorkflowConfig, WorkflowEngine

# Load environment variables from local.env
load_dotenv("local.env")


async def main() -> None:
    """Run a simple workflow test."""
    print("=" * 70)
    print("Simple Workflow Test (No MCP Servers)")
    print("=" * 70)

    # Use test configuration with no MCP servers
    config = WorkflowConfig(
        name="test_workflow",
        agent_type="agent",
        profile="default",
        mcp_config_path="config/mcp_servers_test.yaml",
        stateful=False,
    )

    engine = WorkflowEngine(config=config)
    try:
        await engine.initialize()
        print("\n[Test 1] Simple question")
        response = await engine.execute("What is the capital of France?")
        print(f"Response: {response}\n")

    finally:
        await engine.shutdown()

    print("=" * 70)
    print("Test complete!")


if __name__ == "__main__":
    asyncio.run(main())
