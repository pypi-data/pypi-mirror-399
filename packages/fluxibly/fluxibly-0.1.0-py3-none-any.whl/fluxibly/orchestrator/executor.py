"""Plan execution module for Orchestrator Agent.

This module handles execution of generated plans, including step execution,
dependency management, and error handling.
"""

from typing import TYPE_CHECKING, Any

from loguru import logger

from fluxibly.llm.base import BaseLLM
from fluxibly.orchestrator.config.prompts import get_default_loader

if TYPE_CHECKING:
    from fluxibly.mcp_client.manager import MCPClientManager


class PlanExecutor:
    """Executes orchestration plans with dependency management and error handling.

    The PlanExecutor takes a generated plan and executes each step in order,
    respecting dependencies and handling errors according to the configured strategy.

    Attributes:
        llm: LLM instance for non-tool step execution
        mcp_client_manager: Manager for MCP tool invocations
        prompt_loader: PromptLoader for template management
    """

    def __init__(self, llm: BaseLLM, mcp_client_manager: "MCPClientManager | None" = None) -> None:
        """Initialize the PlanExecutor.

        Args:
            llm: LLM instance for executing non-tool steps
            mcp_client_manager: Optional MCP client manager for tool invocations
        """
        self.llm = llm
        self.mcp_client_manager = mcp_client_manager
        self.prompt_loader = get_default_loader()
        self._logger = logger.bind(component="PlanExecutor")

    async def execute_plan(self, plan: list[dict[str, Any]], context: dict[str, Any] | None = None) -> dict[str, Any]:
        """Execute the plan and collect results from each step.

        Executes plan steps in order, respecting dependencies and leveraging
        parallel execution where possible.

        Args:
            plan: Execution plan from TaskPlanner
            context: Optional execution context

        Returns:
            dict[str, Any]: Execution results containing:
                - step_results: Results from each step
                - errors: Any errors encountered
                - task_complete: Whether all steps completed successfully
                - plan: The executed plan
                - context: Execution context

        Example:
            >>> executor = PlanExecutor(llm, mcp_manager)
            >>> results = await executor.execute_plan(plan)
            >>> # results = {
            >>> #     "step_results": {1: {...}, 2: {...}},
            >>> #     "errors": [],
            >>> #     "task_complete": True
            >>> # }
        """
        context = context or {}
        step_results = {}
        errors = []

        # Execute each step in the plan
        for step in plan:
            step_id = step["step_id"]
            description = step["description"]
            tool_name = step.get("tool")
            tool_args = step.get("tool_args", {})

            try:
                # Check if dependencies are satisfied
                dependencies = step.get("dependencies", [])
                for dep_id in dependencies:
                    if dep_id not in step_results:
                        raise ValueError(f"Dependency {dep_id} not satisfied for step {step_id}")

                # Execute the step
                if tool_name:
                    # Resolve parameter placeholders from previous step results
                    resolved_args = self._resolve_parameters(tool_args, step_results, dependencies)
                    # Use MCP tool if specified
                    result = await self._invoke_mcp_tool(tool_name, resolved_args)
                else:
                    # Execute with LLM
                    result = self._execute_llm_step(description, step_results, context)

                step_results[step_id] = {"description": description, "result": result, "status": "success"}
                self._logger.debug(f"Step {step_id} completed successfully")

            except Exception as e:
                self._logger.exception(f"Step {step_id} failed")
                errors.append({"step_id": step_id, "error": str(e), "description": description})
                step_results[step_id] = {
                    "description": description,
                    "result": None,
                    "status": "failed",
                    "error": str(e),
                }

        # Determine if task is complete
        task_complete = len(errors) == 0 and len(step_results) == len(plan)

        return {
            "step_results": step_results,
            "errors": errors,
            "task_complete": task_complete,
            "plan": plan,
            "context": context,
        }

    def _resolve_parameters(
        self, tool_args: dict[str, Any], step_results: dict[int, Any], dependencies: list[int]
    ) -> dict[str, Any]:
        """Resolve parameter placeholders from previous step results.

        Handles placeholders like:
        - "<result_from_step_1>" - gets entire result from step 1
        - "<result_from_step_1.latitude>" - gets specific field from step 1 result
        - Actual values are passed through unchanged

        Args:
            tool_args: Tool arguments that may contain placeholders
            step_results: Results from previous steps
            dependencies: List of step IDs this step depends on

        Returns:
            dict[str, Any]: Resolved tool arguments with actual values
        """
        resolved = {}

        for key, value in tool_args.items():
            if isinstance(value, str) and value.startswith("<result_from_step_"):
                # Extract step ID from placeholder
                import re

                match = re.match(r"<result_from_step_(\d+)(?:\.(\w+))?>", value)
                if match:
                    step_id = int(match.group(1))
                    field = match.group(2) if match.group(2) else None

                    if step_id not in step_results:
                        self._logger.warning(f"Step {step_id} not in results, cannot resolve parameter {key}")
                        resolved[key] = value  # Keep placeholder
                        continue

                    result = step_results[step_id].get("result")

                    # Extract latitude/longitude from MCP search_location result
                    # MCP result format: CallToolResult object with content array
                    result_text = None
                    if hasattr(result, "content") and result.content:
                        # Get first content item
                        first_content = result.content[0] if result.content else None
                        if hasattr(first_content, "text"):
                            result_text = first_content.text
                            self._logger.debug(f"Extracted text from CallToolResult for {key}")
                    elif isinstance(result, dict):
                        # Fallback for dict format
                        content = result.get("content", [])
                        if content and isinstance(content, list):
                            first_content = content[0]
                            if isinstance(first_content, dict) and "text" in first_content:
                                result_text = first_content["text"]
                                self._logger.debug(f"Extracted text from dict for {key}")

                    # Try to parse coordinates from result text
                    # Use explicit field from placeholder OR auto-detect from parameter name
                    target_field = field if field else key  # If no field in placeholder, use param name

                    if result_text:
                        self._logger.debug(f"Attempting to extract {target_field} from text (field={field}, key={key})")
                        if target_field == "latitude":
                            lat_match = re.search(r"[Ll]atitude[:\s]+(-?\d+\.?\d*)", result_text)
                            if lat_match:
                                lat_value = float(lat_match.group(1))
                                self._logger.info(f"Successfully extracted latitude: {lat_value}")
                                resolved[key] = lat_value
                                continue
                            else:
                                self._logger.warning(f"Failed to extract latitude from text: {result_text[:200]}")
                        elif target_field == "longitude":
                            lon_match = re.search(r"[Ll]ongitude[:\s]+(-?\d+\.?\d*)", result_text)
                            if lon_match:
                                lon_value = float(lon_match.group(1))
                                self._logger.info(f"Successfully extracted longitude: {lon_value}")
                                resolved[key] = lon_value
                                continue
                            else:
                                self._logger.warning(f"Failed to extract longitude from text: {result_text[:200]}")

                    # Fallback: if field specified, try to get it from result dict
                    if field and isinstance(result, dict):
                        resolved[key] = result.get(field, value)
                    else:
                        # No extraction successful, use raw result
                        resolved[key] = result
                else:
                    self._logger.warning(f"Could not parse placeholder: {value}")
                    resolved[key] = value
            else:
                # Not a placeholder, use as-is
                resolved[key] = value

        self._logger.debug(f"Resolved parameters: {resolved}")
        return resolved

    def _execute_llm_step(self, description: str, step_results: dict[int, Any], context: dict[str, Any]) -> str:
        """Execute a step using LLM (for non-tool steps).

        Args:
            description: Step description
            step_results: Results from previous steps
            context: Execution context

        Returns:
            LLM response for the step
        """
        execution_prompt = self.prompt_loader.get_prompt(
            "step_execution", description=description, step_results=str(step_results), context=str(context)
        )

        return self.llm.forward(execution_prompt)

    async def _invoke_mcp_tool(self, tool_name: str, tool_args: dict[str, Any]) -> Any:
        """Internal method to invoke a single MCP tool.

        Args:
            tool_name: Name of the MCP tool to invoke
            tool_args: Arguments to pass to the tool

        Returns:
            Tool execution result

        Raises:
            RuntimeError: If MCP client manager is not available
        """
        if not self.mcp_client_manager:
            self._logger.warning("No MCP client manager available, skipping tool invocation")
            return None

        try:
            self._logger.debug(f"Invoking MCP tool '{tool_name}' with args: {tool_args}")
            result = await self.mcp_client_manager.invoke_tool(tool_name, tool_args)
            self._logger.debug("Tool invocation successful")
            return result
        except Exception:
            self._logger.exception("MCP tool invocation failed")
            raise


class ErrorRecoveryHandler:
    """Handles errors and implements recovery strategies.

    The ErrorRecoveryHandler processes execution errors and determines
    the appropriate recovery action based on the configured strategy.

    Attributes:
        llm: LLM instance for fallback planning
        error_recovery_strategy: Strategy to use for error recovery
        prompt_loader: PromptLoader for template management
    """

    def __init__(self, llm: BaseLLM, error_recovery_strategy: str = "retry_with_fallback") -> None:
        """Initialize the ErrorRecoveryHandler.

        Args:
            llm: LLM instance for generating fallback plans
            error_recovery_strategy: Strategy for error recovery
                Options: "retry_with_fallback", "retry", "skip", "abort", "fallback"
        """
        self.llm = llm
        self.error_recovery_strategy = error_recovery_strategy
        self.prompt_loader = get_default_loader()
        self._logger = logger.bind(component="ErrorRecoveryHandler")

    def handle_error(self, error: Exception, context: dict[str, Any] | None = None) -> dict[str, Any]:
        """Handle errors and attempt recovery based on error recovery strategy.

        Args:
            error: Exception that occurred
            context: Error context (which step, what inputs, etc.)

        Returns:
            dict[str, Any]: Recovery action containing:
                - action: "retry", "skip", "abort", "fallback"
                - modified_plan: Adjusted plan if applicable
                - error: Error information
                - retry_count: Current retry count if applicable

        Example:
            >>> handler = ErrorRecoveryHandler(llm, "retry_with_fallback")
            >>> recovery = handler.handle_error(
            ...     error=ConnectionError("OCR server timeout"),
            ...     context={"step_id": 1}
            ... )
            >>> # recovery = {"action": "retry", "retry_count": 1}
        """
        context = context or {}
        strategy = self.error_recovery_strategy

        # Log the error
        error_info = {
            "error_type": type(error).__name__,
            "error_message": str(error),
            "context": context,
            "strategy": strategy,
        }

        if strategy == "abort":
            # Stop execution immediately
            return {"action": "abort", "error": error_info}

        elif strategy == "skip":
            # Skip the failed step and continue
            return {"action": "skip", "error": error_info}

        elif strategy == "retry":
            # Retry the operation
            return self._handle_retry(error_info, context)

        elif strategy == "fallback":
            # Use LLM to generate a fallback plan
            return self._handle_fallback(error, error_info, context)

        elif strategy == "retry_with_fallback":
            # Try retry first, then fallback if retries exhausted
            retry_count = context.get("retry_count", 0)
            max_retries = self.prompt_loader.get_max_retries()

            if retry_count < max_retries:
                return self._handle_retry(error_info, context)
            else:
                # Retries exhausted, try fallback
                return self._handle_fallback(error, error_info, context)

        else:
            # Unknown strategy, default to abort
            self._logger.warning(f"Unknown error recovery strategy: {strategy}, aborting")
            return {"action": "abort", "error": error_info}

    def _handle_retry(self, error_info: dict[str, Any], context: dict[str, Any]) -> dict[str, Any]:
        """Handle retry recovery action.

        Args:
            error_info: Error information
            context: Error context

        Returns:
            Retry recovery action
        """
        retry_count = context.get("retry_count", 0)
        max_retries = self.prompt_loader.get_max_retries()

        if retry_count >= max_retries:
            # Max retries exceeded, abort
            self._logger.warning(f"Max retries ({max_retries}) exceeded, aborting")
            return {"action": "abort", "error": error_info, "retry_count": retry_count}

        self._logger.info(f"Retrying operation (attempt {retry_count + 1}/{max_retries})")
        return {"action": "retry", "error": error_info, "retry_count": retry_count + 1}

    def _handle_fallback(self, error: Exception, error_info: dict[str, Any], context: dict[str, Any]) -> dict[str, Any]:
        """Handle fallback recovery action using LLM.

        Args:
            error: Original exception
            error_info: Error information
            context: Error context

        Returns:
            Fallback recovery action
        """
        fallback_prompt = self.prompt_loader.get_prompt(
            "error_fallback", error=str(error), error_type=type(error).__name__, context=str(context)
        )

        try:
            _fallback_response = self.llm.forward(fallback_prompt)
            # TODO: Parse LLM response into fallback plan with proper JSON parsing
            # For now, return skip action
            self._logger.info("Fallback plan generation attempted, skipping step")
            return {"action": "skip", "error": error_info}
        except Exception:
            self._logger.exception("Failed to generate fallback plan")
            # If fallback generation fails, skip the step
            return {"action": "skip", "error": error_info}
