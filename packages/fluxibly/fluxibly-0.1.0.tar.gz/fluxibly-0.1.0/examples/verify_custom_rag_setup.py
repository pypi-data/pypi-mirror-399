"""Verify custom RAG MCP server setup.

Quick diagnostic to check if everything is configured correctly.
"""

import asyncio
import os
import sys


async def check_dependencies() -> bool:
    """Check if required packages are installed."""
    print("=" * 70)
    print("Check 1: Dependencies")
    print("=" * 70)

    try:
        import httpx
        import mcp

        print("✓ httpx installed:", httpx.__version__)
        print("✓ mcp installed")
        return True
    except ImportError as e:
        print(f"✗ Missing dependency: {e}")
        print("\nInstall with:")
        print("  uv add mcp httpx")
        return False


async def check_mcp_server() -> bool:
    """Check if custom MCP server can be imported."""
    print("\n" + "=" * 70)
    print("Check 2: Custom MCP Server")
    print("=" * 70)

    try:
        # Add mcp_servers to path if needed
        import sys
        from pathlib import Path

        project_root = Path(__file__).parent.parent
        sys.path.insert(0, str(project_root))

        from mcp_servers.custom_rag import server

        print("✓ Custom MCP server module found")
        print(f"  Location: {server.__file__}")
        return True
    except ImportError as e:
        print(f"✗ Cannot import MCP server: {e}")
        print("\nMake sure mcp_servers/custom_rag/server.py exists")
        return False


async def check_api_connection() -> bool:
    """Check if RAG API is accessible."""
    print("\n" + "=" * 70)
    print("Check 3: RAG API Connection")
    print("=" * 70)

    api_url = os.getenv("RAG_API_URL", "http://localhost:8000")
    print(f"API URL: {api_url}")

    try:
        import httpx

        async with httpx.AsyncClient(timeout=5.0) as client:
            # Try to connect to the search endpoint
            try:
                response = await client.post(
                    f"{api_url}/search",
                    json={"query": "test", "limit": 1, "score_threshold": 0.0},
                )
                print(f"✓ API accessible: {response.status_code}")
                return True
            except httpx.ConnectError:
                print(f"✗ Cannot connect to API at {api_url}")
                print("\nMake sure your RAG API is running:")
                print("  - Check if the API server is started")
                print("  - Verify the port (default: 8000)")
                return False
    except Exception as e:
        print(f"✗ Error testing API: {e}")
        return False


async def check_configuration() -> bool:
    """Check MCP server configuration."""
    print("\n" + "=" * 70)
    print("Check 4: Configuration Files")
    print("=" * 70)

    from pathlib import Path

    project_root = Path(__file__).parent.parent

    # Check mcp_servers.yaml
    mcp_config_file = project_root / "config" / "mcp_servers.yaml"
    if mcp_config_file.exists():
        print(f"✓ MCP config found: {mcp_config_file}")

        with open(mcp_config_file) as f:
            content = f.read()
            if "custom_rag:" in content:
                print("  ✓ custom_rag server configured")
                if "enabled: true" in content.split("custom_rag:")[1].split("\n\n")[0]:
                    print("  ✓ custom_rag enabled")
                else:
                    print("  ⚠️  custom_rag may not be enabled")
                    print("     Set 'enabled: true' under custom_rag")
            else:
                print("  ✗ custom_rag not found in config")
                return False
    else:
        print(f"✗ MCP config not found: {mcp_config_file}")
        return False

    # Check rag_assistant.yaml
    rag_profile = project_root / "config" / "profiles" / "rag_assistant.yaml"
    if rag_profile.exists():
        print(f"✓ RAG profile found: {rag_profile}")

        with open(rag_profile) as f:
            content = f.read()
            if "custom_rag" in content:
                print("  ✓ Profile uses custom_rag")
            else:
                print("  ⚠️  Profile may not use custom_rag")
                print("     Check 'enabled_servers' includes custom_rag")
    else:
        print(f"✗ RAG profile not found: {rag_profile}")
        return False

    return True


async def check_environment() -> bool:
    """Check environment variables."""
    print("\n" + "=" * 70)
    print("Check 5: Environment Variables")
    print("=" * 70)

    openai_key = os.getenv("OPENAI_API_KEY")
    if openai_key:
        print("✓ OPENAI_API_KEY is set")
    else:
        print("⚠️  OPENAI_API_KEY not found")
        print("   Make sure it's in local.env file")

    rag_api_url = os.getenv("RAG_API_URL", "http://localhost:8000")
    print(f"✓ RAG_API_URL: {rag_api_url}")

    return True


async def run_simple_test() -> bool:
    """Run a simple end-to-end test."""
    print("\n" + "=" * 70)
    print("Check 6: End-to-End Test")
    print("=" * 70)

    try:
        from dotenv import load_dotenv

        from fluxibly import WorkflowSession

        load_dotenv("local.env")

        print("Attempting simple workflow execution...")

        async with WorkflowSession(profile="rag_assistant") as session:
            # Very simple query to test MCP integration
            response = await session.execute("Use rag-search to search for 'test' with limit=1")

            print("✓ Workflow executed successfully!")
            print(f"\nResponse preview:")
            print(response[:200] + "..." if len(response) > 200 else response)
            return True

    except Exception as e:
        print(f"✗ Workflow test failed: {e}")
        import traceback

        print("\nError details:")
        traceback.print_exc()
        return False


async def main() -> None:
    """Run all checks."""
    print("\n🔍 Custom RAG MCP Server Setup Verification")
    print("=" * 70)

    results = {
        "Dependencies": await check_dependencies(),
        "MCP Server Module": await check_mcp_server(),
        "API Connection": await check_api_connection(),
        "Configuration": await check_configuration(),
        "Environment": await check_environment(),
    }

    # Summary
    print("\n" + "=" * 70)
    print("Summary")
    print("=" * 70)

    all_passed = all(results.values())

    for check, passed in results.items():
        status = "✓" if passed else "✗"
        print(f"{status} {check}")

    if all_passed:
        print("\n✅ All checks passed! Ready to test.")
        print("\nRun the end-to-end test? (yes/no): ", end="")
        response = input()

        if response.lower() == "yes":
            await run_simple_test()
    else:
        print("\n❌ Some checks failed. Fix the issues above before proceeding.")

    print("\n" + "=" * 70)
    print("Next Steps:")
    if all_passed:
        print("  ✓ Run: uv run python examples/test_custom_rag_mcp.py")
        print("  ✓ Check: CUSTOM_RAG_MCP_SETUP.md for usage examples")
    else:
        print("  1. Fix the failed checks above")
        print("  2. Run this script again to verify")
        print("  3. See CUSTOM_RAG_MCP_SETUP.md for detailed setup instructions")


if __name__ == "__main__":
    asyncio.run(main())
