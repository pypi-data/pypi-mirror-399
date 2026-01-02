"""Result synthesis module for Orchestrator Agent.

This module handles combining and synthesizing results from multiple plan
executions and tool calls into coherent final responses.
"""

import json
from typing import Any

from loguru import logger

from fluxibly.llm.base import BaseLLM
from fluxibly.orchestrator.config.prompts import get_default_loader


class ResultSynthesizer:
    """Synthesizes execution results into coherent responses.

    The ResultSynthesizer combines outputs from multiple MCP tool calls and
    execution steps into a final user-friendly response using various strategies.

    Attributes:
        llm: LLM instance for intelligent synthesis
        synthesis_strategy: Strategy to use for result synthesis
        prompt_loader: PromptLoader for template management
    """

    def __init__(self, llm: BaseLLM, synthesis_strategy: str = "llm_synthesis") -> None:
        """Initialize the ResultSynthesizer.

        Args:
            llm: LLM instance for intelligent result synthesis
            synthesis_strategy: Strategy for combining results
                Options: "llm_synthesis", "concatenate", "structured"
        """
        self.llm = llm
        self.synthesis_strategy = synthesis_strategy
        self.prompt_loader = get_default_loader()
        self._logger = logger.bind(component="ResultSynthesizer")

    def synthesize_results(self, execution_results: dict[str, Any]) -> str:
        """Combine outputs from multiple executions into coherent response.

        Uses the configured synthesis strategy to create final response:
        - llm_synthesis: Use LLM to intelligently combine results
        - concatenate: Simple concatenation of outputs
        - structured: Return structured JSON with all results

        Args:
            execution_results: All results from plan execution(s) containing:
                - step_results: Dict of step results
                - errors: List of errors
                - task_complete: Whether task completed successfully

        Returns:
            str: Synthesized final response for the user

        Example:
            >>> synthesizer = ResultSynthesizer(llm, "llm_synthesis")
            >>> results = {"step_results": {...}, "errors": []}
            >>> final = synthesizer.synthesize_results(results)
            >>> print(final)
            "Based on analysis, the document contains..."
        """
        step_results = execution_results.get("step_results", {})
        errors = execution_results.get("errors", [])
        user_prompt = execution_results.get("user_prompt", "")
        strategy = self.synthesis_strategy

        self._logger.debug(
            f"Synthesizing results using '{strategy}' strategy: {len(step_results)} steps, {len(errors)} errors"
        )

        if strategy == "concatenate":
            return self._synthesize_concatenate(step_results)

        elif strategy == "structured":
            return self._synthesize_structured(step_results, errors, execution_results)

        else:  # llm_synthesis (default)
            return self._synthesize_with_llm(step_results, errors, user_prompt)

    def _synthesize_concatenate(self, step_results: dict[int, dict[str, Any]]) -> str:
        """Synthesize results by simple concatenation.

        Args:
            step_results: Step execution results

        Returns:
            Concatenated results string
        """
        results_text = []
        for step_id, step_data in step_results.items():
            result = step_data.get("result", "")
            if result:
                results_text.append(f"Step {step_id}: {result}")

        if not results_text:
            return "No results generated"

        return "\n\n".join(results_text)

    def _synthesize_structured(
        self, step_results: dict[int, dict[str, Any]], errors: list[dict[str, Any]], execution_results: dict[str, Any]
    ) -> str:
        """Synthesize results as structured JSON.

        Args:
            step_results: Step execution results
            errors: List of errors
            execution_results: Full execution results

        Returns:
            JSON formatted results string
        """
        return json.dumps(
            {
                "step_results": step_results,
                "errors": errors,
                "task_complete": execution_results.get("task_complete", False),
            },
            indent=2,
        )

    def _synthesize_with_llm(
        self, step_results: dict[int, dict[str, Any]], errors: list[dict[str, Any]], user_prompt: str = ""
    ) -> str:
        """Synthesize results using LLM for intelligent combination.

        Args:
            step_results: Step execution results
            errors: List of errors
            user_prompt: Original user request (optional)

        Returns:
            LLM-synthesized final response
        """
        synthesis_prompt = self.prompt_loader.get_prompt(
            "result_synthesis",
            step_results=str(step_results),
            errors=str(errors),
            user_prompt=user_prompt if user_prompt else "No user prompt provided",
        )

        try:
            synthesized = self.llm.forward(synthesis_prompt)
            self._logger.debug(f"LLM synthesis completed: {len(synthesized)} chars")
            return synthesized
        except Exception as e:
            self._logger.exception("LLM synthesis failed, falling back to concatenation")
            # Fallback to concatenation if synthesis fails
            results_text = []
            for step_id, step_data in step_results.items():
                result = step_data.get("result", "")
                if result:
                    results_text.append(f"Step {step_id}: {result}")

            error_text = f"\n\nSynthesis error: {str(e)}" if errors else ""
            return "\n\n".join(results_text) + error_text
