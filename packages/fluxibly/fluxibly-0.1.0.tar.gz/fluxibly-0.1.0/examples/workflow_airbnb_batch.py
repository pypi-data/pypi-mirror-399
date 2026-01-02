"""Airbnb Batch Search Example - Compare Multiple Destinations.

This example demonstrates batch processing to compare Airbnb accommodations
across multiple cities for the same dates and guest count.

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
    """Compare Airbnb accommodations across multiple cities."""
    print("=" * 70)
    print("Airbnb Batch Search - Compare Multiple Destinations")
    print("=" * 70)
    print()
    print("Search Criteria:")
    print("  Destinations: Tokyo, Osaka, Kyoto")
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

        # Create search queries for multiple cities
        cities = ["Tokyo", "Osaka", "Kyoto"]
        queries = [
            f"Find the best Airbnb accommodation in {city}, Japan for 4 adults "
            f"from February 20 to February 27, 2025. Show top option with price."
            for city in cities
        ]

        print("Searching across multiple cities...")
        print("-" * 70)

        # Execute batch search (stateless mode - each search is independent)
        results = await engine.execute_batch(queries, preserve_state=False)

        # Display results for each city
        for city, result in zip(cities, results):
            print()
            print(f"📍 {city.upper()}")
            print("-" * 70)
            print(result)
            print("-" * 70)

        # Now let's do a comparative analysis with state preservation
        print()
        print()
        print("=" * 70)
        print("Comparative Analysis (Stateful)")
        print("=" * 70)
        print()

        # Clear session for fresh start
        engine.clear_session()

        # First, gather all data
        print("Gathering data for all cities...")
        comparison_query = (
            "Compare Airbnb accommodations for 4 adults from Feb 20-27, 2025 "
            "across Tokyo, Osaka, and Kyoto, Japan. "
            "For each city, show the best option with price and key features."
        )

        comparison_result = await engine.execute(comparison_query)
        print()
        print("Comparison Results:")
        print("-" * 70)
        print(comparison_result)
        print("-" * 70)

        # Follow-up with stateful context
        print()
        print("Follow-up: Which city offers the best value for money?")
        print("-" * 70)

        value_analysis = await engine.execute(
            "Based on the search results, which city offers the best value for money considering price and amenities?"
        )

        print()
        print("Value Analysis:")
        print("-" * 70)
        print(value_analysis)
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
        print("Batch example complete!")


if __name__ == "__main__":
    asyncio.run(main())
