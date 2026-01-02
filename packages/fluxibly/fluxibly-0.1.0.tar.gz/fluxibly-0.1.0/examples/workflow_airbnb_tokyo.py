"""Airbnb Search Example - Tokyo Accommodation.

This example demonstrates using the Airbnb MCP server to search for
accommodations in Tokyo, Japan for 4 adults from Feb 20-27, 2025.

Requirements:
- Airbnb MCP server enabled in config/mcp_servers.yaml
- Travel assistant profile configured
- OpenAI API key in environment (for orchestrator)
"""

import asyncio

from dotenv import load_dotenv

from fluxibly import WorkflowEngine

# Load environment variables
load_dotenv("local.env")


async def main() -> None:
    """Search for Airbnb accommodations in Tokyo."""
    print("=" * 70)
    print("Airbnb Search - Tokyo Accommodation")
    print("=" * 70)
    print()
    print("Search Criteria:")
    print("  Location: Tokyo, Japan")
    print("  Dates: February 20-27, 2025 (7 nights)")
    print("  Guests: 4 adults")
    print("=" * 70)
    print()

    # Initialize workflow engine with travel assistant profile
    engine = WorkflowEngine.from_profile("travel_assistant")

    try:
        # Initialize MCP connections
        print("Initializing Airbnb MCP server...")
        await engine.initialize()
        print("✓ Connected to Airbnb MCP server")
        print()

        # Search for accommodations
        search_query = (
            "Find Airbnb accommodations in Tokyo, Japan for 4 adults "
            "from February 20 to February 27, 2025. "
            "Show me the top 5 options with prices and key details."
        )

        print(f"Query: {search_query}")
        print()
        print("Searching...")
        print("-" * 70)

        # Execute the search
        response = await engine.execute(search_query)

        print()
        print("Results:")
        print("-" * 70)
        print(response)
        print("-" * 70)

        # Follow-up question to test stateful conversation
        print()
        print("Follow-up Query: Can you show me more details about the first option?")
        print("-" * 70)

        follow_up = await engine.execute("Can you show me more details about the first option?")

        print()
        print("Details:")
        print("-" * 70)
        print(follow_up)
        print("-" * 70)

    except Exception as e:
        print(f"Error: {e}")
        import traceback

        traceback.print_exc()

    finally:
        # Cleanup
        await engine.shutdown()
        print()
        print("=" * 70)
        print("Example complete!")


if __name__ == "__main__":
    asyncio.run(main())
