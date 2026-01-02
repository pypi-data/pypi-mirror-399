"""Prompt template loader for Orchestrator Agent.

This module provides utilities for loading and formatting prompt templates
from YAML configuration files.
"""

from pathlib import Path
from typing import Any

import yaml
from loguru import logger


class PromptLoader:
    """Loads and manages prompt templates from YAML configuration.

    The PromptLoader reads prompt templates from a YAML file and provides
    methods to format them with dynamic values.

    Attributes:
        config_path: Path to the prompts YAML file
        prompts: Loaded prompt templates dictionary
    """

    def __init__(self, config_path: str | Path | None = None) -> None:
        """Initialize the PromptLoader.

        Args:
            config_path: Path to prompts YAML file. If None, uses default path.
        """
        if config_path is None:
            # Default to config/orchestrator/prompts.yaml relative to project root
            default_path = Path(__file__).parent.parent.parent.parent / "config" / "orchestrator" / "prompts.yaml"
            config_path = default_path

        self.config_path = Path(config_path)
        self.prompts: dict[str, Any] = {}
        self._load_prompts()

    def _load_prompts(self) -> None:
        """Load prompt templates from YAML file."""
        try:
            if not self.config_path.exists():
                logger.warning(f"Prompt config file not found: {self.config_path}, using defaults")
                self._load_defaults()
                return

            with open(self.config_path) as f:
                self.prompts = yaml.safe_load(f) or {}

            # If loaded prompts is empty, fallback to defaults
            if not self.prompts:
                logger.warning(f"Prompt config file is empty: {self.config_path}, using defaults")
                self._load_defaults()
                return

            logger.debug(f"Loaded {len(self.prompts)} prompt templates from {self.config_path}")
        except Exception:
            logger.exception(f"Failed to load prompts from {self.config_path}")
            self._load_defaults()

    def _load_defaults(self) -> None:
        """Load default prompts if config file is not available."""
        self.prompts = {
            "mcp_selection": {
                "template": "Analyze task: {user_prompt}\nAvailable tools: {available_mcps}\n"
                "Return JSON array of selected tools."
            },
            "task_analysis": {"template": "Analyze task: {user_prompt}\nContext: {context}\nReturn JSON analysis."},
            "plan_generation": {
                "template": "Generate plan for: {user_prompt}\nTools: {available_tools}\nReturn JSON plan."
            },
            "step_execution": {"template": "Execute: {description}\nPrevious: {step_results}\nContext: {context}"},
            "plan_refinement": {
                "template": "Refine plan: {current_plan}\nResults: {execution_results}\nErrors: {errors}"
            },
            "result_synthesis": {"template": "Synthesize results: {step_results}\nErrors: {errors}"},
            "error_fallback": {"template": "Handle error: {error}\nType: {error_type}\nContext: {context}"},
            "orchestration_instructions": "You are an orchestrator agent.",
            "parameters": {
                "complexity_levels": ["low", "medium", "high"],
                "max_retries": 3,
                "default_mcp_timeout": 30,
            },
        }

    def get_prompt(self, prompt_name: str, **kwargs: Any) -> str:
        """Get formatted prompt template.

        Args:
            prompt_name: Name of the prompt template
            **kwargs: Values to format into the template

        Returns:
            Formatted prompt string

        Example:
            >>> loader = PromptLoader()
            >>> prompt = loader.get_prompt("task_analysis", user_prompt="Analyze data", context={})
        """
        if prompt_name not in self.prompts:
            logger.warning(f"Prompt '{prompt_name}' not found, returning empty string")
            return ""

        prompt_data = self.prompts[prompt_name]

        # Handle string prompts (like orchestration_instructions)
        if isinstance(prompt_data, str):
            return prompt_data.format(**kwargs) if kwargs else prompt_data

        # Handle dict prompts with template key
        template = prompt_data.get("template", "")
        if not template:
            logger.warning(f"Prompt '{prompt_name}' has no template")
            return ""

        try:
            return template.format(**kwargs)
        except KeyError as e:
            logger.warning(f"Missing template variable in '{prompt_name}': {e}")
            # Return template with unfilled placeholders
            return template

    def get_parameter(self, param_path: str, default: Any = None) -> Any:
        """Get configuration parameter from prompts config.

        Args:
            param_path: Dot-separated path to parameter (e.g., "parameters.max_retries")
            default: Default value if parameter not found

        Returns:
            Parameter value or default

        Example:
            >>> loader = PromptLoader()
            >>> max_retries = loader.get_parameter("parameters.max_retries", 3)
        """
        keys = param_path.split(".")
        value = self.prompts

        try:
            for key in keys:
                value = value[key]
            return value
        except (KeyError, TypeError):
            logger.debug(f"Parameter '{param_path}' not found, using default: {default}")
            return default

    def get_complexity_levels(self) -> list[str]:
        """Get available complexity levels.

        Returns:
            List of complexity level strings
        """
        return self.get_parameter("parameters.complexity_levels", ["low", "medium", "high"])

    def get_max_retries(self) -> int:
        """Get maximum retry count for error recovery.

        Returns:
            Maximum number of retries
        """
        return self.get_parameter("parameters.max_retries", 3)

    def get_default_mcp_timeout(self) -> int:
        """Get default MCP tool timeout in seconds.

        Returns:
            Timeout in seconds
        """
        return self.get_parameter("parameters.default_mcp_timeout", 30)

    def reload(self) -> None:
        """Reload prompts from configuration file.

        Useful for hot-reloading configuration changes during development.
        """
        self._load_prompts()
        logger.info(f"Reloaded prompts from {self.config_path}")


# Global prompt loader instance
_default_loader: PromptLoader | None = None


def get_default_loader() -> PromptLoader:
    """Get or create the default global PromptLoader instance.

    Returns:
        Global PromptLoader instance
    """
    global _default_loader
    if _default_loader is None:
        _default_loader = PromptLoader()
    return _default_loader
