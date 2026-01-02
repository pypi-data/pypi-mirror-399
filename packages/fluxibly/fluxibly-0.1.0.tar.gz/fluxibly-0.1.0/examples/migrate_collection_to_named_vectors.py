"""Migrate existing Qdrant collection from unnamed to named vectors.

This script converts an existing collection with unnamed vectors to use
named vectors compatible with the Qdrant MCP server.

IMPORTANT: This creates a backup of your data before migration.
"""

import asyncio
from typing import Any

try:
    from qdrant_client import QdrantClient
    from qdrant_client.models import Distance, PointStruct, VectorParams
except ImportError:
    print("Error: qdrant-client not installed.")
    print("Install with: uv add qdrant-client")
    exit(1)


async def migrate_collection(
    source_collection: str = "documents",
    backup_collection: str = "documents_backup",
    vector_name: str = "fast-all-minilm-l6-v2",
) -> None:
    """Migrate collection from unnamed to named vectors.

    Args:
        source_collection: Name of collection to migrate
        backup_collection: Name for backup collection
        vector_name: Name for the new named vector
    """
    print("=" * 70)
    print("Qdrant Collection Migration: Unnamed → Named Vectors")
    print("=" * 70)

    client = QdrantClient(host="localhost", port=6333)

    try:
        # Step 1: Get source collection info
        print(f"\n[Step 1] Inspecting source collection '{source_collection}'...")
        source_info = client.get_collection(collection_name=source_collection)

        print(f"  Points count: {source_info.points_count}")
        print(f"  Status: {source_info.status}")

        # Check if already using named vectors
        vectors_config = source_info.config.params.vectors
        if isinstance(vectors_config, dict):
            print("\n⚠️  Collection already uses named vectors!")
            print("  Vector names:", list(vectors_config.keys()))
            print("\n  No migration needed.")
            return

        # Get vector dimensions
        vector_size = vectors_config.size
        vector_distance = vectors_config.distance
        print(f"  Vector config: size={vector_size}, distance={vector_distance}")

        # Step 2: Create backup
        print(f"\n[Step 2] Creating backup collection '{backup_collection}'...")
        try:
            client.delete_collection(collection_name=backup_collection)
            print(f"  Deleted existing backup")
        except Exception:
            pass

        # Create backup with same unnamed vector config
        client.create_collection(
            collection_name=backup_collection,
            vectors_config=VectorParams(size=vector_size, distance=vector_distance),
        )
        print(f"  ✓ Created backup collection")

        # Step 3: Copy all points to backup
        print(f"\n[Step 3] Copying {source_info.points_count} points to backup...")

        # Scroll through all points
        offset = None
        total_copied = 0

        while True:
            points, next_offset = client.scroll(
                collection_name=source_collection,
                limit=100,
                offset=offset,
                with_payload=True,
                with_vectors=True,
            )

            if not points:
                break

            # Upload to backup
            client.upsert(collection_name=backup_collection, points=points)
            total_copied += len(points)
            print(f"  Copied {total_copied} points...", end="\r")

            offset = next_offset
            if offset is None:
                break

        print(f"\n  ✓ Backed up {total_copied} points")

        # Step 4: Create new collection with named vectors
        print(f"\n[Step 4] Recreating '{source_collection}' with named vectors...")

        # Delete old collection
        client.delete_collection(collection_name=source_collection)
        print(f"  Deleted old collection")

        # Create with named vectors
        client.create_collection(
            collection_name=source_collection,
            vectors_config={vector_name: VectorParams(size=vector_size, distance=vector_distance)},
        )
        print(f"  ✓ Created new collection with vector '{vector_name}'")

        # Step 5: Migrate points with named vectors
        print(f"\n[Step 5] Migrating {total_copied} points with named vectors...")

        offset = None
        total_migrated = 0

        while True:
            points, next_offset = client.scroll(
                collection_name=backup_collection,
                limit=100,
                offset=offset,
                with_payload=True,
                with_vectors=True,
            )

            if not points:
                break

            # Convert to named vectors
            migrated_points: list[PointStruct] = []
            for point in points:
                migrated_point = PointStruct(
                    id=point.id,
                    vector={vector_name: point.vector},  # Wrap in dict with vector name
                    payload=point.payload,
                )
                migrated_points.append(migrated_point)

            # Upload to new collection
            client.upsert(collection_name=source_collection, points=migrated_points)
            total_migrated += len(migrated_points)
            print(f"  Migrated {total_migrated} points...", end="\r")

            offset = next_offset
            if offset is None:
                break

        print(f"\n  ✓ Migrated {total_migrated} points")

        # Step 6: Verify migration
        print(f"\n[Step 6] Verifying migration...")
        new_info = client.get_collection(collection_name=source_collection)

        print(f"  New collection points: {new_info.points_count}")
        print(f"  Original points: {source_info.points_count}")

        if new_info.points_count == source_info.points_count:
            print("  ✓ Point count matches!")
        else:
            print("  ⚠️  Point count mismatch!")

        # Check vector structure
        vectors_config = new_info.config.params.vectors
        if isinstance(vectors_config, dict) and vector_name in vectors_config:
            print(f"  ✓ Named vector '{vector_name}' confirmed")
        else:
            print("  ⚠️  Named vector not found!")

        # Sample a point
        sample_points = client.scroll(collection_name=source_collection, limit=1, with_vectors=True)
        if sample_points[0]:
            sample = sample_points[0][0]
            if isinstance(sample.vector, dict) and vector_name in sample.vector:
                print(f"  ✓ Sample point has named vector")
            else:
                print("  ⚠️  Sample point vector structure unexpected!")

        print("\n" + "=" * 70)
        print("Migration Complete!")
        print("=" * 70)
        print(f"\n✅ Collection '{source_collection}' now uses named vectors")
        print(f"✅ Backup saved in '{backup_collection}'")
        print(f"\nVector configuration:")
        print(f"  Name: {vector_name}")
        print(f"  Size: {vector_size}")
        print(f"  Distance: {vector_distance}")
        print(f"\nNext steps:")
        print(f"1. Test your workflows with the migrated collection")
        print(f"2. If everything works, you can delete the backup:")
        print(f"   client.delete_collection('{backup_collection}')")
        print(f"3. Update MCP server config to use COLLECTION_NAME: '{source_collection}'")

    except Exception as e:
        print(f"\n❌ Error during migration: {e}")
        print("\nYour original data should be safe in the backup collection.")
        print(f"To restore: rename '{backup_collection}' back to '{source_collection}'")
        raise


async def main() -> None:
    """Main migration workflow."""
    import sys

    source = "documents"
    backup = "documents_backup"
    vector_name = "fast-all-minilm-l6-v2"

    # Parse command line arguments
    if len(sys.argv) > 1:
        source = sys.argv[1]
    if len(sys.argv) > 2:
        backup = sys.argv[2]
    if len(sys.argv) > 3:
        vector_name = sys.argv[3]

    print(f"\nMigration settings:")
    print(f"  Source collection: {source}")
    print(f"  Backup collection: {backup}")
    print(f"  Vector name: {vector_name}")

    # Confirm before proceeding
    print("\n⚠️  This will recreate the source collection with named vectors.")
    print("   A backup will be created first to preserve your data.")
    response = input("\nProceed with migration? (yes/no): ")

    if response.lower() != "yes":
        print("\nMigration cancelled.")
        return

    await migrate_collection(source, backup, vector_name)


if __name__ == "__main__":
    asyncio.run(main())
