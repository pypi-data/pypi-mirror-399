"""Basic RAG workflow example using Qdrant MCP.

This example demonstrates simple question-answering with semantic retrieval
from a Qdrant vector database.
"""

import asyncio

from dotenv import load_dotenv

from fluxibly import WorkflowSession

# Load environment variables from local.env
load_dotenv("local.env")


async def main() -> None:
    """Run basic RAG queries."""
    print("=" * 70)
    print("Basic RAG Example - Question Answering with Retrieval")
    print("=" * 70)

    # Use RAG profile with Qdrant MCP
    async with WorkflowSession(profile="rag_assistant") as session:
        # Example 1: Simple factual query
        print("\n[Query 1] Simple factual retrieval")
        response1 = await session.execute(
            "What are the key concepts in machine learning? "
            "Search the knowledge base and provide a comprehensive overview."
        )
        print(f"Response: {response1}\n")

        # Example 2: Specific information lookup
        print("[Query 2] Specific information lookup")
        response2 = await session.execute(
            "Find information about neural network architectures. Include specific examples and use cases."
        )
        print(f"Response: {response2}\n")

        # Example 3: Comparative analysis
        print("[Query 3] Comparative analysis")
        response3 = await session.execute(
            "Compare supervised and unsupervised learning approaches. "
            "Retrieve relevant documents and synthesize the key differences."
        )
        print(f"Response: {response3}\n")

    print("=" * 70)
    print("RAG workflow complete!")


if __name__ == "__main__":
    asyncio.run(main())
