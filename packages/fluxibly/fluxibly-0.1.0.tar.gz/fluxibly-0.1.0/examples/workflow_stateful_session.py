"""Stateful session example - conversation with context.

This example demonstrates how to maintain conversation history
across multiple interactions using WorkflowSession.
"""

import asyncio

from fluxibly import WorkflowSession


async def main() -> None:
    """Run a stateful conversation session."""
    print("=" * 70)
    print("Stateful Session Example - Conversation with Context")
    print("=" * 70)

    # Use WorkflowSession context manager for automatic lifecycle management
    async with WorkflowSession(profile="development_assistant") as session:
        print("\n[Turn 1] Initial code analysis")
        response1 = await session.execute("Analyze this Python code: def add(a, b): return a + b")
        print(f"Response: {response1}\n")

        print("[Turn 2] Follow-up (has context from Turn 1)")
        response2 = await session.execute("Add type hints to the function")
        print(f"Response: {response2}\n")

        print("[Turn 3] Another follow-up (has context from Turn 1 and 2)")
        response3 = await session.execute("Now add a comprehensive docstring")
        print(f"Response: {response3}\n")

        # Check conversation history
        history = session.get_session_history()
        print(f"[Session History] Total messages: {len(history)}")
        for i, msg in enumerate(history, 1):
            print(f"  {i}. {msg.role}: {msg.content[:50]}...")

    print("\n" + "=" * 70)
    print("Session complete! (automatically shut down)")


if __name__ == "__main__":
    asyncio.run(main())
