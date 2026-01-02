"""Fluxibly - MCP-Native Agentic Framework.

A modular, extensible agentic framework built on LangGraph with an MCP-native approach.
"""

from typing import Any

__version__ = "0.1.0"

from fluxibly.mcp_client.manager import MCPClientManager
from fluxibly.orchestrator.agent import OrchestratorAgent
from fluxibly.workflow import WorkflowConfig, WorkflowEngine, WorkflowSession

__all__ = [
    "MCPClientManager",
    "OrchestratorAgent",
    "WorkflowEngine",
    "WorkflowConfig",
    "WorkflowSession",
    "run_workflow",
    "run_batch_workflow",
]


# Convenience functions for simple workflow execution


async def run_workflow(
    prompt: str,
    profile: str = "default",
    context: dict[str, Any] | None = None,
) -> str:
    """Run a single task with specified profile.

    Convenience function that handles initialization and cleanup automatically.

    Args:
        prompt: User input/task
        profile: Configuration profile name
        context: Optional execution context

    Returns:
        Agent response

    Example:
        >>> import asyncio
        >>> from fluxibly import run_workflow
        >>>
        >>> async def main():
        ...     response = await run_workflow(
        ...         "What is the capital of France?",
        ...         profile="development_assistant"
        ...     )
        ...     print(response)
        >>>
        >>> asyncio.run(main())
    """
    engine = WorkflowEngine.from_profile(profile)
    try:
        await engine.initialize()
        return await engine.execute(prompt, context)
    finally:
        await engine.shutdown()


async def run_batch_workflow(
    prompts: list[str],
    profile: str = "default",
    contexts: list[dict[str, Any]] | None = None,
    preserve_state: bool = False,
) -> list[str]:
    """Run multiple tasks with specified profile.

    Convenience function for batch processing with automatic lifecycle management.

    Args:
        prompts: List of user inputs/tasks
        profile: Configuration profile name
        contexts: Optional list of contexts (one per prompt)
        preserve_state: Whether to preserve conversation state across tasks

    Returns:
        List of responses (one per prompt)

    Example:
        >>> import asyncio
        >>> from fluxibly import run_batch_workflow
        >>>
        >>> async def main():
        ...     tasks = [
        ...         "Explain async/await in Python",
        ...         "What are Python decorators?",
        ...         "How does the GIL work?"
        ...     ]
        ...     responses = await run_batch_workflow(
        ...         tasks,
        ...         profile="development_assistant"
        ...     )
        ...     for task, response in zip(tasks, responses):
        ...         print(f"Q: {task}")
        ...         print(f"A: {response}\n")
        >>>
        >>> asyncio.run(main())
    """
    engine = WorkflowEngine.from_profile(profile)
    try:
        await engine.initialize()
        return await engine.execute_batch(prompts, contexts, preserve_state)
    finally:
        await engine.shutdown()
