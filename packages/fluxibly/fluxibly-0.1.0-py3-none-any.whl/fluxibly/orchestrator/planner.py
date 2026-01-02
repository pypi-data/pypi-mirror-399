"""Task planning module for Orchestrator Agent.

This module handles task analysis and execution plan generation for the
OrchestratorAgent.
"""

import json
import re
from typing import Any

from loguru import logger

from fluxibly.llm.base import BaseLLM
from fluxibly.orchestrator.config.prompts import get_default_loader


class TaskPlanner:
    """Handles task analysis and plan generation for orchestration.

    The TaskPlanner analyzes user tasks to understand requirements and generates
    detailed execution plans with steps, dependencies, and tool assignments.

    Attributes:
        llm: LLM instance for plan generation
        prompt_loader: PromptLoader for template management
        mcp_servers: List of available MCP server names
    """

    def __init__(self, llm: BaseLLM, mcp_servers: list[str], mcp_client_manager: Any = None) -> None:
        """Initialize the TaskPlanner.

        Args:
            llm: LLM instance for generating plans
            mcp_servers: List of available MCP server names
            mcp_client_manager: Optional MCP client manager for accessing tool information
        """
        self.llm = llm
        self.mcp_servers = mcp_servers
        self.mcp_client_manager = mcp_client_manager
        self.prompt_loader = get_default_loader()
        self._logger = logger.bind(component="TaskPlanner")

    def analyze_task(self, user_prompt: str, context: dict[str, Any] | None = None) -> dict[str, Any]:
        """Analyze user task to identify requirements and capabilities needed.

        This method performs deep analysis of the user's request to understand:
        - What is the user trying to accomplish?
        - What capabilities/tools are needed?
        - What is the optimal execution strategy?
        - What are the dependencies between steps?

        Args:
            user_prompt: The user's task/request
            context: Optional context for analysis

        Returns:
            dict[str, Any]: Task analysis containing:
                - objectives: List of task objectives
                - required_capabilities: Needed tool capabilities
                - complexity: Task complexity assessment
                - suggested_strategy: Recommended execution approach
                - dependencies: Identified dependencies between steps
                - user_prompt: Original user prompt
                - context: Original context

        Example:
            >>> planner = TaskPlanner(llm, ["ocr", "translation"])
            >>> analysis = planner.analyze_task("Extract text from PDF and translate to Spanish")
            >>> # analysis = {
            >>> #     "objectives": ["extract_text", "translate"],
            >>> #     "required_capabilities": ["ocr", "translation"],
            >>> #     "dependencies": {"translate": ["extract_text"]}
            >>> # }
        """
        context = context or {}

        # Format conversation history if available
        history_text = ""
        if "conversation_history" in context and context["conversation_history"]:
            history_text = self._format_conversation_history(context["conversation_history"])
            if history_text:
                self._logger.debug(f"Using conversation history:\n{history_text}")

        # Get prompt template
        analysis_prompt = self.prompt_loader.get_prompt(
            "task_analysis",
            user_prompt=user_prompt,
            context=context if context else "None provided",
            conversation_history=history_text if history_text else "No previous conversation",
        )

        try:
            analysis_response = self.llm.forward(analysis_prompt)
            # Try to parse structured analysis from LLM response
            json_match = re.search(r"\{[\s\S]*\}", analysis_response)
            if json_match:
                parsed_analysis = json.loads(json_match.group(0))
                # Merge with defaults
                analysis = {
                    "objectives": parsed_analysis.get("objectives", ["complete_user_task"]),
                    "required_capabilities": parsed_analysis.get("required_capabilities", self.mcp_servers),
                    "complexity": parsed_analysis.get("complexity", "medium"),
                    "suggested_strategy": parsed_analysis.get("suggested_strategy", "sequential_execution"),
                    "dependencies": parsed_analysis.get("dependencies", {}),
                    "user_prompt": user_prompt,
                    "context": context,
                }
                self._logger.debug(
                    f"Task analysis completed: {analysis['complexity']} complexity, "
                    f"{len(analysis['objectives'])} objectives"
                )
                return analysis
            else:
                # No JSON found, return basic structure
                self._logger.warning("No JSON found in analysis response, using basic structure")
                return self._get_default_analysis(user_prompt, context)
        except Exception:
            self._logger.exception("Failed to parse task analysis")
            return self._get_default_analysis(user_prompt, context)

    def _get_available_tools_info(self) -> str:
        """Get formatted information about available MCP tools including schemas.

        Returns:
            str: Formatted string with tool names, descriptions, and parameter schemas
        """
        if not self.mcp_client_manager:
            return "No tools available"

        tools = []
        tool_list = self.mcp_client_manager.get_all_tools()  # Returns list of tool dicts
        for tool_info in tool_list:
            tool_name = tool_info.get("name", "unknown")
            description = tool_info.get("description", "No description")
            schema = tool_info.get("schema", {})

            # Format schema information
            tool_str = f"\n### {tool_name}\n"
            tool_str += f"Description: {description}\n"

            # Extract required and optional parameters from schema
            properties = schema.get("properties", {})
            required = schema.get("required", [])

            if properties:
                tool_str += "\nParameters:\n"
                for param_name, param_info in properties.items():
                    param_type = param_info.get("type", "unknown")
                    param_desc = param_info.get("description", "")
                    is_required = param_name in required
                    req_marker = " (REQUIRED)" if is_required else " (optional)"

                    tool_str += f"  - {param_name} ({param_type}){req_marker}: {param_desc}\n"

                    # Add constraints if present
                    if "minimum" in param_info and "maximum" in param_info:
                        tool_str += f"    Range: {param_info['minimum']} to {param_info['maximum']}\n"
                    if "enum" in param_info:
                        tool_str += f"    Options: {', '.join(map(str, param_info['enum']))}\n"
                    if "default" in param_info:
                        tool_str += f"    Default: {param_info['default']}\n"

            tools.append(tool_str)

        return "\n".join(tools) if tools else "No tools available"

    def generate_plan(
        self, task_analysis: dict[str, Any], context: dict[str, Any] | None = None
    ) -> list[dict[str, Any]]:
        """Generate detailed execution plan from task analysis.

        Creates a structured plan with:
        - Ordered steps for execution
        - MCP tool assignments for each step
        - Parallel execution opportunities
        - Dependencies and prerequisites

        Args:
            task_analysis: Output from analyze_task()
            context: Optional context dictionary with conversation_history

        Returns:
            list[dict[str, Any]]: Execution plan where each step contains:
                - step_id: Unique identifier
                - description: What this step does
                - tool: MCP tool to use (or None)
                - tool_args: Arguments for the tool
                - dependencies: List of prerequisite step_ids
                - parallel_group: ID for parallel execution grouping

        Example:
            >>> plan = planner.generate_plan(task_analysis)
            >>> # plan = [
            >>> #     {"step_id": 1, "tool": "get_current_conditions", "dependencies": []},
            >>> #     {"step_id": 2, "tool": "get_forecast", "dependencies": [1]}
            >>> # ]
        """
        context = context or {}
        user_prompt = task_analysis.get("user_prompt", "")

        # Get actual available MCP tools instead of abstract capabilities
        available_tools_info = self._get_available_tools_info()

        # Format conversation history if available
        history_text = ""
        if "conversation_history" in context and context["conversation_history"]:
            history_text = self._format_conversation_history(context["conversation_history"])
            if history_text:
                self._logger.debug(f"Using conversation history for plan generation:\n{history_text}")

        # Get prompt template
        planning_prompt = self.prompt_loader.get_prompt(
            "plan_generation",
            user_prompt=user_prompt,
            available_tools=available_tools_info,
            task_analysis=str(task_analysis),
            conversation_history=history_text if history_text else "No previous conversation",
        )

        try:
            plan_response = self.llm.forward(planning_prompt)
            # Try to parse plan from LLM response
            json_match = re.search(r"\[[\s\S]*\]", plan_response)
            if json_match:
                parsed_plan = json.loads(json_match.group(0))
                # Validate and normalize plan structure
                normalized_plan = self._normalize_plan(parsed_plan)

                if normalized_plan:
                    self._logger.info(f"Generated plan with {len(normalized_plan)} steps")
                    # Log each step for visibility
                    for i, step in enumerate(normalized_plan, 1):
                        step_desc = step.get("description", "No description")
                        step_tool = step.get("tool", "No tool")
                        self._logger.info(f"  Step {i}: {step_desc} [Tool: {step_tool}]")
                    return normalized_plan
                else:
                    # Empty plan [] - intentional (for follow-up questions)
                    self._logger.debug("Generated empty plan (no tools needed for follow-up question)")
                    return []
            else:
                raise ValueError("No JSON array found in plan response")
        except json.JSONDecodeError:
            self._logger.exception("Failed to parse plan JSON, using fallback single-step plan")
            return self._get_fallback_plan(user_prompt)
        except ValueError as e:
            if "No JSON array found" in str(e):
                self._logger.exception("No JSON array in plan response, using fallback")
                return self._get_fallback_plan(user_prompt)
            raise

    def refine_plan(
        self, current_plan: list[dict[str, Any]], execution_results: dict[str, Any]
    ) -> list[dict[str, Any]] | None:
        """Refine the execution plan based on results.

        Analyzes execution results to determine if plan needs adjustment:
        - Were objectives met?
        - Did any steps fail or produce unexpected results?
        - Should we add, remove, or modify steps?

        Args:
            current_plan: The plan that was just executed
            execution_results: Results from plan execution

        Returns:
            list[dict[str, Any]]: Refined execution plan, or None if task is complete

        Note:
            Returns None if no refinement needed (task complete).
        """
        # Check if task is complete
        if execution_results.get("task_complete", False):
            return None

        # Check if there were errors
        errors = execution_results.get("errors", [])
        if not errors:
            # No errors, task is complete
            return None

        # Get prompt template
        refinement_prompt = self.prompt_loader.get_prompt(
            "plan_refinement",
            current_plan=str(current_plan),
            execution_results=str(execution_results),
            errors=str(errors),
        )

        try:
            refinement_response = self.llm.forward(refinement_prompt)
            # Try to parse refined plan from LLM response
            json_match = re.search(r"\[[\s\S]*\]", refinement_response)
            if json_match:
                parsed_plan = json.loads(json_match.group(0))
                # Validate and normalize plan structure
                normalized_plan = self._normalize_plan(parsed_plan)

                if normalized_plan:
                    self._logger.info(f"Refined plan with {len(normalized_plan)} steps")
                    # Log each step for visibility
                    for i, step in enumerate(normalized_plan, 1):
                        step_desc = step.get("description", "No description")
                        step_tool = step.get("tool", "No tool")
                        self._logger.info(f"  Step {i}: {step_desc} [Tool: {step_tool}]")
                    return normalized_plan
                else:
                    # Empty plan means task is complete
                    return None
            else:
                # No JSON found, assume task is complete
                self._logger.debug("No refined plan found in response, assuming task complete")
                return None
        except Exception:
            self._logger.exception("Failed to parse refined plan")
            # If refinement fails, return None to complete the task
            return None

    def _normalize_plan(self, parsed_plan: list[dict[str, Any]]) -> list[dict[str, Any]]:
        """Normalize and validate plan structure.

        Args:
            parsed_plan: Raw plan from LLM

        Returns:
            Normalized plan with validated structure
        """
        normalized_plan = []
        for step in parsed_plan:
            if not isinstance(step, dict) or "step_id" not in step:
                continue
            normalized_step = {
                "step_id": step.get("step_id"),
                "description": step.get("description", f"Step {step.get('step_id')}"),
                "tool": step.get("tool"),
                "tool_args": step.get("tool_args", {}),
                "dependencies": step.get("dependencies", []),
                "parallel_group": step.get("parallel_group", 0),
            }
            normalized_plan.append(normalized_step)
        return normalized_plan

    def _get_default_analysis(self, user_prompt: str, context: dict[str, Any]) -> dict[str, Any]:
        """Get default task analysis structure.

        Args:
            user_prompt: User's task
            context: Context dictionary

        Returns:
            Default analysis structure
        """
        return {
            "objectives": ["complete_user_task"],
            "required_capabilities": self.mcp_servers,
            "complexity": "medium",
            "suggested_strategy": "sequential_execution",
            "dependencies": {},
            "user_prompt": user_prompt,
            "context": context,
        }

    def _get_fallback_plan(self, user_prompt: str) -> list[dict[str, Any]]:
        """Get fallback single-step plan.

        Args:
            user_prompt: User's task

        Returns:
            Single-step fallback plan
        """
        return [
            {
                "step_id": 1,
                "description": f"Execute task: {user_prompt}",
                "tool": None,
                "tool_args": {},
                "dependencies": [],
                "parallel_group": 0,
            }
        ]

    def _format_conversation_history(self, history) -> str:
        """Format conversation history for inclusion in prompts.

        Args:
            history: ConversationHistory object or list of Message objects

        Returns:
            str: Formatted conversation history as text
        """
        if not history:
            return ""

        # Get messages list from ConversationHistory object if needed
        if hasattr(history, "get_messages"):
            messages = history.get_messages()
        else:
            messages = history

        if not messages:
            return ""

        formatted = []
        # Get last 6 messages (3 exchanges) to avoid context overflow
        recent_messages = messages[-6:] if len(messages) > 6 else messages

        for msg in recent_messages:
            role = msg.role if hasattr(msg, "role") else "unknown"
            content = msg.content if hasattr(msg, "content") else str(msg)

            # Truncate long messages
            if len(content) > 500:
                content = content[:500] + "..."

            formatted.append(f"{role.upper()}: {content}")

        return "\n".join(formatted)
