"""Tokyo Airbnb Search - February 20-27, 2025 for 4 Adults.

Exact search as requested:
- Location: Tokyo, Japan
- Dates: February 20-27, 2025 (7 nights)
- Guests: 4 adults

This demonstrates the complete workflow from initialization to results.
"""

import asyncio

from dotenv import load_dotenv

from fluxibly import WorkflowEngine

# Load environment variables
load_dotenv("local.env")


async def main() -> None:
    """Search for Tokyo accommodations matching the exact criteria."""
    print("=" * 70)
    print("Tokyo Airbnb Search")
    print("=" * 70)
    print()
    print("📍 Location: Tokyo, Japan")
    print("📅 Check-in: February 20, 2025")
    print("📅 Check-out: February 27, 2025 (7 nights)")
    print("👥 Guests: 4 adults")
    print("=" * 70)
    print()

    # Initialize workflow engine with travel assistant profile
    engine = WorkflowEngine.from_profile("travel_assistant")

    try:
        # Step 1: Initialize MCP connections
        print("⚙️  Initializing Airbnb MCP server...")
        await engine.initialize()
        print("✓ Connected to Airbnb MCP server")
        print()

        # Step 2: Execute search
        search_query = "Search for Airbnb accommodations in Tokyo, Japan for 4 adults checking in on February 20, 2025 and checking out on February 27, 2025. Show me the top 5 options with price per night, total price, ratings, number of bedrooms/bathrooms, and key amenities."

        print("🔍 Searching for accommodations...")
        print()

        response = await engine.execute(search_query)

        # Display results
        print("📋 Search Results:")
        print("=" * 70)
        print(response)
        print("=" * 70)
        print()

        # Step 3: Follow-up questions
        print("💡 Follow-up Questions:")
        print("-" * 70)

        # Question 1: Most economical option
        print()
        print("Q1: Which option offers the best value for 4 adults?")
        print()

        value_response = await engine.execute(
            "Based on the search results, which accommodation offers the best "
            "value for money considering price, space, and amenities for 4 adults?"
        )

        print("A1:")
        print(value_response)
        print()

        # Question 2: Location details
        print("-" * 70)
        print("Q2: Which option has the best location for first-time visitors?")
        print()

        location_response = await engine.execute(
            "Which listing has the best location for first-time visitors to Tokyo "
            "in terms of access to tourist attractions and public transportation?"
        )

        print("A2:")
        print(location_response)
        print()

        print("=" * 70)
        print("✓ Search complete!")
        print()

        # Print summary
        print("📊 Summary:")
        print("-" * 70)
        print(f"  Total accommodations found: Check results above")
        print(f"  Search duration: 7 nights (Feb 20-27, 2025)")
        print(f"  Guest count: 4 adults")
        print(f"  Profile used: travel_assistant")
        print(f"  Agent type: orchestrator (multi-step planning)")
        print("-" * 70)

    except Exception as e:
        print("❌ Error occurred:")
        print(f"  {e}")
        print()
        import traceback

        traceback.print_exc()

    finally:
        # Cleanup
        print()
        print("🔌 Shutting down MCP connections...")
        await engine.shutdown()
        print("✓ Cleanup complete")
        print()
        print("=" * 70)


if __name__ == "__main__":
    asyncio.run(main())
