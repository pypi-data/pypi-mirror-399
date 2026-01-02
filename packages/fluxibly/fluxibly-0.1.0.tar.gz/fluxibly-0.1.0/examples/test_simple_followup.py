"""Simple test for follow-up questions."""

import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from dotenv import load_dotenv

from fluxibly import WorkflowSession

load_dotenv("local.env")


async def test_simple_followup():
    """Test a single follow-up question."""
    print("\n" + "=" * 70)
    print("Simple Follow-up Test")
    print("=" * 70)

    async with WorkflowSession(profile="travel_assistant") as session:
        # First query
        print("\n[Query 1] Initial search")
        print("-" * 70)
        response1 = await session.execute("Find 2 Tokyo accommodations for 4 adults, Feb 20-27, 2025")
        print(f"\nResponse 1:\n{response1}\n")

        # Follow-up - should analyze previous results
        print("\n[Query 2] Follow-up - which is cheaper?")
        print("-" * 70)
        response2 = await session.execute("Which one is cheaper?")
        print(f"\nResponse 2:\n{response2}\n")

    print("\n" + "=" * 70)
    print("Test complete!")
    print("=" * 70)


if __name__ == "__main__":
    asyncio.run(test_simple_followup())
