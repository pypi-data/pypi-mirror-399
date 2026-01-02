"""Test profile loading by name and by path.

This example demonstrates both ways to load configuration profiles:
1. By profile name (searches in config/profiles/)
2. By file path (absolute or relative)
"""

import asyncio
from pathlib import Path

from dotenv import load_dotenv

from fluxibly import WorkflowEngine, run_workflow

# Load environment variables
load_dotenv("local.env")


async def test_profile_by_name() -> None:
    """Test loading profile by name."""
    print("\n" + "=" * 70)
    print("Test 1: Load Profile by Name")
    print("=" * 70)

    # Load built-in profile by name
    engine = WorkflowEngine.from_profile("default")
    try:
        await engine.initialize()
        print("✓ Successfully loaded 'default' profile by name")

        response = await engine.execute("What is 2+2?")
        print(f"Response: {response}\n")
    finally:
        await engine.shutdown()


async def test_profile_by_relative_path() -> None:
    """Test loading profile by relative path."""
    print("\n" + "=" * 70)
    print("Test 2: Load Profile by Relative Path")
    print("=" * 70)

    # Load profile using relative path
    profile_path = "config/profiles/default.yaml"
    engine = WorkflowEngine.from_profile(profile_path)
    try:
        await engine.initialize()
        print(f"✓ Successfully loaded profile from: {profile_path}")

        response = await engine.execute("What is the capital of Japan?")
        print(f"Response: {response}\n")
    finally:
        await engine.shutdown()


async def test_profile_by_absolute_path() -> None:
    """Test loading profile by absolute path."""
    print("\n" + "=" * 70)
    print("Test 3: Load Profile by Absolute Path")
    print("=" * 70)

    # Get absolute path to profile
    current_dir = Path.cwd()
    profile_path = (current_dir / "config" / "profiles" / "default.yaml").absolute()

    engine = WorkflowEngine.from_profile(str(profile_path))
    try:
        await engine.initialize()
        print(f"✓ Successfully loaded profile from: {profile_path}")

        response = await engine.execute("What is 10 * 5?")
        print(f"Response: {response}\n")
    finally:
        await engine.shutdown()


async def test_convenience_function_with_path() -> None:
    """Test using convenience function with path."""
    print("\n" + "=" * 70)
    print("Test 4: Convenience Function with Path")
    print("=" * 70)

    # Use convenience function with file path
    profile_path = "config/profiles/default.yaml"
    response = await run_workflow(
        "What is the square root of 16?",
        profile=profile_path,
    )
    print(f"✓ Successfully used run_workflow with path: {profile_path}")
    print(f"Response: {response}\n")


async def main() -> None:
    """Run all profile loading tests."""
    print("\n" + "=" * 70)
    print("Profile Loading Tests")
    print("=" * 70)
    print("\nTesting different ways to load configuration profiles...")

    try:
        # Test 1: Load by name
        await test_profile_by_name()

        # Test 2: Load by relative path
        await test_profile_by_relative_path()

        # Test 3: Load by absolute path
        await test_profile_by_absolute_path()

        # Test 4: Convenience function with path
        await test_convenience_function_with_path()

        print("=" * 70)
        print("✓ All tests completed successfully!")
        print("=" * 70)

    except Exception as e:
        print(f"\n✗ Test failed with error: {e}")
        raise


if __name__ == "__main__":
    asyncio.run(main())
