"""Comprehensive diagnostic tool for Qdrant MCP server connection and search.

This script tests the MCP server independently to identify issues.
"""

import asyncio
import os
import subprocess
import sys
from typing import Any

from dotenv import load_dotenv

# Load environment variables
load_dotenv("local.env")


async def test_qdrant_connection() -> bool:
    """Test direct connection to Qdrant server."""
    print("=" * 70)
    print("Test 1: Qdrant Server Connection")
    print("=" * 70)

    try:
        from qdrant_client import QdrantClient
    except ImportError:
        print("✗ qdrant-client not installed")
        print("  Install: uv add qdrant-client")
        return False

    try:
        client = QdrantClient(host="localhost", port=6333)
        collections = client.get_collections()
        print(f"✓ Connected to Qdrant at localhost:6333")
        print(f"✓ Found {len(collections.collections)} collection(s):")
        for col in collections.collections:
            print(f"  - {col.name}")
        return True
    except Exception as e:
        print(f"✗ Failed to connect to Qdrant: {e}")
        print("\nMake sure Qdrant is running:")
        print("  docker run -p 6333:6333 qdrant/qdrant")
        return False


async def test_collection_structure() -> dict[str, Any]:
    """Test the 'documents' collection structure."""
    print("\n" + "=" * 70)
    print("Test 2: Collection 'documents' Structure")
    print("=" * 70)

    try:
        from qdrant_client import QdrantClient
    except ImportError:
        return {}

    client = QdrantClient(host="localhost", port=6333)
    collection_name = "documents"

    try:
        info = client.get_collection(collection_name=collection_name)
        print(f"\n✓ Collection '{collection_name}' exists")
        print(f"  Points: {info.points_count}")
        print(f"  Status: {info.status}")

        vectors_config = info.config.params.vectors

        result = {
            "exists": True,
            "points_count": info.points_count,
            "is_named": isinstance(vectors_config, dict),
        }

        if isinstance(vectors_config, dict):
            print(f"  Vector type: Named vectors")
            for name, config in vectors_config.items():
                print(f"    - '{name}': {config.size}D, {config.distance}")
                result["vector_names"] = list(vectors_config.keys())
                result["vector_size"] = config.size
        else:
            print(f"  Vector type: Unnamed (default)")
            print(f"  Dimensions: {vectors_config.size}")
            print(f"  Distance: {vectors_config.distance}")
            result["vector_size"] = vectors_config.size

        # Sample a point to check structure
        points = client.scroll(collection_name=collection_name, limit=1, with_vectors=True)
        if points[0]:
            sample = points[0][0]
            print(f"\n  Sample point ID: {sample.id}")

            if isinstance(sample.vector, dict):
                print(f"  Sample vector type: Named (dict)")
                for vec_name in sample.vector.keys():
                    print(f"    - '{vec_name}': {len(sample.vector[vec_name])}D")
                result["sample_vector_type"] = "named"
                result["sample_vector_names"] = list(sample.vector.keys())
            else:
                print(f"  Sample vector type: Unnamed (list)")
                print(f"  Sample dimensions: {len(sample.vector)}")
                result["sample_vector_type"] = "unnamed"

            if sample.payload:
                print(f"  Payload keys: {list(sample.payload.keys())}")
                result["payload_keys"] = list(sample.payload.keys())

        return result

    except Exception as e:
        print(f"✗ Error accessing collection: {e}")
        return {"exists": False, "error": str(e)}


async def test_direct_search() -> bool:
    """Test direct search using qdrant-client."""
    print("\n" + "=" * 70)
    print("Test 3: Direct Search (qdrant-client)")
    print("=" * 70)

    try:
        from qdrant_client import QdrantClient
        from sentence_transformers import SentenceTransformer
    except ImportError:
        print("✗ Required packages not installed")
        print("  Install: uv add qdrant-client sentence-transformers")
        return False

    client = QdrantClient(host="localhost", port=6333)
    model = SentenceTransformer("all-MiniLM-L6-v2")

    query = "test search query"
    query_embedding = model.encode(query).tolist()

    print(f"\nQuery: '{query}'")
    print(f"Embedding dimensions: {len(query_embedding)}")

    # Try unnamed vector search
    print("\n[Attempt 1] Searching with unnamed vector...")
    try:
        results = client.search(
            collection_name="documents",
            query_vector=query_embedding,
            limit=3,
        )
        print(f"✓ Success! Found {len(results)} results")
        for i, result in enumerate(results, 1):
            print(f"  {i}. Score: {result.score:.3f}, ID: {result.id}")
        return True
    except Exception as e:
        print(f"✗ Failed: {e}")

    # Try named vector search
    print("\n[Attempt 2] Searching with named vector 'fast-all-minilm-l6-v2'...")
    try:
        results = client.search(
            collection_name="documents",
            query_vector=("fast-all-minilm-l6-v2", query_embedding),
            limit=3,
        )
        print(f"✓ Success! Found {len(results)} results")
        for i, result in enumerate(results, 1):
            print(f"  {i}. Score: {result.score:.3f}, ID: {result.id}")
        return True
    except Exception as e:
        print(f"✗ Failed: {e}")

    return False


async def test_mcp_server_standalone() -> bool:
    """Test MCP server standalone (outside of framework)."""
    print("\n" + "=" * 70)
    print("Test 4: MCP Server Standalone Test")
    print("=" * 70)

    # Check if uvx is available
    try:
        result = subprocess.run(["uvx", "--version"], capture_output=True, text=True, timeout=5)
        print(f"✓ uvx available: {result.stdout.strip()}")
    except Exception as e:
        print(f"✗ uvx not available: {e}")
        return False

    # Set environment variables for MCP server
    env = os.environ.copy()
    env["QDRANT_URL"] = "http://localhost:6333"
    env["COLLECTION_NAME"] = "documents"
    env["EMBEDDING_MODEL"] = "sentence-transformers/all-MiniLM-L6-v2"

    print(f"\nMCP Server configuration:")
    print(f"  QDRANT_URL: {env['QDRANT_URL']}")
    print(f"  COLLECTION_NAME: {env['COLLECTION_NAME']}")
    print(f"  EMBEDDING_MODEL: {env['EMBEDDING_MODEL']}")

    print("\n⚠️  Note: Testing MCP server directly requires MCP protocol interaction")
    print("   This is complex to test standalone. The server expects MCP JSON-RPC.")
    print("\n   Instead, we'll verify the server can be launched:")

    try:
        # Try to launch the server briefly to see if it starts
        print("\n[Launching MCP server for 3 seconds...]")
        proc = subprocess.Popen(
            ["uvx", "mcp-server-qdrant"],
            env=env,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )

        # Wait a bit for it to start
        await asyncio.sleep(3)

        # Terminate it
        proc.terminate()
        try:
            stdout, stderr = proc.communicate(timeout=2)
        except subprocess.TimeoutExpired:
            proc.kill()
            stdout, stderr = proc.communicate()

        if proc.returncode is None or proc.returncode == 0 or "Traceback" not in stderr:
            print("✓ MCP server launched successfully")
            if stdout:
                print(f"\n  Server output:\n{stdout[:500]}")
            return True
        else:
            print(f"✗ MCP server failed to launch")
            if stderr:
                print(f"\n  Error output:\n{stderr[:500]}")
            return False

    except Exception as e:
        print(f"✗ Failed to launch MCP server: {e}")
        return False


async def test_mcp_through_framework() -> bool:
    """Test MCP integration through Fluxibly framework."""
    print("\n" + "=" * 70)
    print("Test 5: MCP Integration Through Framework")
    print("=" * 70)

    try:
        from fluxibly import WorkflowSession
    except ImportError:
        print("✗ Fluxibly not available")
        return False

    print("\n[Attempting simple RAG query through framework...]")

    try:
        async with WorkflowSession(profile="rag_assistant") as session:
            print("✓ Session created")

            # Simple query to test MCP integration
            query = "Search the knowledge base for any information."

            print(f"\nExecuting query: '{query}'")
            response = await session.execute(query)

            print(f"✓ Query executed successfully!")
            print(f"\nResponse preview:")
            print(response[:500] if len(response) > 500 else response)
            return True

    except Exception as e:
        print(f"✗ Framework query failed: {e}")
        print(f"\nError type: {type(e).__name__}")

        # Print full traceback for debugging
        import traceback

        print("\nFull traceback:")
        traceback.print_exc()
        return False


async def generate_diagnostic_report(results: dict[str, Any]) -> None:
    """Generate diagnostic report and recommendations."""
    print("\n" + "=" * 70)
    print("Diagnostic Report & Recommendations")
    print("=" * 70)

    collection_info = results.get("collection_structure", {})

    print("\n[Summary]")
    print(f"  Qdrant connection: {'✓' if results.get('qdrant_connected') else '✗'}")
    print(f"  Collection exists: {'✓' if collection_info.get('exists') else '✗'}")
    print(f"  Direct search works: {'✓' if results.get('direct_search') else '✗'}")
    print(f"  MCP server launches: {'✓' if results.get('mcp_server') else '✗'}")
    print(f"  Framework integration: {'✓' if results.get('framework') else '✗'}")

    if not collection_info.get("exists"):
        print("\n[Issue] Collection 'documents' not found")
        print("  → Create collection or check collection name in config")
        return

    is_named = collection_info.get("is_named", False)
    sample_type = collection_info.get("sample_vector_type")

    print(f"\n[Collection Analysis]")
    print(f"  Points: {collection_info.get('points_count', 0)}")
    print(f"  Vector config type: {'Named' if is_named else 'Unnamed'}")
    print(f"  Sample vector type: {sample_type}")

    if sample_type == "unnamed" and is_named:
        print("\n⚠️  [Warning] Mismatch detected!")
        print("  Collection config says 'named' but sample point is 'unnamed'")

    if sample_type == "unnamed":
        print("\n[Issue] Collection uses UNNAMED vectors")
        print("  MCP server expects NAMED vectors with name 'fast-all-minilm-l6-v2'")
        print("\n  Solutions:")
        print("  1. Migrate existing collection to named vectors:")
        print("     uv run python examples/migrate_collection_to_named_vectors.py")
        print("\n  2. Use a different collection for RAG examples:")
        print("     a. Update config: COLLECTION_NAME='rag_documents'")
        print("     b. Run: uv run python examples/setup_qdrant_academic.py")

    elif sample_type == "named":
        vector_names = collection_info.get("sample_vector_names", [])
        expected = "fast-all-minilm-l6-v2"

        if expected in vector_names:
            print(f"\n✓ Collection has correct named vector: '{expected}'")
            if not results.get("framework"):
                print("\n[Issue] Framework integration failed despite correct setup")
                print("  → Check MCP server logs and framework configuration")
        else:
            print(f"\n[Issue] Collection has named vectors but wrong names")
            print(f"  Expected: '{expected}'")
            print(f"  Found: {vector_names}")
            print("\n  Solution: Update EMBEDDING_MODEL in config to match vector name")

    # Check for other issues
    if collection_info.get("points_count", 0) == 0:
        print("\n[Warning] Collection is empty")
        print("  → Add documents to the collection before querying")

    print("\n[Next Steps]")
    if not results.get("qdrant_connected"):
        print("  1. Start Qdrant: docker run -p 6333:6333 qdrant/qdrant")
    elif sample_type == "unnamed":
        print("  1. Run migration: uv run python examples/migrate_collection_to_named_vectors.py")
        print("  2. Test again: uv run python examples/diagnose_qdrant_mcp.py")
    elif results.get("framework"):
        print("  ✓ All tests passed! Your setup is working correctly.")
    else:
        print("  1. Check error messages above")
        print("  2. Verify MCP server configuration in config/mcp_servers.yaml")
        print("  3. Check OpenAI API key is set in local.env")


async def main() -> None:
    """Run all diagnostic tests."""
    print("\n🔍 Qdrant MCP Server Diagnostic Tool")
    print("=" * 70)

    results: dict[str, Any] = {}

    # Test 1: Qdrant connection
    results["qdrant_connected"] = await test_qdrant_connection()

    if not results["qdrant_connected"]:
        print("\n❌ Cannot proceed without Qdrant connection")
        return

    # Test 2: Collection structure
    results["collection_structure"] = await test_collection_structure()

    if not results["collection_structure"].get("exists"):
        print("\n❌ Cannot proceed without collection 'documents'")
        await generate_diagnostic_report(results)
        return

    # Test 3: Direct search
    results["direct_search"] = await test_direct_search()

    # Test 4: MCP server standalone
    results["mcp_server"] = await test_mcp_server_standalone()

    # Test 5: Framework integration
    results["framework"] = await test_mcp_through_framework()

    # Generate report
    await generate_diagnostic_report(results)


if __name__ == "__main__":
    asyncio.run(main())
