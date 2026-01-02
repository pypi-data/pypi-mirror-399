"""Direct API test to diagnose the connection issue."""

import asyncio


async def test_api():
    """Test the API directly with detailed error info."""
    try:
        import httpx
    except ImportError:
        print("Installing httpx...")
        import subprocess

        subprocess.run(["uv", "add", "httpx"])
        import httpx

    api_url = "http://localhost:8000"

    print(f"Testing API at: {api_url}")
    print("=" * 70)

    # Test 1: Basic connectivity
    print("\n[Test 1] Basic connectivity test...")
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(f"{api_url}/")
            print(f"✓ Root endpoint: {response.status_code}")
            print(f"  Response: {response.text[:200]}")
    except Exception as e:
        print(f"✗ Root endpoint failed: {type(e).__name__}: {e}")

    # Test 2: Search endpoint
    print("\n[Test 2] Search endpoint test...")
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.post(
                f"{api_url}/search",
                json={"query": "public relations", "limit": 5, "score_threshold": 0.1},
                headers={"Content-Type": "application/json"},
            )
            print(f"✓ Search endpoint: {response.status_code}")
            print(f"  Response length: {len(response.text)} bytes")

            if response.status_code == 200:
                result = response.json()
                print(f"  Result type: {type(result)}")
                if isinstance(result, dict):
                    print(f"  Keys: {list(result.keys())}")
                elif isinstance(result, list):
                    print(f"  Items: {len(result)}")
                print(f"  Sample: {str(result)[:300]}")
            else:
                print(f"  Error response: {response.text[:500]}")

    except Exception as e:
        print(f"✗ Search endpoint failed: {type(e).__name__}")
        print(f"  Error: {e}")
        import traceback

        traceback.print_exc()

    # Test 3: Index endpoint
    print("\n[Test 3] Index endpoint test...")
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.post(
                f"{api_url}/index/gcs",
                json={"gcs_path": "gs://test/", "recursive": True},
                headers={"Content-Type": "application/json"},
            )
            print(f"  Index endpoint: {response.status_code}")
            print(f"  Response: {response.text[:200]}")
    except Exception as e:
        print(f"  Index endpoint: {type(e).__name__}: {e}")

    print("\n" + "=" * 70)
    print("API test complete")


if __name__ == "__main__":
    asyncio.run(test_api())
