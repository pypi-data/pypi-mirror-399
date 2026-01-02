"""Workflow configuration models.

This module provides Pydantic models for configuring workflow execution.
"""

from typing import Literal

from pydantic import BaseModel, Field


class WorkflowConfig(BaseModel):
    """Configuration for workflow execution.

    Attributes:
        name: Workflow identifier for logging and tracking
        agent_type: Type of agent to use ("agent" or "orchestrator")
        profile: Name of configuration profile to load
        execution_mode: Execution mode ("single" for one task, "batch" for multiple)
        stateful: Whether to maintain conversation history across calls
        mcp_config_path: Path to MCP servers configuration file
        config_dir: Base configuration directory path

    Example:
        >>> config = WorkflowConfig(
        ...     name="my_workflow",
        ...     agent_type="orchestrator",
        ...     profile="development_assistant",
        ...     stateful=True
        ... )
    """

    name: str = Field(..., description="Workflow identifier")
    agent_type: Literal["agent", "orchestrator"] = Field(default="agent", description="Type of agent to use")
    profile: str = Field(default="default", description="Configuration profile name")
    execution_mode: Literal["single", "batch"] = Field(
        default="single", description="Execution mode: single task or batch processing"
    )
    stateful: bool = Field(default=True, description="Maintain conversation history across calls")
    mcp_config_path: str = Field(default="config/mcp_servers.yaml", description="Path to MCP servers configuration")
    config_dir: str = Field(default="config", description="Configuration directory path")
