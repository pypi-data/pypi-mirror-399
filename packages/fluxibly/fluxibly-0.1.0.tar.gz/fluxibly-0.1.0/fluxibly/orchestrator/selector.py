"""MCP tool selection module for Orchestrator Agent.

This module handles advanced MCP tool selection using semantic matching
and relevance scoring to determine which tools are most appropriate for a task.
"""

import json
import re
from typing import Any

from loguru import logger

from fluxibly.llm.base import BaseLLM
from fluxibly.orchestrator.config.prompts import get_default_loader


class MCPSelector:
    """Selects and prioritizes MCP tools for task execution.

    The MCPSelector performs advanced MCP tool selection using semantic matching
    and relevance scoring to determine which tools are most appropriate for a task.

    Attributes:
        llm: LLM instance for semantic analysis
        prompt_loader: PromptLoader for template management
    """

    def __init__(self, llm: BaseLLM) -> None:
        """Initialize the MCPSelector.

        Args:
            llm: LLM instance for tool selection analysis
        """
        self.llm = llm
        self.prompt_loader = get_default_loader()
        self._logger = logger.bind(component="MCPSelector")

    def select_mcp_tools(
        self, user_prompt: str, available_mcps: list[str], context: dict[str, Any]
    ) -> list[dict[str, Any]]:
        """Perform advanced MCP selection using semantic matching.

        Analyzes the user's task and selects the most relevant MCP tools based on:
        - Semantic similarity between task and tool capabilities
        - Tool dependencies
        - Priority and relevance scoring
        - Context information about the task

        Args:
            user_prompt: User's task description
            available_mcps: List of available MCP server names
            context: Additional context for selection (e.g., domain, constraints, history)

        Returns:
            List of selected MCP tools with metadata:
                - name: MCP server name
                - priority: Priority level (higher = more important)
                - relevance: Relevance score (0-1)
                - use_case: Intended use for this task
                - dependencies: Other MCP servers this depends on

        Example:
            >>> selector = MCPSelector(llm)
            >>> tools = selector.select_mcp_tools(
            ...     "Analyze PDF document",
            ...     ["ocr", "vision", "text_analysis"],
            ...     {"domain": "finance", "document_type": "invoice"}
            ... )
            >>> # tools = [
            >>> #     {"name": "ocr", "relevance": 0.9, ...},
            >>> #     {"name": "text_analysis", "relevance": 0.7, ...}
            >>> # ]
        """
        if not available_mcps:
            return []

        # Format context for prompt
        context_str = self._format_context(context)

        # Get prompt template with context
        selection_prompt = self.prompt_loader.get_prompt(
            "mcp_selection",
            user_prompt=user_prompt,
            available_mcps=", ".join(available_mcps),
            context=context_str,
        )

        try:
            response = self.llm.forward(selection_prompt)
            # Try to extract JSON from response
            json_match = re.search(r"\[[\s\S]*\]", response)
            if json_match:
                selected_mcps = json.loads(json_match.group(0))
                # Validate structure
                for mcp in selected_mcps:
                    if "name" not in mcp or mcp["name"] not in available_mcps:
                        raise ValueError("Invalid MCP selection format")
                    # Set defaults for missing fields
                    mcp.setdefault("priority", 1)
                    mcp.setdefault("relevance", 1.0)
                    mcp.setdefault("use_case", "General purpose")
                    mcp.setdefault("dependencies", [])

                self._logger.debug(f"Selected {len(selected_mcps)} MCPs via LLM: {[m['name'] for m in selected_mcps]}")
                return selected_mcps
            else:
                raise ValueError("No JSON array found in LLM response")
        except Exception:
            self._logger.exception("Failed to parse MCP selection, falling back to all available MCPs")
            # Fallback: return all available MCPs
            return [
                {"name": mcp, "priority": 1, "relevance": 1.0, "use_case": "General purpose", "dependencies": []}
                for mcp in available_mcps
            ]

    def format_mcp_tools(self, selected_mcps: list[dict[str, Any]]) -> str:
        """Format selected MCP tools for inclusion in system prompt.

        Args:
            selected_mcps: List of selected MCP tool metadata

        Returns:
            Formatted string describing available MCP tools
        """
        if not selected_mcps:
            return "No MCP tools available."

        lines = []
        for mcp in selected_mcps:
            lines.append(f"- {mcp['name']}: {mcp.get('use_case', 'General purpose tool')}")
        return "\n".join(lines)

    def _format_context(self, context: dict[str, Any]) -> str:
        """Format context dictionary for inclusion in prompts.

        Args:
            context: Context dictionary

        Returns:
            Formatted context string
        """
        if not context:
            return "No additional context provided"

        formatted_parts = []
        for key, value in context.items():
            # Skip execution history and other internal keys
            if key in ["execution_history", "selected_mcps", "planning_context", "execution_params"]:
                continue

            if isinstance(value, dict):
                # Format nested dict
                formatted_parts.append(f"{key}:")
                for subkey, subvalue in value.items():
                    formatted_parts.append(f"  - {subkey}: {subvalue}")
            elif isinstance(value, list):
                # Format list
                formatted_parts.append(f"{key}: {', '.join(str(v) for v in value)}")
            else:
                # Format simple value
                formatted_parts.append(f"{key}: {value}")

        return "\n".join(formatted_parts) if formatted_parts else "No additional context provided"
