"""Configuration loader for MCP servers and framework settings.

This module provides configuration loading and validation for the framework.
"""

from pathlib import Path
from typing import Any

import yaml
from pydantic import BaseModel, Field


class OrchestratorConfig(BaseModel):
    """Orchestrator configuration."""

    model: str = Field("gpt-4o", description="LLM model to use")
    temperature: float = Field(0.7, description="Temperature for LLM")
    system_prompt: str = Field("", description="System prompt for orchestrator")
    max_iterations: int = Field(10, description="Maximum execution iterations")


class FrameworkConfig(BaseModel):
    """Framework-level configuration."""

    log_level: str = Field("INFO", description="Logging level")
    enable_tracing: bool = Field(False, description="Enable distributed tracing")
    health_check_interval: int = Field(60, description="Health check interval in seconds")


class MCPServerConfig(BaseModel):
    """Configuration for a single MCP server."""

    command: str = Field(..., description="Command to start server")
    args: list[str] = Field(default_factory=list, description="Command arguments")
    env: dict[str, str] = Field(default_factory=dict, description="Environment variables")
    enabled: bool = Field(True, description="Whether server is enabled")
    priority: int = Field(1, description="Server priority")


class ConfigLoader:
    """Loads and validates framework configuration from YAML files."""

    def __init__(self, config_dir: str | Path = "config") -> None:
        """Initialize configuration loader.

        Args:
            config_dir: Directory containing configuration files
        """
        self.config_dir = Path(config_dir)

    def load_mcp_servers(self, filename: str = "mcp_servers.yaml") -> dict[str, MCPServerConfig]:
        """Load MCP server configurations.

        Args:
            filename: Configuration filename

        Returns:
            Dictionary of server name to configuration
        """
        raise NotImplementedError

    def load_framework_config(self, filename: str = "framework.yaml") -> FrameworkConfig:
        """Load framework configuration.

        Args:
            filename: Configuration filename

        Returns:
            Framework configuration
        """
        raise NotImplementedError

    def load_profile(self, profile_name: str) -> dict[str, Any]:
        """Load a configuration profile.

        Loads the base framework configuration and merges it with the specified
        profile configuration. Profile settings override framework defaults.

        Args:
            profile_name: Name of the profile to load, or path to a profile YAML file.
                         If it contains path separators (/ or \\) or ends with .yaml/.yml,
                         it's treated as a file path. Otherwise, it's treated as a profile
                         name in the config/profiles/ directory.

        Returns:
            Merged profile configuration

        Raises:
            FileNotFoundError: If profile file doesn't exist
            ValueError: If YAML parsing fails

        Examples:
            >>> # Load by name (searches in config/profiles/)
            >>> config = loader.load_profile("development_assistant")
            >>> # Load by absolute path
            >>> config = loader.load_profile("/path/to/my_profile.yaml")
            >>> # Load by relative path
            >>> config = loader.load_profile("../custom_profiles/special.yaml")
        """
        # Load base framework configuration
        framework_path = self.config_dir / "framework.yaml"
        if not framework_path.exists():
            raise FileNotFoundError(f"Framework configuration not found: {framework_path}")

        base_config = self._load_yaml(framework_path)

        # Determine if profile_name is a path or a name
        is_path = "/" in profile_name or "\\" in profile_name or profile_name.endswith((".yaml", ".yml"))

        if is_path:
            # Treat as file path
            profile_path = Path(profile_name)
            if not profile_path.is_absolute():
                # Make relative paths relative to current working directory
                profile_path = profile_path.resolve()
        else:
            # Treat as profile name in config/profiles/
            profile_path = self.config_dir / "profiles" / f"{profile_name}.yaml"

        if not profile_path.exists():
            if is_path:
                raise FileNotFoundError(f"Profile file not found: {profile_path}")
            else:
                raise FileNotFoundError(f"Profile not found: {profile_name} at {profile_path}")

        profile_config = self._load_yaml(profile_path)

        # Deep merge profile into base
        merged_config = self.merge_configs(base_config, profile_config)

        return merged_config

    def merge_configs(self, base: dict[str, Any], override: dict[str, Any]) -> dict[str, Any]:
        """Deep merge two configuration dictionaries.

        Override values take precedence over base values. For nested dictionaries,
        the merge is recursive. Lists and primitive values are replaced entirely.

        Args:
            base: Base configuration dictionary
            override: Override configuration dictionary

        Returns:
            Merged configuration (base is not modified)

        Example:
            >>> base = {"a": 1, "b": {"c": 2, "d": 3}}
            >>> override = {"b": {"c": 10}, "e": 4}
            >>> merged = loader.merge_configs(base, override)
            >>> merged
            {"a": 1, "b": {"c": 10, "d": 3}, "e": 4}
        """
        # Create a copy to avoid modifying the base
        result = base.copy()

        for key, value in override.items():
            if key in result and isinstance(result[key], dict) and isinstance(value, dict):
                # Recursively merge nested dictionaries
                result[key] = self.merge_configs(result[key], value)
            else:
                # Override value (works for primitives, lists, and new keys)
                result[key] = value

        return result

    def _load_yaml(self, filepath: Path) -> dict[str, Any]:
        """Load YAML file.

        Args:
            filepath: Path to YAML file

        Returns:
            Parsed YAML content

        Raises:
            FileNotFoundError: If file doesn't exist
            ValueError: If YAML parsing fails
        """
        if not filepath.exists():
            raise FileNotFoundError(f"YAML file not found: {filepath}")

        try:
            with open(filepath) as f:
                content = yaml.safe_load(f)

            if content is None:
                return {}

            if not isinstance(content, dict):
                raise ValueError(f"Expected dict in YAML file, got {type(content)}: {filepath}")

            return content

        except yaml.YAMLError as e:
            raise ValueError(f"Failed to parse YAML file: {filepath}") from e
