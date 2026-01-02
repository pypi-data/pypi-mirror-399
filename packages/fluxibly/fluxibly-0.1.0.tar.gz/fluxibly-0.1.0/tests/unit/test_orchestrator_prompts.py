"""Unit tests for orchestrator PromptLoader."""

from pathlib import Path

import pytest
import yaml

from fluxibly.orchestrator.config.prompts import PromptLoader, get_default_loader


@pytest.fixture
def sample_prompts_yaml(tmp_path: Path) -> Path:
    """Create a sample prompts.yaml file for testing."""
    prompts_config = {
        "mcp_selection": {
            "template": "Select tools for: {user_prompt}\nAvailable: {available_mcps}\nContext: {context}"
        },
        "task_analysis": {"template": "Analyze: {user_prompt}\nContext: {context}"},
        "orchestration_instructions": "You are an orchestrator agent with advanced capabilities.",
        "parameters": {"complexity_levels": ["low", "medium", "high"], "max_retries": 5, "default_mcp_timeout": 60},
    }

    yaml_path = tmp_path / "test_prompts.yaml"
    with open(yaml_path, "w") as f:
        yaml.dump(prompts_config, f)

    return yaml_path


@pytest.fixture
def empty_yaml(tmp_path: Path) -> Path:
    """Create an empty YAML file."""
    yaml_path = tmp_path / "empty.yaml"
    yaml_path.write_text("")
    return yaml_path


class TestPromptLoaderInitialization:
    """Tests for PromptLoader initialization."""

    def test_init_with_custom_path(self, sample_prompts_yaml: Path) -> None:
        """Test initialization with custom config path."""
        loader = PromptLoader(config_path=sample_prompts_yaml)

        assert loader.config_path == sample_prompts_yaml
        assert len(loader.prompts) > 0
        assert "mcp_selection" in loader.prompts
        assert "task_analysis" in loader.prompts

    def test_init_with_nonexistent_path(self, tmp_path: Path) -> None:
        """Test initialization with nonexistent file falls back to defaults."""
        nonexistent = tmp_path / "nonexistent.yaml"
        loader = PromptLoader(config_path=nonexistent)

        # Should load defaults
        assert len(loader.prompts) > 0
        assert "mcp_selection" in loader.prompts
        assert "parameters" in loader.prompts

    def test_init_with_default_path(self) -> None:
        """Test initialization without custom path uses default."""
        loader = PromptLoader()

        # Should have loaded some prompts (either from file or defaults)
        assert len(loader.prompts) > 0
        assert isinstance(loader.prompts, dict)

    def test_init_with_empty_yaml(self, empty_yaml: Path) -> None:
        """Test initialization with empty YAML file loads defaults."""
        loader = PromptLoader(config_path=empty_yaml)

        # Should fallback to defaults when YAML is empty
        assert len(loader.prompts) > 0


class TestGetPrompt:
    """Tests for get_prompt method."""

    def test_get_prompt_dict_template(self, sample_prompts_yaml: Path) -> None:
        """Test getting prompt with dict template format."""
        loader = PromptLoader(config_path=sample_prompts_yaml)

        prompt = loader.get_prompt("mcp_selection", user_prompt="Test task", available_mcps="tool1, tool2", context="")

        assert "Test task" in prompt
        assert "tool1, tool2" in prompt

    def test_get_prompt_string_template(self, sample_prompts_yaml: Path) -> None:
        """Test getting prompt with string template format."""
        loader = PromptLoader(config_path=sample_prompts_yaml)

        prompt = loader.get_prompt("orchestration_instructions")

        assert "orchestrator agent" in prompt

    def test_get_prompt_missing_template(self, sample_prompts_yaml: Path) -> None:
        """Test getting nonexistent prompt returns empty string."""
        loader = PromptLoader(config_path=sample_prompts_yaml)

        prompt = loader.get_prompt("nonexistent_prompt")

        assert prompt == ""

    def test_get_prompt_missing_kwargs(self, sample_prompts_yaml: Path) -> None:
        """Test get_prompt with missing template variables returns template."""
        loader = PromptLoader(config_path=sample_prompts_yaml)

        # Call with missing required kwargs
        prompt = loader.get_prompt("task_analysis", user_prompt="Test")
        # Should return template even with missing 'context' variable

        assert isinstance(prompt, str)

    def test_get_prompt_with_extra_kwargs(self, sample_prompts_yaml: Path) -> None:
        """Test get_prompt ignores extra kwargs."""
        loader = PromptLoader(config_path=sample_prompts_yaml)

        prompt = loader.get_prompt(
            "task_analysis", user_prompt="Test", context="ctx", extra_arg="ignored", another="also_ignored"
        )

        assert "Test" in prompt
        assert "ctx" in prompt
        # Extra args should be ignored without error


class TestGetParameter:
    """Tests for get_parameter method."""

    def test_get_parameter_simple(self, sample_prompts_yaml: Path) -> None:
        """Test getting a simple parameter."""
        loader = PromptLoader(config_path=sample_prompts_yaml)

        max_retries = loader.get_parameter("parameters.max_retries")

        assert max_retries == 5

    def test_get_parameter_nested(self, sample_prompts_yaml: Path) -> None:
        """Test getting nested parameter."""
        loader = PromptLoader(config_path=sample_prompts_yaml)

        timeout = loader.get_parameter("parameters.default_mcp_timeout")

        assert timeout == 60

    def test_get_parameter_list(self, sample_prompts_yaml: Path) -> None:
        """Test getting list parameter."""
        loader = PromptLoader(config_path=sample_prompts_yaml)

        levels = loader.get_parameter("parameters.complexity_levels")

        assert levels == ["low", "medium", "high"]

    def test_get_parameter_with_default(self, sample_prompts_yaml: Path) -> None:
        """Test getting nonexistent parameter returns default."""
        loader = PromptLoader(config_path=sample_prompts_yaml)

        value = loader.get_parameter("parameters.nonexistent", default=42)

        assert value == 42

    def test_get_parameter_invalid_path(self, sample_prompts_yaml: Path) -> None:
        """Test getting parameter with invalid path returns default."""
        loader = PromptLoader(config_path=sample_prompts_yaml)

        value = loader.get_parameter("invalid.path.to.param", default="fallback")

        assert value == "fallback"


class TestConvenienceMethods:
    """Tests for convenience parameter getter methods."""

    def test_get_complexity_levels(self, sample_prompts_yaml: Path) -> None:
        """Test get_complexity_levels method."""
        loader = PromptLoader(config_path=sample_prompts_yaml)

        levels = loader.get_complexity_levels()

        assert isinstance(levels, list)
        assert len(levels) == 3
        assert "low" in levels
        assert "medium" in levels
        assert "high" in levels

    def test_get_max_retries(self, sample_prompts_yaml: Path) -> None:
        """Test get_max_retries method."""
        loader = PromptLoader(config_path=sample_prompts_yaml)

        max_retries = loader.get_max_retries()

        assert isinstance(max_retries, int)
        assert max_retries == 5

    def test_get_default_mcp_timeout(self, sample_prompts_yaml: Path) -> None:
        """Test get_default_mcp_timeout method."""
        loader = PromptLoader(config_path=sample_prompts_yaml)

        timeout = loader.get_default_mcp_timeout()

        assert isinstance(timeout, int)
        assert timeout == 60

    def test_get_methods_with_defaults(self, tmp_path: Path) -> None:
        """Test convenience methods return defaults when parameter missing."""
        # Create YAML without parameters
        minimal_yaml = tmp_path / "minimal.yaml"
        minimal_yaml.write_text("mcp_selection:\n  template: 'test'")

        loader = PromptLoader(config_path=minimal_yaml)

        # Should return defaults
        assert loader.get_complexity_levels() == ["low", "medium", "high"]
        assert loader.get_max_retries() == 3
        assert loader.get_default_mcp_timeout() == 30


class TestReload:
    """Tests for reload method."""

    def test_reload_updates_prompts(self, sample_prompts_yaml: Path) -> None:
        """Test reload updates prompts from file."""
        loader = PromptLoader(config_path=sample_prompts_yaml)

        original_prompt = loader.get_prompt("task_analysis", user_prompt="test", context="ctx")

        # Modify the YAML file
        with open(sample_prompts_yaml) as f:
            config = yaml.safe_load(f)

        config["task_analysis"]["template"] = "UPDATED: {user_prompt}"

        with open(sample_prompts_yaml, "w") as f:
            yaml.dump(config, f)

        # Reload
        loader.reload()

        updated_prompt = loader.get_prompt("task_analysis", user_prompt="test")

        assert "UPDATED" in updated_prompt
        assert updated_prompt != original_prompt

    def test_reload_handles_file_deletion(self, tmp_path: Path) -> None:
        """Test reload handles deleted config file gracefully."""
        yaml_path = tmp_path / "temp.yaml"
        yaml_path.write_text("test_prompt:\n  template: 'test'")

        loader = PromptLoader(config_path=yaml_path)
        assert "test_prompt" in loader.prompts

        # Delete file
        yaml_path.unlink()

        # Reload should fallback to defaults
        loader.reload()
        assert len(loader.prompts) > 0  # Should have defaults


class TestGetDefaultLoader:
    """Tests for get_default_loader singleton."""

    def test_get_default_loader_returns_instance(self) -> None:
        """Test get_default_loader returns a PromptLoader instance."""
        loader = get_default_loader()

        assert isinstance(loader, PromptLoader)
        assert len(loader.prompts) > 0

    def test_get_default_loader_singleton(self) -> None:
        """Test get_default_loader returns same instance."""
        loader1 = get_default_loader()
        loader2 = get_default_loader()

        assert loader1 is loader2  # Same object reference


class TestLoadDefaults:
    """Tests for default prompt loading."""

    def test_load_defaults_has_all_prompts(self) -> None:
        """Test default prompts include all required templates."""
        loader = PromptLoader(config_path="/nonexistent/path.yaml")

        # Check all required prompts exist
        required_prompts = [
            "mcp_selection",
            "task_analysis",
            "plan_generation",
            "step_execution",
            "plan_refinement",
            "result_synthesis",
            "error_fallback",
            "orchestration_instructions",
        ]

        for prompt_name in required_prompts:
            assert prompt_name in loader.prompts, f"Missing default prompt: {prompt_name}"

    def test_load_defaults_has_parameters(self) -> None:
        """Test default prompts include parameters section."""
        loader = PromptLoader(config_path="/nonexistent/path.yaml")

        assert "parameters" in loader.prompts
        assert "complexity_levels" in loader.prompts["parameters"]
        assert "max_retries" in loader.prompts["parameters"]
        assert "default_mcp_timeout" in loader.prompts["parameters"]


class TestErrorHandling:
    """Tests for error handling in PromptLoader."""

    def test_invalid_yaml_loads_defaults(self, tmp_path: Path) -> None:
        """Test invalid YAML content loads defaults."""
        invalid_yaml = tmp_path / "invalid.yaml"
        invalid_yaml.write_text("invalid: yaml: content: [[[")

        loader = PromptLoader(config_path=invalid_yaml)

        # Should fallback to defaults
        assert len(loader.prompts) > 0
        assert "mcp_selection" in loader.prompts

    def test_template_format_error_returns_template(self, sample_prompts_yaml: Path) -> None:
        """Test format error returns unformatted template."""
        loader = PromptLoader(config_path=sample_prompts_yaml)

        # Call with completely wrong kwargs
        prompt = loader.get_prompt("mcp_selection")

        # Should return template string even if formatting fails
        assert isinstance(prompt, str)
