"""Advanced workflow example - custom configuration.

This example demonstrates advanced usage with custom WorkflowConfig,
different agent types, and manual lifecycle management.
"""

import asyncio

from fluxibly import WorkflowConfig, WorkflowEngine


async def main() -> None:
    """Run advanced workflow examples."""
    print("=" * 70)
    print("Advanced Workflow Example - Custom Configuration")
    print("=" * 70)

    # Example 1: Custom config with basic Agent
    print("\n[Example 1] Custom config with basic Agent")
    config1 = WorkflowConfig(
        name="simple_workflow",
        agent_type="agent",  # Use basic Agent
        profile="default",
        stateful=False,  # Stateless execution
    )

    engine1 = WorkflowEngine(config=config1)
    try:
        await engine1.initialize()
        print(f"Engine: {engine1}")

        response = await engine1.execute("What is 2 + 2?")
        print(f"Response: {response}")

    finally:
        await engine1.shutdown()

    # Example 2: Custom config with OrchestratorAgent
    print("\n\n[Example 2] Custom config with OrchestratorAgent")
    config2 = WorkflowConfig(
        name="complex_workflow",
        agent_type="orchestrator",  # Use OrchestratorAgent
        profile="document_processing",
        execution_mode="batch",
        stateful=True,
    )

    engine2 = WorkflowEngine(config=config2)
    try:
        await engine2.initialize()
        print(f"Engine: {engine2}")

        # Simulate document processing task
        response = await engine2.execute(
            "Extract and summarize key information",
            context={"document_type": "invoice", "format": "PDF"},
        )
        print(f"Response: {response[:100]}...")

    finally:
        await engine2.shutdown()

    # Example 3: Using from_profile factory method
    print("\n\n[Example 3] Using from_profile factory method")
    engine3 = WorkflowEngine.from_profile("development_assistant")

    try:
        await engine3.initialize()
        print(f"Engine: {engine3}")

        # Get conversation history
        history_before = engine3.get_session_history()
        print(f"History before: {len(history_before)} messages")

        response = await engine3.execute("Write a hello world function in Python")
        print(f"Response: {response[:100]}...")

        history_after = engine3.get_session_history()
        print(f"History after: {len(history_after)} messages")

        # Clear session
        engine3.clear_session()
        history_cleared = engine3.get_session_history()
        print(f"History after clear: {len(history_cleared)} messages")

    finally:
        await engine3.shutdown()

    print("\n" + "=" * 70)
    print("Advanced examples complete!")


if __name__ == "__main__":
    asyncio.run(main())
