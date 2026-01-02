"""Conversational RAG workflow with context persistence.

This example demonstrates multi-turn conversations where the agent
maintains context and performs follow-up retrievals based on the
ongoing conversation.
"""

import asyncio

from dotenv import load_dotenv

from fluxibly import WorkflowSession

# Load environment variables from local.env
load_dotenv("local.env")


async def main() -> None:
    """Run conversational RAG session with follow-ups."""
    print("=" * 70)
    print("Conversational RAG - Multi-turn Context-Aware Retrieval")
    print("=" * 70)

    async with WorkflowSession(profile="rag_assistant") as session:
        # Turn 1: Initial broad query
        print("\n[Turn 1] Initial query - broad topic")
        response1 = await session.execute("What is deep learning? Retrieve relevant documents and explain.")
        print(f"Response: {response1}\n")

        # Turn 2: Follow-up asking for specific details
        print("[Turn 2] Follow-up - specific aspect (uses context from Turn 1)")
        response2 = await session.execute(
            "Tell me more about the training process. Find additional details on backpropagation and optimization."
        )
        print(f"Response: {response2}\n")

        # Turn 3: Drilling down further
        print("[Turn 3] Drilling down - practical application")
        response3 = await session.execute("What are some real-world applications? Search for case studies or examples.")
        print(f"Response: {response3}\n")

        # Turn 4: Related question building on context
        print("[Turn 4] Related question - challenges")
        response4 = await session.execute(
            "What are common challenges in implementing this? Retrieve information about best practices and pitfalls."
        )
        print(f"Response: {response4}\n")

        # Check conversation history
        history = session.get_session_history()
        print(f"\n[Session Summary]")
        print(f"Total conversation turns: {len([m for m in history if m.role == 'user'])}")
        print(f"Total messages (including assistant): {len(history)}")

    print("\n" + "=" * 70)
    print("Conversational RAG session complete!")


if __name__ == "__main__":
    asyncio.run(main())
