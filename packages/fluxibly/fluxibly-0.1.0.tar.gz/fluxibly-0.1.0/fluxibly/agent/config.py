"""Configuration models for agents.

This module defines the configuration structures for agent initialization.
"""

from typing import Any

from pydantic import BaseModel, Field

from fluxibly.llm.base import LLMConfig


class AgentConfig(BaseModel):
    """Configuration for Agent initialization.

    All parameters can be loaded from config files (YAML/JSON).

    Attributes:
        name: Agent name/identifier for logging and tracking
        llm: LLM configuration (model, temperature, etc.)
        system_prompt: Instructions defining agent behavior and capabilities
        mcp_servers: List of MCP server names/IDs this agent can use
        max_mcp_calls: Maximum number of MCP tool calls per forward() execution
        mcp_selection_strategy: Strategy for selecting MCPs ("all", "auto", "none")
        enable_parallel_mcp: Whether to execute multiple MCP calls in parallel
        mcp_timeout: Timeout for individual MCP tool calls in seconds
        context_window: Maximum context length to maintain in prompt
        enable_memory: Whether to maintain conversation history
        metadata: Additional agent-specific configuration
    """

    name: str = Field(..., description="Agent name/identifier")
    llm: LLMConfig = Field(..., description="LLM configuration")
    system_prompt: str = Field(
        default="You are a helpful AI assistant with access to tools.",
        description="System prompt defining agent behavior",
    )
    mcp_servers: list[str] = Field(
        default_factory=list, description="List of MCP server names/IDs available to this agent"
    )
    max_mcp_calls: int = Field(default=5, description="Maximum MCP tool calls per execution")
    mcp_selection_strategy: str = Field(
        default="auto",
        description="MCP selection strategy: 'all' (provide all), 'auto' (basic selection), 'none' (no tools)",
    )
    enable_parallel_mcp: bool = Field(default=False, description="Enable parallel MCP execution")
    mcp_timeout: int = Field(default=30, description="MCP tool call timeout in seconds")
    context_window: int | None = Field(default=None, description="Maximum context length")
    enable_memory: bool = Field(default=True, description="Maintain conversation history")
    metadata: dict[str, Any] = Field(default_factory=dict, description="Additional agent configuration")
