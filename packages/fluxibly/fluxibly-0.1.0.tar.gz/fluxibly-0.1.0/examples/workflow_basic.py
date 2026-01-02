"""Basic workflow example - simple one-shot execution.

This example demonstrates the simplest way to use the workflow system
with the convenience function.
"""

import asyncio

from dotenv import load_dotenv

from fluxibly import run_workflow

# Load environment variables from local.env
load_dotenv("local.env")


async def main() -> None:
    """Run a simple one-shot workflow."""
    print("=" * 70)
    print("Basic Workflow Example - One-Shot Execution")
    print("=" * 70)

    # Example 1: Simple question
    print("\n[Example 1] Simple question")
    response = await run_workflow("What is the capital of France?", profile="default")
    print(f"Response: {response}\n")

    # Example 2: With context
    print("[Example 2] With context")
    response = await run_workflow(
        "What's the weather like?",
        profile="default",
        context={"location": "Paris, France"},
    )
    print(f"Response: {response}\n")

    print("=" * 70)
    print("Example complete!")


if __name__ == "__main__":
    asyncio.run(main())
