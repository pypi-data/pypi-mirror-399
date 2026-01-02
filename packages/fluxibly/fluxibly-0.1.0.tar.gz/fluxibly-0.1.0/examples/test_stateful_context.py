"""Test stateful context with Airbnb searches.

This script tests whether follow-up questions correctly reference previous search results.
"""

import asyncio
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from dotenv import load_dotenv

from fluxibly import WorkflowSession

# Load environment variables
load_dotenv("local.env")


async def test_stateful_context():
    """Test stateful conversation with follow-up questions."""
    print("\n" + "=" * 70)
    print("Testing Stateful Context with Airbnb Searches")
    print("=" * 70)

    async with WorkflowSession(profile="travel_assistant") as session:
        # First query - should perform search
        print(
            "\n[Query 1] Find accommodations in Tokyo, Japan for 4 adults from Feb 20-27, 2025. Show me top 3 options with prices."
        )
        print("-" * 70)
        response1 = await session.execute(
            "Find accommodations in Tokyo, Japan for 4 adults from Feb 20-27, 2025. Show me top 3 options with prices."
        )
        print(f"\nResponse 1:\n{response1}\n")

        # Follow-up query 1 - should analyze previous results, NOT search again
        print("\n[Query 2] Which one offers the best value for money?")
        print("-" * 70)
        response2 = await session.execute("Which one offers the best value for money?")
        print(f"\nResponse 2:\n{response2}\n")

        # Follow-up query 2 - should still reference first results
        print("\n[Query 3] What about the location? Which is most convenient for tourists?")
        print("-" * 70)
        response3 = await session.execute("What about the location? Which is most convenient for tourists?")
        print(f"\nResponse 3:\n{response3}\n")

    print("\n" + "=" * 70)
    print("Test complete!")
    print("=" * 70)


if __name__ == "__main__":
    asyncio.run(test_stateful_context())
