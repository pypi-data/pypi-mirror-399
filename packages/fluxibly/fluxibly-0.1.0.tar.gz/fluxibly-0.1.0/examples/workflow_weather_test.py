"""Weather workflow test with MCP server.

This example demonstrates using the workflow system with a real MCP server
(weather) to fetch actual weather data.
"""

import asyncio

from dotenv import load_dotenv

from fluxibly import run_workflow

# Load environment variables from local.env
load_dotenv("local.env")


async def main() -> None:
    """Run weather workflow tests."""
    print("=" * 70)
    print("Weather Workflow Test - Using MCP Weather Server")
    print("=" * 70)

    # Test 1: Get weather for Paris
    print("\n[Test 1] Weather for Paris, France")
    response = await run_workflow(
        "What is the current weather in Paris, France? Please provide temperature, conditions, and forecast.",
        profile="default",
    )
    print(f"Response:\n{response}\n")

    # Test 2: Get weather for New York
    print("\n[Test 2] Weather for New York, USA")
    response = await run_workflow(
        "Get me the weather forecast for New York City. Include current conditions and next 24 hours.",
        profile="default",
    )
    print(f"Response:\n{response}\n")

    # Test 3: Weather alerts
    print("\n[Test 3] Check for weather alerts in San Francisco")
    response = await run_workflow(
        "Are there any weather alerts or warnings for San Francisco, California?",
        profile="default",
    )
    print(f"Response:\n{response}\n")

    print("=" * 70)
    print("Weather tests complete!")


if __name__ == "__main__":
    asyncio.run(main())
