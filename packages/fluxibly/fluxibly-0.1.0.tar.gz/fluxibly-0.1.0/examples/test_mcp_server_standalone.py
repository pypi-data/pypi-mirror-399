"""Test the custom MCP server directly (without framework)."""

import asyncio
import json
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))


async def test_mcp_tools():
    """Test MCP server tools directly."""
    print("=" * 70)
    print("Testing Custom RAG MCP Server")
    print("=" * 70)

    # Import after adding to path
    from mcp_servers.custom_rag.server import handle_search, handle_index_gcs

    # Test 1: Search
    print("\n[Test 1] rag-search tool")
    print("-" * 70)

    search_args = {"query": "public relations", "limit": 3, "score_threshold": 0.1}

    print(f"Arguments: {json.dumps(search_args, indent=2)}")
    print("\nExecuting search...")

    try:
        results = await handle_search(search_args)
        print("\n✓ Search completed successfully!")
        print(f"\nResults ({len(results)} response(s)):")
        for i, result in enumerate(results, 1):
            print(f"\n--- Response {i} ---")
            print(result.text[:500] + "..." if len(result.text) > 500 else result.text)
    except Exception as e:
        print(f"\n✗ Search failed: {e}")
        import traceback

        traceback.print_exc()

    # Test 2: Index (optional - will fail if path doesn't exist)
    print("\n" + "=" * 70)
    print("[Test 2] rag-index-gcs tool")
    print("-" * 70)

    index_args = {"gcs_path": "gs://test-bucket/test-path/", "recursive": True}

    print(f"Arguments: {json.dumps(index_args, indent=2)}")
    print("\nNote: This will likely fail unless the GCS path exists.")
    print("      This is expected for testing.")

    try:
        results = await handle_index_gcs(index_args)
        print("\n✓ Index request completed!")
        print(f"\nResults ({len(results)} response(s)):")
        for i, result in enumerate(results, 1):
            print(f"\n--- Response {i} ---")
            print(result.text[:500] + "..." if len(result.text) > 500 else result.text)
    except Exception as e:
        print(f"\n⚠️  Index request returned error (expected): {type(e).__name__}")
        print(f"   Message: {e}")

    print("\n" + "=" * 70)
    print("MCP Server Test Complete")
    print("=" * 70)


if __name__ == "__main__":
    asyncio.run(test_mcp_tools())
