"""Inspect existing Qdrant collection to see vector configuration."""

import asyncio

try:
    from qdrant_client import QdrantClient
except ImportError:
    print("Error: qdrant-client not installed.")
    print("Install with: uv add qdrant-client")
    exit(1)


async def inspect_collection(collection_name: str = "documents") -> None:
    """Inspect the existing Qdrant collection structure."""
    print("=" * 70)
    print(f"Inspecting Qdrant Collection: {collection_name}")
    print("=" * 70)

    # Connect to Qdrant
    client = QdrantClient(host="localhost", port=6333)

    try:
        # Get collection info
        print(f"\n[Collection: {collection_name}]")
        collection_info = client.get_collection(collection_name=collection_name)

        print(f"\nPoints count: {collection_info.points_count}")
        print(f"Status: {collection_info.status}")

        # Vector configuration
        print("\nVector Configuration:")
        vectors_config = collection_info.config.params.vectors

        # Check if it's a named vector or unnamed
        if isinstance(vectors_config, dict):
            print("  Type: Named Vectors")
            for vector_name, config in vectors_config.items():
                print(f"  - Vector name: '{vector_name}'")
                print(f"    Size: {config.size}")
                print(f"    Distance: {config.distance}")
        else:
            print("  Type: Unnamed/Default Vector")
            print(f"  Size: {vectors_config.size}")
            print(f"  Distance: {vectors_config.distance}")

        # Sample a point to see its structure
        print("\nSample Point Structure:")
        points = client.scroll(
            collection_name=collection_name,
            limit=1,
            with_payload=True,
            with_vectors=True,
        )

        if points[0]:
            sample_point = points[0][0]
            print(f"  Point ID: {sample_point.id}")

            # Check vector structure
            if isinstance(sample_point.vector, dict):
                print("  Vector type: Named vectors (dict)")
                for vec_name in sample_point.vector.keys():
                    print(f"    - '{vec_name}': {len(sample_point.vector[vec_name])} dimensions")
            else:
                print(f"  Vector type: Unnamed vector (list)")
                print(f"    Dimensions: {len(sample_point.vector)}")

            # Show payload keys
            if sample_point.payload:
                print(f"  Payload keys: {list(sample_point.payload.keys())}")

    except Exception as e:
        print(f"\nError: {e}")
        print("\nMake sure:")
        print("1. Qdrant is running on localhost:6333")
        print("2. Collection 'documents' exists")

    print("\n" + "=" * 70)


async def inspect_all_collections() -> None:
    """Inspect all collections in Qdrant."""
    client = QdrantClient(host="localhost", port=6333)

    # List all collections
    collections = client.get_collections()
    print("\n" + "=" * 70)
    print(f"Found {len(collections.collections)} collection(s) in Qdrant")
    print("=" * 70)

    for collection in collections.collections:
        print(f"\n➤ {collection.name}")
        await inspect_collection(collection.name)
        print()


if __name__ == "__main__":
    import sys

    if len(sys.argv) > 1:
        # Inspect specific collection
        asyncio.run(inspect_collection(sys.argv[1]))
    else:
        # Inspect all collections
        asyncio.run(inspect_all_collections())
