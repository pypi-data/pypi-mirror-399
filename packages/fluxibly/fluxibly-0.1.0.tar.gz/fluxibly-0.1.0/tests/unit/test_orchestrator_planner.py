"""Unit tests for orchestrator TaskPlanner."""

from unittest.mock import MagicMock

import pytest

from fluxibly.llm.base import BaseLLM, LLMConfig
from fluxibly.orchestrator.planner import TaskPlanner


class MockLLM(BaseLLM):
    """Mock LLM for testing."""

    def __init__(self, config: LLMConfig) -> None:
        super().__init__(config)
        self.call_count = 0
        self.last_prompt = None
        self.response = '{"objectives": ["test"], "complexity": "low"}'

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
def task_planner(mock_llm: MockLLM) -> TaskPlanner:
    """Create a TaskPlanner with mock LLM."""
    return TaskPlanner(llm=mock_llm, mcp_servers=["ocr", "translation", "calculator"])


class TestTaskPlannerInitialization:
    """Tests for TaskPlanner initialization."""

    def test_init(self, mock_llm: MockLLM) -> None:
        """Test TaskPlanner initialization."""
        planner = TaskPlanner(llm=mock_llm, mcp_servers=["tool1", "tool2"])

        assert planner.llm == mock_llm
        assert planner.mcp_servers == ["tool1", "tool2"]
        assert planner.prompt_loader is not None

    def test_init_with_empty_mcp_servers(self, mock_llm: MockLLM) -> None:
        """Test TaskPlanner initialization with empty MCP servers."""
        planner = TaskPlanner(llm=mock_llm, mcp_servers=[])

        assert planner.mcp_servers == []


class TestAnalyzeTask:
    """Tests for analyze_task method."""

    def test_analyze_task_basic(self, task_planner: TaskPlanner, mock_llm: MockLLM) -> None:
        """Test basic task analysis."""
        mock_llm.response = """
        {
            "objectives": ["extract_text", "translate"],
            "required_capabilities": ["ocr", "translation"],
            "complexity": "medium",
            "suggested_strategy": "sequential",
            "dependencies": {"translate": ["extract_text"]}
        }
        """

        analysis = task_planner.analyze_task("Extract and translate PDF")

        assert analysis["objectives"] == ["extract_text", "translate"]
        assert analysis["required_capabilities"] == ["ocr", "translation"]
        assert analysis["complexity"] == "medium"
        assert analysis["suggested_strategy"] == "sequential"
        assert analysis["dependencies"] == {"translate": ["extract_text"]}
        assert analysis["user_prompt"] == "Extract and translate PDF"
        assert mock_llm.call_count == 1

    def test_analyze_task_with_context(self, task_planner: TaskPlanner, mock_llm: MockLLM) -> None:
        """Test task analysis with context."""
        context = {"document_type": "invoice", "language": "spanish"}

        analysis = task_planner.analyze_task("Process invoice", context=context)

        assert analysis["context"] == context
        assert "invoice" in mock_llm.last_prompt or "spanish" in mock_llm.last_prompt

    def test_analyze_task_with_invalid_json(self, task_planner: TaskPlanner, mock_llm: MockLLM) -> None:
        """Test task analysis with invalid JSON response falls back to defaults."""
        mock_llm.response = "This is not valid JSON"

        analysis = task_planner.analyze_task("Some task")

        # Should return default analysis
        assert analysis["objectives"] == ["complete_user_task"]
        assert analysis["required_capabilities"] == task_planner.mcp_servers
        assert analysis["complexity"] == "medium"

    def test_analyze_task_with_no_json(self, task_planner: TaskPlanner, mock_llm: MockLLM) -> None:
        """Test task analysis with no JSON in response."""
        mock_llm.response = "Just plain text without any JSON structure"

        analysis = task_planner.analyze_task("Test task")

        # Should return default analysis
        assert analysis["objectives"] == ["complete_user_task"]
        assert analysis["user_prompt"] == "Test task"

    def test_analyze_task_with_partial_json(self, task_planner: TaskPlanner, mock_llm: MockLLM) -> None:
        """Test task analysis with partial JSON (missing fields)."""
        mock_llm.response = '{"objectives": ["custom_objective"]}'

        analysis = task_planner.analyze_task("Test task")

        assert analysis["objectives"] == ["custom_objective"]
        # Should have defaults for missing fields
        assert "required_capabilities" in analysis
        assert "complexity" in analysis

    def test_analyze_task_exception_handling(self, task_planner: TaskPlanner, mock_llm: MockLLM) -> None:
        """Test task analysis handles LLM exceptions."""
        mock_llm.forward = MagicMock(side_effect=Exception("LLM error"))

        analysis = task_planner.analyze_task("Test task")

        # Should return default analysis without raising
        assert analysis["objectives"] == ["complete_user_task"]
        assert analysis["user_prompt"] == "Test task"


class TestGeneratePlan:
    """Tests for generate_plan method."""

    def test_generate_plan_basic(self, task_planner: TaskPlanner, mock_llm: MockLLM) -> None:
        """Test basic plan generation."""
        task_analysis = {
            "user_prompt": "Extract and translate",
            "required_capabilities": ["ocr", "translation"],
            "objectives": ["extract", "translate"],
        }

        mock_llm.response = """
        [
            {
                "step_id": 1,
                "description": "Extract text using OCR",
                "tool": "ocr",
                "tool_args": {"page": 1},
                "dependencies": [],
                "parallel_group": 0
            },
            {
                "step_id": 2,
                "description": "Translate text",
                "tool": "translation",
                "tool_args": {"target": "es"},
                "dependencies": [1],
                "parallel_group": 0
            }
        ]
        """

        plan = task_planner.generate_plan(task_analysis)

        assert len(plan) == 2
        assert plan[0]["step_id"] == 1
        assert plan[0]["tool"] == "ocr"
        assert plan[0]["dependencies"] == []
        assert plan[1]["step_id"] == 2
        assert plan[1]["tool"] == "translation"
        assert plan[1]["dependencies"] == [1]

    def test_generate_plan_with_minimal_steps(self, task_planner: TaskPlanner, mock_llm: MockLLM) -> None:
        """Test plan generation with minimal step information."""
        task_analysis = {"user_prompt": "Simple task"}

        mock_llm.response = '[{"step_id": 1}]'

        plan = task_planner.generate_plan(task_analysis)

        assert len(plan) == 1
        # Should have defaults filled in
        assert plan[0]["step_id"] == 1
        assert "description" in plan[0]
        assert "tool" in plan[0]
        assert "dependencies" in plan[0]

    def test_generate_plan_with_invalid_json(self, task_planner: TaskPlanner, mock_llm: MockLLM) -> None:
        """Test plan generation with invalid JSON falls back to single-step plan."""
        task_analysis = {"user_prompt": "Test task"}

        mock_llm.response = "Not valid JSON"

        plan = task_planner.generate_plan(task_analysis)

        # Should return fallback plan
        assert len(plan) == 1
        assert plan[0]["step_id"] == 1
        assert "Test task" in plan[0]["description"]

    def test_generate_plan_with_no_json_array(self, task_planner: TaskPlanner, mock_llm: MockLLM) -> None:
        """Test plan generation with no JSON array in response."""
        task_analysis = {"user_prompt": "Test task"}

        mock_llm.response = '{"not": "an array"}'

        plan = task_planner.generate_plan(task_analysis)

        # Should return fallback plan
        assert len(plan) == 1

    def test_generate_plan_with_empty_array(self, task_planner: TaskPlanner, mock_llm: MockLLM) -> None:
        """Test plan generation with empty array falls back."""
        task_analysis = {"user_prompt": "Test task"}

        mock_llm.response = "[]"

        plan = task_planner.generate_plan(task_analysis)

        # Empty plan should trigger fallback
        assert len(plan) == 1

    def test_generate_plan_normalizes_steps(self, task_planner: TaskPlanner, mock_llm: MockLLM) -> None:
        """Test plan generation normalizes step structure."""
        task_analysis = {"user_prompt": "Test"}

        # Plan with some missing fields
        mock_llm.response = """
        [
            {"step_id": 1, "tool": "ocr"},
            {"step_id": 2, "description": "Custom desc", "tool_args": {"arg": "val"}}
        ]
        """

        plan = task_planner.generate_plan(task_analysis)

        # All steps should have complete structure
        for step in plan:
            assert "step_id" in step
            assert "description" in step
            assert "tool" in step
            assert "tool_args" in step
            assert "dependencies" in step
            assert "parallel_group" in step

    def test_generate_plan_filters_invalid_steps(self, task_planner: TaskPlanner, mock_llm: MockLLM) -> None:
        """Test plan generation filters out invalid steps."""
        task_analysis = {"user_prompt": "Test"}

        # Plan with invalid entries
        mock_llm.response = """
        [
            {"step_id": 1, "tool": "valid"},
            "invalid_string",
            {"no_step_id": "invalid"},
            {"step_id": 2, "tool": "also_valid"}
        ]
        """

        plan = task_planner.generate_plan(task_analysis)

        # Should only have 2 valid steps
        assert len(plan) == 2
        assert plan[0]["step_id"] == 1
        assert plan[1]["step_id"] == 2


class TestRefinePlan:
    """Tests for refine_plan method."""

    def test_refine_plan_when_task_complete(self, task_planner: TaskPlanner) -> None:
        """Test refine_plan returns None when task is complete."""
        current_plan = [{"step_id": 1, "description": "Done"}]
        execution_results = {"task_complete": True, "step_results": {1: {"result": "Success"}}}

        refined_plan = task_planner.refine_plan(current_plan, execution_results)

        assert refined_plan is None

    def test_refine_plan_when_no_errors(self, task_planner: TaskPlanner) -> None:
        """Test refine_plan returns None when no errors."""
        current_plan = [{"step_id": 1, "description": "Done"}]
        execution_results = {"task_complete": False, "errors": [], "step_results": {}}

        refined_plan = task_planner.refine_plan(current_plan, execution_results)

        assert refined_plan is None

    def test_refine_plan_with_errors(self, task_planner: TaskPlanner, mock_llm: MockLLM) -> None:
        """Test refine_plan generates new plan when errors present."""
        current_plan = [{"step_id": 1, "description": "Failed step"}]
        execution_results = {
            "task_complete": False,
            "errors": [{"step": 1, "error": "Connection timeout"}],
            "step_results": {},
        }

        mock_llm.response = """
        [
            {
                "step_id": 1,
                "description": "Retry with different approach",
                "tool": "alternative_tool",
                "dependencies": []
            }
        ]
        """

        refined_plan = task_planner.refine_plan(current_plan, execution_results)

        assert refined_plan is not None
        assert len(refined_plan) == 1
        assert refined_plan[0]["description"] == "Retry with different approach"

    def test_refine_plan_with_invalid_json(self, task_planner: TaskPlanner, mock_llm: MockLLM) -> None:
        """Test refine_plan returns None when LLM returns invalid JSON."""
        current_plan = [{"step_id": 1}]
        execution_results = {"task_complete": False, "errors": [{"error": "test"}]}

        mock_llm.response = "Not valid JSON"

        refined_plan = task_planner.refine_plan(current_plan, execution_results)

        assert refined_plan is None

    def test_refine_plan_with_empty_response(self, task_planner: TaskPlanner, mock_llm: MockLLM) -> None:
        """Test refine_plan returns None when LLM returns empty plan."""
        current_plan = [{"step_id": 1}]
        execution_results = {"task_complete": False, "errors": [{"error": "test"}]}

        mock_llm.response = "[]"

        refined_plan = task_planner.refine_plan(current_plan, execution_results)

        assert refined_plan is None

    def test_refine_plan_exception_handling(self, task_planner: TaskPlanner, mock_llm: MockLLM) -> None:
        """Test refine_plan handles LLM exceptions gracefully."""
        current_plan = [{"step_id": 1}]
        execution_results = {"task_complete": False, "errors": [{"error": "test"}]}

        mock_llm.forward = MagicMock(side_effect=Exception("LLM error"))

        refined_plan = task_planner.refine_plan(current_plan, execution_results)

        # Should return None without raising
        assert refined_plan is None


class TestNormalizePlan:
    """Tests for _normalize_plan helper method."""

    def test_normalize_plan_complete_steps(self, task_planner: TaskPlanner) -> None:
        """Test normalizing plan with complete step information."""
        raw_plan = [
            {
                "step_id": 1,
                "description": "First step",
                "tool": "tool1",
                "tool_args": {"arg": "val"},
                "dependencies": [],
                "parallel_group": 0,
            }
        ]

        normalized = task_planner._normalize_plan(raw_plan)

        assert len(normalized) == 1
        assert normalized[0] == raw_plan[0]

    def test_normalize_plan_missing_fields(self, task_planner: TaskPlanner) -> None:
        """Test normalizing plan fills in missing fields with defaults."""
        raw_plan = [{"step_id": 1, "tool": "tool1"}]

        normalized = task_planner._normalize_plan(raw_plan)

        assert len(normalized) == 1
        assert normalized[0]["step_id"] == 1
        assert normalized[0]["tool"] == "tool1"
        assert "description" in normalized[0]
        assert normalized[0]["tool_args"] == {}
        assert normalized[0]["dependencies"] == []
        assert normalized[0]["parallel_group"] == 0

    def test_normalize_plan_filters_invalid(self, task_planner: TaskPlanner) -> None:
        """Test normalizing plan filters out invalid entries."""
        raw_plan = [
            {"step_id": 1, "tool": "valid"},
            "invalid_string",
            None,
            {"no_step_id": "invalid"},
            {"step_id": 2, "tool": "also_valid"},
        ]

        normalized = task_planner._normalize_plan(raw_plan)

        assert len(normalized) == 2
        assert normalized[0]["step_id"] == 1
        assert normalized[1]["step_id"] == 2


class TestHelperMethods:
    """Tests for helper methods."""

    def test_get_default_analysis(self, task_planner: TaskPlanner) -> None:
        """Test getting default analysis structure."""
        context = {"key": "value"}

        analysis = task_planner._get_default_analysis("Test prompt", context)

        assert analysis["objectives"] == ["complete_user_task"]
        assert analysis["required_capabilities"] == task_planner.mcp_servers
        assert analysis["complexity"] == "medium"
        assert analysis["suggested_strategy"] == "sequential_execution"
        assert analysis["dependencies"] == {}
        assert analysis["user_prompt"] == "Test prompt"
        assert analysis["context"] == context

    def test_get_fallback_plan(self, task_planner: TaskPlanner) -> None:
        """Test getting fallback single-step plan."""
        plan = task_planner._get_fallback_plan("Execute this task")

        assert len(plan) == 1
        assert plan[0]["step_id"] == 1
        assert "Execute this task" in plan[0]["description"]
        assert plan[0]["tool"] is None
        assert plan[0]["tool_args"] == {}
        assert plan[0]["dependencies"] == []
        assert plan[0]["parallel_group"] == 0
