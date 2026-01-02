"""Test the custom RAG MCP server integration.

This script demonstrates how to use the custom RAG MCP server
that integrates with your existing API endpoints.
"""

import asyncio

from dotenv import load_dotenv

from fluxibly import WorkflowSession

# Load environment variables
load_dotenv("local.env")


async def test_search() -> None:
    """Test semantic search through the custom RAG MCP server."""
    print("=" * 70)
    print("Test 1: Semantic Search via Custom RAG MCP")
    print("=" * 70)

    async with WorkflowSession(profile="rag_assistant") as session:
        # Query 1: Simple search
        print("\n[Query 1] Simple search query")
        query1 = """
        Search the knowledge base for information about "public relations".
        Use the rag-search tool with limit=5.
        """

        try:
            response1 = await session.execute(query1)
            print("\n✓ Search completed")
            print(f"\nResponse:\n{response1}")
        except Exception as e:
            print(f"\n✗ Search failed: {e}")

        # Query 2: Specific search with threshold
        print("\n" + "=" * 70)
        print("[Query 2] Search with custom threshold")
        query2 = """
        Search for documents about "course learning outcomes"
        using rag-search with limit=3 and score_threshold=0.3.
        """

        try:
            response2 = await session.execute(query2)
            print("\n✓ Search completed")
            print(f"\nResponse:\n{response2}")
        except Exception as e:
            print(f"\n✗ Search failed: {e}")


async def test_conversational() -> None:
    """Test conversational queries with context."""
    print("\n" + "=" * 70)
    print("Test 2: Conversational RAG Queries")
    print("=" * 70)

    async with WorkflowSession(profile="rag_assistant") as session:
        # First query
        print("\n[Query 1] Initial question")
        query1 = "What information do we have about public relations courses?"

        response1 = await session.execute(query1)
        print(f"\n✓ Response:\n{response1[:500]}...")

        # Follow-up query (uses context)
        print("\n[Query 2] Follow-up question")
        query2 = "What are the main learning objectives mentioned?"

        response2 = await session.execute(query2)
        print(f"\n✓ Response:\n{response2[:500]}...")


async def test_index_gcs() -> None:
    """Test GCS indexing (optional - requires valid GCS path)."""
    print("\n" + "=" * 70)
    print("Test 3: GCS Indexing (Optional)")
    print("=" * 70)

    # This is an example - modify the GCS path to match your data
    gcs_path = "gs://datanetwork-files-prod/test_data/"

    print(f"\nExample GCS indexing command:")
    print(f"  GCS Path: {gcs_path}")
    print(f"  Recursive: true")

    response = input("\nDo you want to run indexing? (yes/no): ")

    if response.lower() == "yes":
        async with WorkflowSession(profile="rag_assistant") as session:
            query = f"""
            Index documents from Google Cloud Storage using the rag-index-gcs tool.
            GCS path: {gcs_path}
            Recursive: true
            """

            try:
                result = await session.execute(query)
                print(f"\n✓ Indexing completed")
                print(f"\nResult:\n{result}")
            except Exception as e:
                print(f"\n✗ Indexing failed: {e}")
    else:
        print("\nSkipping indexing test")


async def test_multi_hop_reasoning() -> None:
    """Test multi-hop reasoning across multiple searches."""
    print("\n" + "=" * 70)
    print("Test 4: Multi-hop Reasoning")
    print("=" * 70)

    async with WorkflowSession(profile="rag_assistant") as session:
        query = """
        I need comprehensive information about public relations education.

        Please:
        1. Search for information about PR course objectives
        2. Search for information about teaching methods
        3. Search for information about assessment criteria
        4. Synthesize this information to give me a complete overview

        Use multiple rag-search calls with appropriate queries.
        """

        try:
            response = await session.execute(query)
            print("\n✓ Multi-hop reasoning completed")
            print(f"\nResponse:\n{response}")
        except Exception as e:
            print(f"\n✗ Multi-hop reasoning failed: {e}")


async def main() -> None:
    """Run all tests."""
    print("\n🧪 Custom RAG MCP Server Test Suite")
    print("=" * 70)
    print("\nThis test requires:")
    print("  1. RAG API running on http://localhost:8000")
    print("  2. API endpoints /search and /index/gcs available")
    print("  3. OpenAI API key in local.env")
    print("=" * 70)

    proceed = input("\nProceed with tests? (yes/no): ")

    if proceed.lower() != "yes":
        print("\nTests cancelled.")
        return

    # Test 1: Basic search
    await test_search()

    # Test 2: Conversational queries
    await test_conversational()

    # Test 3: Multi-hop reasoning
    await test_multi_hop_reasoning()

    # Test 4: GCS indexing (optional)
    await test_index_gcs()

    print("\n" + "=" * 70)
    print("✓ All tests completed!")
    print("=" * 70)


if __name__ == "__main__":
    asyncio.run(main())
