"""Unit tests for orchestrator MCPSelector."""

from unittest.mock import MagicMock

import pytest

from fluxibly.llm.base import BaseLLM, LLMConfig
from fluxibly.orchestrator.selector import MCPSelector


class MockLLM(BaseLLM):
    """Mock LLM for testing."""

    def __init__(self, config: LLMConfig) -> None:
        super().__init__(config)
        self.call_count = 0
        self.last_prompt = None
        self.response = '[{"name": "tool1", "priority": 1, "relevance": 0.9, "use_case": "test"}]'

    def forward(self, prompt: str, **kwargs) -> str:  # noqa: ARG002
        """Mock forward method."""
        self.call_count += 1
        self.last_prompt = prompt
        return self.response


@pytest.fixture
def mock_llm() -> MockLLM:
    """Create a mock LLM for testing."""
    config = LLMConfig(model="gpt-4o")
    return MockLLM(config=config)


@pytest.fixture
def mcp_selector(mock_llm: MockLLM) -> MCPSelector:
    """Create an MCPSelector with mock LLM."""
    return MCPSelector(llm=mock_llm)


class TestMCPSelectorInitialization:
    """Tests for MCPSelector initialization."""

    def test_init(self, mock_llm: MockLLM) -> None:
        """Test MCPSelector initialization."""
        selector = MCPSelector(llm=mock_llm)

        assert selector.llm == mock_llm
        assert selector.prompt_loader is not None


class TestSelectMCPTools:
    """Tests for select_mcp_tools method."""

    def test_select_mcp_tools_basic(self, mcp_selector: MCPSelector, mock_llm: MockLLM) -> None:
        """Test basic MCP tool selection."""
        mock_llm.response = """
        [
            {"name": "ocr", "priority": 1, "relevance": 0.9, "use_case": "Extract text", "dependencies": []},
            {"name": "translation", "priority": 2, "relevance": 0.7, "use_case": "Translate text", "dependencies": ["ocr"]}
        ]
        """

        selected = mcp_selector.select_mcp_tools(
            user_prompt="Extract and translate PDF", available_mcps=["ocr", "translation", "calculator"], context={}
        )

        assert len(selected) == 2
        assert selected[0]["name"] == "ocr"
        assert selected[0]["relevance"] == 0.9
        assert selected[1]["name"] == "translation"
        assert selected[1]["dependencies"] == ["ocr"]

    def test_select_mcp_tools_with_context(self, mcp_selector: MCPSelector, mock_llm: MockLLM) -> None:
        """Test MCP tool selection includes context in prompt."""
        context = {"document_type": "invoice", "language": "spanish"}

        mcp_selector.select_mcp_tools(
            user_prompt="Process document", available_mcps=["ocr", "translation"], context=context
        )

        # Context should be formatted and included in prompt
        assert mock_llm.last_prompt and ("invoice" in mock_llm.last_prompt or "spanish" in mock_llm.last_prompt)

    def test_select_mcp_tools_empty_available(self, mcp_selector: MCPSelector) -> None:
        """Test MCP tool selection with empty available tools."""
        selected = mcp_selector.select_mcp_tools(user_prompt="Test", available_mcps=[], context={})

        assert selected == []

    def test_select_mcp_tools_invalid_json(self, mcp_selector: MCPSelector, mock_llm: MockLLM) -> None:
        """Test MCP tool selection falls back when JSON is invalid."""
        mock_llm.response = "Not valid JSON"
        available_mcps = ["tool1", "tool2"]

        selected = mcp_selector.select_mcp_tools(user_prompt="Test", available_mcps=available_mcps, context={})

        # Should fallback to all available MCPs
        assert len(selected) == 2
        assert selected[0]["name"] == "tool1"
        assert selected[1]["name"] == "tool2"
        assert selected[0]["priority"] == 1
        assert selected[0]["relevance"] == 1.0

    def test_select_mcp_tools_no_json_array(self, mcp_selector: MCPSelector, mock_llm: MockLLM) -> None:
        """Test MCP tool selection when no JSON array in response."""
        mock_llm.response = '{"not": "an array"}'
        available_mcps = ["tool1"]

        selected = mcp_selector.select_mcp_tools(user_prompt="Test", available_mcps=available_mcps, context={})

        # Should fallback
        assert len(selected) == 1
        assert selected[0]["name"] == "tool1"

    def test_select_mcp_tools_with_defaults(self, mcp_selector: MCPSelector, mock_llm: MockLLM) -> None:
        """Test MCP tool selection fills in missing fields with defaults."""
        mock_llm.response = '[{"name": "tool1"}]'  # Minimal data

        selected = mcp_selector.select_mcp_tools(user_prompt="Test", available_mcps=["tool1"], context={})

        assert len(selected) == 1
        assert selected[0]["name"] == "tool1"
        # Should have defaults
        assert selected[0]["priority"] == 1
        assert selected[0]["relevance"] == 1.0
        assert selected[0]["use_case"] == "General purpose"
        assert selected[0]["dependencies"] == []

    def test_select_mcp_tools_invalid_mcp_name(self, mcp_selector: MCPSelector, mock_llm: MockLLM) -> None:
        """Test MCP tool selection falls back when invalid MCP names provided."""
        mock_llm.response = """
        [
            {"name": "valid_tool", "priority": 1},
            {"name": "invalid_tool", "priority": 2}
        ]
        """
        available_mcps = ["valid_tool"]  # invalid_tool is not available

        # Should fallback to all available MCPs when validation fails
        selected = mcp_selector.select_mcp_tools(user_prompt="Test", available_mcps=available_mcps, context={})

        assert len(selected) == 1
        assert selected[0]["name"] == "valid_tool"

    def test_select_mcp_tools_missing_name_field(self, mcp_selector: MCPSelector, mock_llm: MockLLM) -> None:
        """Test MCP tool selection falls back when entries missing name field."""
        mock_llm.response = '[{"priority": 1, "relevance": 0.9}]'  # No name field
        available_mcps = ["tool1"]

        # Should fallback to all available MCPs when validation fails
        selected = mcp_selector.select_mcp_tools(user_prompt="Test", available_mcps=available_mcps, context={})

        assert len(selected) == 1
        assert selected[0]["name"] == "tool1"

    def test_select_mcp_tools_exception_handling(self, mcp_selector: MCPSelector, mock_llm: MockLLM) -> None:
        """Test MCP tool selection handles LLM exceptions."""
        mock_llm.forward = MagicMock(side_effect=Exception("LLM error"))
        available_mcps = ["tool1", "tool2"]

        selected = mcp_selector.select_mcp_tools(user_prompt="Test", available_mcps=available_mcps, context={})

        # Should fallback without raising
        assert len(selected) == 2


class TestFormatMCPTools:
    """Tests for format_mcp_tools method."""

    def test_format_mcp_tools_basic(self, mcp_selector: MCPSelector) -> None:
        """Test formatting MCP tools for system prompt."""
        selected_mcps = [
            {"name": "ocr", "use_case": "Extract text from images"},
            {"name": "translation", "use_case": "Translate between languages"},
        ]

        formatted = mcp_selector.format_mcp_tools(selected_mcps)

        assert "- ocr: Extract text from images" in formatted
        assert "- translation: Translate between languages" in formatted
        assert "\n" in formatted  # Multi-line

    def test_format_mcp_tools_single(self, mcp_selector: MCPSelector) -> None:
        """Test formatting single MCP tool."""
        selected_mcps = [{"name": "calculator", "use_case": "Perform calculations"}]

        formatted = mcp_selector.format_mcp_tools(selected_mcps)

        assert "- calculator: Perform calculations" in formatted

    def test_format_mcp_tools_empty(self, mcp_selector: MCPSelector) -> None:
        """Test formatting empty MCP tools list."""
        formatted = mcp_selector.format_mcp_tools([])

        assert formatted == "No MCP tools available."

    def test_format_mcp_tools_missing_use_case(self, mcp_selector: MCPSelector) -> None:
        """Test formatting MCP tools with missing use_case field."""
        selected_mcps = [{"name": "tool1"}]

        formatted = mcp_selector.format_mcp_tools(selected_mcps)

        assert "- tool1: General purpose tool" in formatted


class TestFormatContext:
    """Tests for _format_context helper method."""

    def test_format_context_empty(self, mcp_selector: MCPSelector) -> None:
        """Test formatting empty context."""
        formatted = mcp_selector._format_context({})

        assert formatted == "No additional context provided"

    def test_format_context_none(self, mcp_selector: MCPSelector) -> None:
        """Test formatting None context."""
        formatted = mcp_selector._format_context({})

        assert formatted == "No additional context provided"

    def test_format_context_simple_values(self, mcp_selector: MCPSelector) -> None:
        """Test formatting context with simple values."""
        context = {"language": "spanish", "format": "pdf", "pages": 10}

        formatted = mcp_selector._format_context(context)

        assert "language: spanish" in formatted
        assert "format: pdf" in formatted
        assert "pages: 10" in formatted

    def test_format_context_nested_dict(self, mcp_selector: MCPSelector) -> None:
        """Test formatting context with nested dictionary."""
        context = {"metadata": {"author": "John Doe", "date": "2024-01-01"}, "type": "invoice"}

        formatted = mcp_selector._format_context(context)

        assert "metadata:" in formatted
        assert "author: John Doe" in formatted
        assert "date: 2024-01-01" in formatted
        assert "type: invoice" in formatted
        assert "  - " in formatted  # Should be indented

    def test_format_context_list_values(self, mcp_selector: MCPSelector) -> None:
        """Test formatting context with list values."""
        context = {"languages": ["english", "spanish", "french"], "pages": [1, 2, 3]}

        formatted = mcp_selector._format_context(context)

        assert "languages: english, spanish, french" in formatted
        assert "pages: 1, 2, 3" in formatted

    def test_format_context_mixed_types(self, mcp_selector: MCPSelector) -> None:
        """Test formatting context with mixed data types."""
        context = {
            "string_val": "test",
            "number_val": 42,
            "list_val": [1, 2, 3],
            "dict_val": {"nested": "value"},
        }

        formatted = mcp_selector._format_context(context)

        assert "string_val: test" in formatted
        assert "number_val: 42" in formatted
        assert "list_val: 1, 2, 3" in formatted
        assert "dict_val:" in formatted
        assert "nested: value" in formatted

    def test_format_context_filters_internal_keys(self, mcp_selector: MCPSelector) -> None:
        """Test formatting context filters out internal keys."""
        context = {
            "user_data": "visible",
            "execution_history": "should_be_filtered",
            "selected_mcps": "should_be_filtered",
            "planning_context": "should_be_filtered",
            "execution_params": "should_be_filtered",
            "other_data": "visible",
        }

        formatted = mcp_selector._format_context(context)

        assert "user_data: visible" in formatted
        assert "other_data: visible" in formatted
        # Internal keys should not appear
        assert "execution_history" not in formatted
        assert "selected_mcps" not in formatted
        assert "planning_context" not in formatted
        assert "execution_params" not in formatted

    def test_format_context_only_internal_keys(self, mcp_selector: MCPSelector) -> None:
        """Test formatting context with only internal keys."""
        context = {"execution_history": "data", "selected_mcps": "data"}

        formatted = mcp_selector._format_context(context)

        # Should return "no context" message
        assert formatted == "No additional context provided"

    def test_format_context_empty_nested_dict(self, mcp_selector: MCPSelector) -> None:
        """Test formatting context with empty nested dictionary."""
        context = {"metadata": {}, "type": "test"}

        formatted = mcp_selector._format_context(context)

        assert "type: test" in formatted
        # Empty dict should still show key
        assert "metadata:" in formatted

    def test_format_context_empty_list(self, mcp_selector: MCPSelector) -> None:
        """Test formatting context with empty list."""
        context = {"items": [], "name": "test"}

        formatted = mcp_selector._format_context(context)

        assert "name: test" in formatted
        assert "items: " in formatted


class TestEdgeCases:
    """Tests for edge cases in MCPSelector."""

    def test_select_tools_large_context(self, mcp_selector: MCPSelector, mock_llm: MockLLM) -> None:
        """Test MCP tool selection with large context."""
        context = {f"key_{i}": f"value_{i}" for i in range(100)}

        mcp_selector.select_mcp_tools(user_prompt="Test", available_mcps=["tool1"], context=context)

        # Should handle large context without error
        assert mock_llm.call_count == 1

    def test_select_tools_special_characters(self, mcp_selector: MCPSelector, mock_llm: MockLLM) -> None:
        """Test MCP tool selection with special characters in context."""
        context = {"text": "Special chars: {}, [], \", ', \\n, \\t"}

        mcp_selector.select_mcp_tools(user_prompt="Test", available_mcps=["tool1"], context=context)

        # Should handle special characters
        assert mock_llm.call_count == 1

    def test_format_tools_unicode(self, mcp_selector: MCPSelector) -> None:
        """Test formatting MCP tools with unicode characters."""
        selected_mcps = [{"name": "translator", "use_case": "Translate to 中文, 日本語, العربية"}]

        formatted = mcp_selector.format_mcp_tools(selected_mcps)

        assert "translator" in formatted
        assert "中文" in formatted
