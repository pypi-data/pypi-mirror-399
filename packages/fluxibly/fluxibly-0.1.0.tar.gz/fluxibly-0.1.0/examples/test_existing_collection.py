"""Test MCP integration with existing 'documents' collection.

This script tests if we can query your existing collection through
the workflow system, without modifying the collection structure.
"""

import asyncio

from dotenv import load_dotenv

from fluxibly import WorkflowSession

# Load environment variables
load_dotenv("local.env")


async def test_direct_qdrant_query() -> None:
    """Test direct Qdrant query without MCP (baseline test)."""
    print("=" * 70)
    print("Test 1: Direct Qdrant Query (Baseline)")
    print("=" * 70)

    try:
        from qdrant_client import QdrantClient
        from sentence_transformers import SentenceTransformer
    except ImportError:
        print("Error: Required packages not installed.")
        print("Install with: uv add qdrant-client sentence-transformers")
        return

    client = QdrantClient(host="localhost", port=6333)
    model = SentenceTransformer("all-MiniLM-L6-v2")

    # Get collection info
    collection_info = client.get_collection(collection_name="documents")
    print(f"\nCollection 'documents':")
    print(f"  Points: {collection_info.points_count}")
    print(f"  Status: {collection_info.status}")

    # Check vector config
    vectors_config = collection_info.config.params.vectors
    if isinstance(vectors_config, dict):
        print(f"  Type: Named vectors")
        for name in vectors_config.keys():
            print(f"    - {name}")
    else:
        print(f"  Type: Unnamed vector")
        print(f"  Size: {vectors_config.size}")
        print(f"  Distance: {vectors_config.distance}")

    # Try a search query
    print("\n[Search Test] Searching for content...")
    query = "document content"
    query_embedding = model.encode(query).tolist()

    try:
        # Try unnamed vector search
        results = client.search(
            collection_name="documents",
            query_vector=query_embedding,
            limit=3,
        )
        print(f"✓ Found {len(results)} results")

        for i, result in enumerate(results, 1):
            payload = result.payload or {}
            print(f"\n  Result {i} (score: {result.score:.3f}):")
            print(f"    ID: {result.id}")
            if "content" in payload:
                content = payload["content"]
                preview = content[:100] + "..." if len(content) > 100 else content
                print(f"    Content: {preview}")
            else:
                print(f"    Payload keys: {list(payload.keys())}")

    except Exception as e:
        print(f"✗ Search failed: {e}")


async def test_mcp_workflow() -> None:
    """Test querying through MCP workflow."""
    print("\n" + "=" * 70)
    print("Test 2: MCP Workflow Query")
    print("=" * 70)

    print("\n⚠️  Note: This test uses the MCP server configuration from")
    print("   config/mcp_servers.yaml (currently set to 'rag_documents')")
    print("\n   To test with 'documents' collection, we would need to")
    print("   temporarily change COLLECTION_NAME in the config.")

    # Show current config
    try:
        import yaml

        with open("config/mcp_servers.yaml") as f:
            config = yaml.safe_load(f)
            qdrant_config = config.get("mcp_servers", {}).get("qdrant", {})
            collection_name = qdrant_config.get("env", {}).get("COLLECTION_NAME", "unknown")
            print(f"\n   Current MCP config: COLLECTION_NAME='{collection_name}'")
    except Exception:
        pass

    print("\n   Skipping MCP workflow test to avoid errors.")
    print("   (Would fail with unnamed vector error on 'documents' collection)")


async def test_collection_compatibility() -> None:
    """Check if collection is compatible with MCP server."""
    print("\n" + "=" * 70)
    print("Test 3: MCP Server Compatibility Check")
    print("=" * 70)

    try:
        from qdrant_client import QdrantClient
    except ImportError:
        print("Error: qdrant-client not installed.")
        return

    client = QdrantClient(host="localhost", port=6333)
    collection_name = "documents"

    print(f"\nChecking '{collection_name}' compatibility with MCP server...")

    collection_info = client.get_collection(collection_name=collection_name)
    vectors_config = collection_info.config.params.vectors

    # Check 1: Named vs Unnamed vectors
    print("\n[Check 1] Vector naming:")
    if isinstance(vectors_config, dict):
        print("  ✓ Uses named vectors (MCP compatible)")
        expected_name = "fast-all-minilm-l6-v2"
        if expected_name in vectors_config:
            print(f"  ✓ Has expected vector name: '{expected_name}'")
            print("  → Collection IS compatible with MCP server!")
        else:
            print(f"  ⚠️  Vector names: {list(vectors_config.keys())}")
            print(f"  ⚠️  Expected name: '{expected_name}'")
            print("  → May need to adjust EMBEDDING_MODEL in MCP config")
    else:
        print("  ✗ Uses unnamed vector (NOT MCP compatible)")
        print(f"    Vector size: {vectors_config.size}")
        print(f"    Distance: {vectors_config.distance}")
        print("\n  → Collection needs migration to named vectors")
        print("    Run: uv run python examples/migrate_collection_to_named_vectors.py")

    # Check 2: Vector dimensions
    print("\n[Check 2] Vector dimensions:")
    if isinstance(vectors_config, dict):
        for name, config in vectors_config.items():
            print(f"  Vector '{name}': {config.size} dimensions")
    else:
        print(f"  Dimensions: {vectors_config.size}")

    if isinstance(vectors_config, dict):
        sizes = [config.size for config in vectors_config.values()]
        expected_size = 384
    else:
        sizes = [vectors_config.size]
        expected_size = 384

    if all(size == expected_size for size in sizes):
        print(f"  ✓ Matches all-MiniLM-L6-v2 model ({expected_size} dimensions)")
    else:
        print(f"  ⚠️  Expected {expected_size} dimensions for all-MiniLM-L6-v2")

    # Check 3: Point count
    print("\n[Check 3] Data availability:")
    print(f"  Points in collection: {collection_info.points_count}")
    if collection_info.points_count > 0:
        print("  ✓ Collection has data")
    else:
        print("  ⚠️  Collection is empty")

    # Summary
    print("\n" + "=" * 70)
    print("Summary")
    print("=" * 70)

    if isinstance(vectors_config, dict) and "fast-all-minilm-l6-v2" in vectors_config:
        print("\n✅ Your 'documents' collection IS compatible with MCP server!")
        print("\nYou can use it by updating config/mcp_servers.yaml:")
        print("  COLLECTION_NAME: 'documents'")
    else:
        print("\n❌ Your 'documents' collection is NOT compatible with MCP server")
        print("\nOptions:")
        print("  1. Migrate to named vectors (preserves all data):")
        print("     uv run python examples/migrate_collection_to_named_vectors.py")
        print("\n  2. Use separate 'rag_documents' collection (current setup):")
        print("     uv run python examples/setup_qdrant_academic.py")


async def main() -> None:
    """Run all tests."""
    await test_direct_qdrant_query()
    await test_mcp_workflow()
    await test_collection_compatibility()


if __name__ == "__main__":
    asyncio.run(main())
