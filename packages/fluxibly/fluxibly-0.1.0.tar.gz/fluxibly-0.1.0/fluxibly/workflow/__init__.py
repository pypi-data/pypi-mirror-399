"""Workflow orchestration package.

This package provides high-level workflow orchestration for agent execution
with MCP tool integration.

Main classes:
    - WorkflowEngine: Main orchestration engine
    - WorkflowConfig: Configuration model
    - WorkflowSession: Context manager for sessions

Convenience functions:
    - run_workflow: Execute a single task
    - run_batch_workflow: Execute multiple tasks
"""

from fluxibly.workflow.config import WorkflowConfig
from fluxibly.workflow.engine import WorkflowEngine, WorkflowSession

__all__ = ["WorkflowConfig", "WorkflowEngine", "WorkflowSession"]
