"""Weather workflow test using OrchestratorAgent.

This example demonstrates using the OrchestratorAgent which has better
tool execution capabilities compared to the base Agent.
"""

import asyncio

from dotenv import load_dotenv

from fluxibly import WorkflowConfig, WorkflowEngine

# Load environment variables from local.env
load_dotenv("local.env")


async def main() -> None:
    """Run weather workflow tests with OrchestratorAgent."""
    print("=" * 70)
    print("Weather Test - Using OrchestratorAgent with MCP Tools")
    print("=" * 70)

    # Use OrchestratorAgent for better tool execution
    config = WorkflowConfig(
        name="weather_workflow",
        agent_type="orchestrator",  # Use orchestrator instead of agent
        profile="default",
        stateful=False,
    )

    engine = WorkflowEngine(config=config)

    try:
        await engine.initialize()

        # Test 1: Get weather for Paris
        print("\n[Test 1] Weather for Paris, France")
        response = await engine.execute(
            "What is the current weather in Paris, France? Please provide temperature, conditions, and forecast."
        )
        print(f"Response:\n{response}\n")

        # Test 2: Get weather for New York
        print("\n[Test 2] Weather for New York, USA")
        response = await engine.execute(
            "Get me the weather forecast for New York City. Include current conditions and next 24 hours."
        )
        print(f"Response:\n{response}\n")

        # Test 3: Weather alerts
        print("\n[Test 3] Check for weather alerts in San Francisco")
        response = await engine.execute("Are there any weather alerts or warnings for San Francisco, California?")
        print(f"Response:\n{response}\n")

    finally:
        await engine.shutdown()

    print("=" * 70)
    print("Weather tests complete!")


if __name__ == "__main__":
    asyncio.run(main())
