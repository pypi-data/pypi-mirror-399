"""Unit tests for orchestrator ResultSynthesizer."""

from unittest.mock import MagicMock

import pytest

from fluxibly.llm.base import BaseLLM, LLMConfig
from fluxibly.orchestrator.synthesizer import ResultSynthesizer


class MockLLM(BaseLLM):
    """Mock LLM for testing."""

    def __init__(self, config: LLMConfig) -> None:
        super().__init__(config)
        self.call_count = 0
        self.last_prompt = None
        self.response = "Synthesized response"

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
def synthesizer_llm_strategy(mock_llm: MockLLM) -> ResultSynthesizer:
    """Create a ResultSynthesizer with LLM synthesis strategy."""
    return ResultSynthesizer(llm=mock_llm, synthesis_strategy="llm_synthesis")


@pytest.fixture
def synthesizer_concatenate(mock_llm: MockLLM) -> ResultSynthesizer:
    """Create a ResultSynthesizer with concatenate strategy."""
    return ResultSynthesizer(llm=mock_llm, synthesis_strategy="concatenate")


@pytest.fixture
def synthesizer_structured(mock_llm: MockLLM) -> ResultSynthesizer:
    """Create a ResultSynthesizer with structured strategy."""
    return ResultSynthesizer(llm=mock_llm, synthesis_strategy="structured")


class TestResultSynthesizerInitialization:
    """Tests for ResultSynthesizer initialization."""

    def test_init_llm_synthesis(self, mock_llm: MockLLM) -> None:
        """Test ResultSynthesizer initialization with llm_synthesis strategy."""
        synthesizer = ResultSynthesizer(llm=mock_llm, synthesis_strategy="llm_synthesis")

        assert synthesizer.llm == mock_llm
        assert synthesizer.synthesis_strategy == "llm_synthesis"
        assert synthesizer.prompt_loader is not None

    def test_init_concatenate(self, mock_llm: MockLLM) -> None:
        """Test ResultSynthesizer initialization with concatenate strategy."""
        synthesizer = ResultSynthesizer(llm=mock_llm, synthesis_strategy="concatenate")

        assert synthesizer.synthesis_strategy == "concatenate"

    def test_init_structured(self, mock_llm: MockLLM) -> None:
        """Test ResultSynthesizer initialization with structured strategy."""
        synthesizer = ResultSynthesizer(llm=mock_llm, synthesis_strategy="structured")

        assert synthesizer.synthesis_strategy == "structured"


class TestSynthesizeResultsLLM:
    """Tests for synthesize_results with LLM strategy."""

    def test_synthesize_with_llm_basic(self, synthesizer_llm_strategy: ResultSynthesizer, mock_llm: MockLLM) -> None:
        """Test LLM synthesis with basic results."""
        execution_results = {
            "step_results": {1: {"result": "First result"}, 2: {"result": "Second result"}},
            "errors": [],
            "task_complete": True,
        }

        mock_llm.response = "Combined analysis of results"

        result = synthesizer_llm_strategy.synthesize_results(execution_results)

        assert result == "Combined analysis of results"
        assert mock_llm.call_count == 1

    def test_synthesize_with_llm_and_errors(
        self, synthesizer_llm_strategy: ResultSynthesizer, mock_llm: MockLLM
    ) -> None:
        """Test LLM synthesis with errors present."""
        execution_results = {
            "step_results": {1: {"result": "Partial result"}},
            "errors": [{"step_id": 2, "error": "Connection failed"}],
            "task_complete": False,
        }

        result = synthesizer_llm_strategy.synthesize_results(execution_results)

        # Should include errors in synthesis
        assert isinstance(result, str)
        assert mock_llm.call_count == 1

    def test_synthesize_with_llm_failure_fallback(
        self, synthesizer_llm_strategy: ResultSynthesizer, mock_llm: MockLLM
    ) -> None:
        """Test LLM synthesis falls back to concatenation on failure."""
        execution_results = {
            "step_results": {1: {"result": "Result 1"}, 2: {"result": "Result 2"}},
            "errors": [],
            "task_complete": True,
        }

        mock_llm.forward = MagicMock(side_effect=Exception("LLM error"))

        result = synthesizer_llm_strategy.synthesize_results(execution_results)

        # Should fallback to concatenation
        assert "Step 1: Result 1" in result
        assert "Step 2: Result 2" in result

    def test_synthesize_with_llm_empty_results(
        self, synthesizer_llm_strategy: ResultSynthesizer, mock_llm: MockLLM
    ) -> None:
        """Test LLM synthesis with empty results."""
        execution_results = {"step_results": {}, "errors": [], "task_complete": True}

        result = synthesizer_llm_strategy.synthesize_results(execution_results)

        # Should still call LLM
        assert isinstance(result, str)


class TestSynthesizeResultsConcatenate:
    """Tests for synthesize_results with concatenate strategy."""

    def test_synthesize_concatenate_basic(self, synthesizer_concatenate: ResultSynthesizer) -> None:
        """Test concatenate synthesis with basic results."""
        execution_results = {
            "step_results": {1: {"result": "First result"}, 2: {"result": "Second result"}},
            "errors": [],
        }

        result = synthesizer_concatenate.synthesize_results(execution_results)

        assert "Step 1: First result" in result
        assert "Step 2: Second result" in result
        assert "\n\n" in result  # Should be separated

    def test_synthesize_concatenate_single_result(self, synthesizer_concatenate: ResultSynthesizer) -> None:
        """Test concatenate synthesis with single result."""
        execution_results = {"step_results": {1: {"result": "Only result"}}, "errors": []}

        result = synthesizer_concatenate.synthesize_results(execution_results)

        assert "Step 1: Only result" in result

    def test_synthesize_concatenate_empty_results(self, synthesizer_concatenate: ResultSynthesizer) -> None:
        """Test concatenate synthesis with empty results."""
        execution_results = {"step_results": {}, "errors": []}

        result = synthesizer_concatenate.synthesize_results(execution_results)

        assert result == "No results generated"

    def test_synthesize_concatenate_missing_result_field(self, synthesizer_concatenate: ResultSynthesizer) -> None:
        """Test concatenate synthesis handles missing result field."""
        execution_results = {"step_results": {1: {"status": "success"}, 2: {"result": "Has result"}}, "errors": []}

        result = synthesizer_concatenate.synthesize_results(execution_results)

        # Should only include step with result
        assert "Step 2: Has result" in result
        assert "Step 1" not in result

    def test_synthesize_concatenate_empty_result_values(self, synthesizer_concatenate: ResultSynthesizer) -> None:
        """Test concatenate synthesis with empty result values."""
        execution_results = {"step_results": {1: {"result": ""}, 2: {"result": None}}, "errors": []}

        result = synthesizer_concatenate.synthesize_results(execution_results)

        # Empty results should be filtered out
        assert result == "No results generated"


class TestSynthesizeResultsStructured:
    """Tests for synthesize_results with structured strategy."""

    def test_synthesize_structured_basic(self, synthesizer_structured: ResultSynthesizer) -> None:
        """Test structured synthesis returns valid JSON."""
        execution_results = {
            "step_results": {1: {"result": "Result 1"}},
            "errors": [],
            "task_complete": True,
        }

        result = synthesizer_structured.synthesize_results(execution_results)

        # Should be valid JSON
        import json

        parsed = json.loads(result)
        assert "step_results" in parsed
        assert "errors" in parsed
        assert "task_complete" in parsed
        assert parsed["task_complete"] is True

    def test_synthesize_structured_with_errors(self, synthesizer_structured: ResultSynthesizer) -> None:
        """Test structured synthesis includes errors."""
        execution_results = {
            "step_results": {1: {"result": "Result"}},
            "errors": [{"step_id": 2, "error": "Failed"}],
            "task_complete": False,
        }

        result = synthesizer_structured.synthesize_results(execution_results)

        import json

        parsed = json.loads(result)
        assert len(parsed["errors"]) == 1
        assert parsed["errors"][0]["step_id"] == 2
        assert parsed["task_complete"] is False

    def test_synthesize_structured_formatting(self, synthesizer_structured: ResultSynthesizer) -> None:
        """Test structured synthesis is properly formatted."""
        execution_results = {
            "step_results": {1: {"result": "Test"}},
            "errors": [],
            "task_complete": True,
        }

        result = synthesizer_structured.synthesize_results(execution_results)

        # Should be indented (indent=2 in implementation)
        assert "\n" in result  # Multi-line
        assert "  " in result  # Indented


class TestSynthesizeResultsEdgeCases:
    """Tests for edge cases in synthesize_results."""

    def test_synthesize_missing_step_results(self, synthesizer_llm_strategy: ResultSynthesizer) -> None:
        """Test synthesis handles missing step_results key."""
        execution_results = {"errors": [], "task_complete": True}

        result = synthesizer_llm_strategy.synthesize_results(execution_results)

        # Should handle gracefully
        assert isinstance(result, str)

    def test_synthesize_missing_errors(self, synthesizer_llm_strategy: ResultSynthesizer) -> None:
        """Test synthesis handles missing errors key."""
        execution_results = {"step_results": {1: {"result": "Test"}}, "task_complete": True}

        result = synthesizer_llm_strategy.synthesize_results(execution_results)

        assert isinstance(result, str)

    def test_synthesize_invalid_strategy_uses_llm(self, mock_llm: MockLLM) -> None:
        """Test synthesis with invalid strategy defaults to LLM."""
        synthesizer = ResultSynthesizer(llm=mock_llm, synthesis_strategy="invalid_strategy")
        execution_results = {"step_results": {1: {"result": "Test"}}, "errors": []}

        synthesizer.synthesize_results(execution_results)

        # Should default to LLM synthesis
        assert mock_llm.call_count == 1

    def test_synthesize_large_results(self, synthesizer_concatenate: ResultSynthesizer) -> None:
        """Test synthesis handles large number of results."""
        step_results = {i: {"result": f"Result {i}"} for i in range(1, 101)}
        execution_results = {"step_results": step_results, "errors": []}

        result = synthesizer_concatenate.synthesize_results(execution_results)

        # Should concatenate all results
        assert "Step 1: Result 1" in result
        assert "Step 100: Result 100" in result

    def test_synthesize_with_complex_result_objects(self, synthesizer_structured: ResultSynthesizer) -> None:
        """Test synthesis with complex nested result objects."""
        execution_results = {
            "step_results": {1: {"result": {"nested": {"data": [1, 2, 3]}, "status": "ok"}}},
            "errors": [],
            "task_complete": True,
        }

        result = synthesizer_structured.synthesize_results(execution_results)

        import json

        parsed = json.loads(result)
        # JSON converts integer keys to strings
        assert parsed["step_results"]["1"]["result"]["nested"]["data"] == [1, 2, 3]


class TestLLMSynthesisFallback:
    """Tests for LLM synthesis fallback behavior."""

    def test_llm_synthesis_fallback_with_errors(
        self, synthesizer_llm_strategy: ResultSynthesizer, mock_llm: MockLLM
    ) -> None:
        """Test LLM synthesis fallback includes error text."""
        execution_results = {
            "step_results": {1: {"result": "Result 1"}},
            "errors": [{"error": "Something failed"}],
            "task_complete": False,
        }

        mock_llm.forward = MagicMock(side_effect=Exception("LLM failed"))

        result = synthesizer_llm_strategy.synthesize_results(execution_results)

        # Fallback should include results
        assert "Step 1: Result 1" in result
        # And mention the synthesis error
        assert "Synthesis error" in result or "LLM failed" in result

    def test_llm_synthesis_fallback_empty_results(
        self, synthesizer_llm_strategy: ResultSynthesizer, mock_llm: MockLLM
    ) -> None:
        """Test LLM synthesis fallback with empty results."""
        execution_results = {"step_results": {}, "errors": [], "task_complete": True}

        mock_llm.forward = MagicMock(side_effect=Exception("LLM failed"))

        result = synthesizer_llm_strategy.synthesize_results(execution_results)

        # Should gracefully handle empty results
        assert isinstance(result, str)
