"""Batch processing example - multiple tasks.

This example demonstrates batch processing of multiple tasks
with and without state preservation.
"""

import asyncio

from fluxibly import WorkflowEngine, run_batch_workflow


async def main() -> None:
    """Run batch processing examples."""
    print("=" * 70)
    print("Batch Processing Example")
    print("=" * 70)

    # Example 1: Simple batch without state preservation
    print("\n[Example 1] Independent tasks (no state preservation)")
    tasks = [
        "Explain async/await in Python",
        "What are Python decorators?",
        "How does the GIL work?",
    ]

    responses = await run_batch_workflow(tasks, profile="development_assistant", preserve_state=False)

    for i, (task, response) in enumerate(zip(tasks, responses, strict=True), 1):
        print(f"\n{i}. Q: {task}")
        print(f"   A: {response[:100]}...")

    # Example 2: Batch with state preservation (sequential context)
    print("\n\n[Example 2] Sequential tasks (with state preservation)")
    sequential_tasks = [
        "Create a function to calculate fibonacci numbers",
        "Add memoization to improve performance",
        "Add error handling for negative inputs",
    ]

    engine = WorkflowEngine.from_profile("development_assistant")
    try:
        await engine.initialize()

        responses = await engine.execute_batch(
            sequential_tasks,
            preserve_state=True,  # Each task builds on previous
        )

        for i, (task, response) in enumerate(zip(sequential_tasks, responses, strict=True), 1):
            print(f"\n{i}. Q: {task}")
            print(f"   A: {response[:100]}...")

        # Check final state
        history = engine.get_session_history()
        print(f"\n[Final State] Conversation has {len(history)} messages")

    finally:
        await engine.shutdown()

    print("\n" + "=" * 70)
    print("Batch processing complete!")


if __name__ == "__main__":
    asyncio.run(main())
