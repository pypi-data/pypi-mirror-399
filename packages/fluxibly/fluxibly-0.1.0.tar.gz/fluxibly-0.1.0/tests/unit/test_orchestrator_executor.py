"""Unit tests for orchestrator PlanExecutor and ErrorRecoveryHandler."""

from unittest.mock import MagicMock

import pytest

from fluxibly.llm.base import BaseLLM, LLMConfig
from fluxibly.orchestrator.executor import ErrorRecoveryHandler, PlanExecutor


class MockLLM(BaseLLM):
    """Mock LLM for testing."""

    def __init__(self, config: LLMConfig) -> None:
        super().__init__(config)
        self.call_count = 0
        self.last_prompt = None
        self.response = "LLM response"

    def forward(self, prompt: str, **kwargs) -> str:  # noqa: ARG002
        """Mock forward method."""
        self.call_count += 1
        self.last_prompt = prompt
        return self.response


class MockMCPClientManager:
    """Mock MCP client manager for testing."""

    def __init__(self) -> None:
        self.invoked_tools = []
        self.should_fail = False
        self.fail_count = 0

    async def invoke_tool(self, tool_name: str, tool_args: dict) -> str:
        """Mock tool invocation."""
        self.invoked_tools.append((tool_name, tool_args))
        if self.should_fail:
            self.fail_count += 1
            raise RuntimeError(f"Tool {tool_name} failed")
        return f"Result from {tool_name}"


@pytest.fixture
def mock_llm() -> MockLLM:
    """Create a mock LLM for testing."""
    config = LLMConfig(model="gpt-4o")
    return MockLLM(config=config)


@pytest.fixture
def mock_mcp_manager() -> MockMCPClientManager:
    """Create a mock MCP client manager."""
    return MockMCPClientManager()


@pytest.fixture
def plan_executor(mock_llm: MockLLM, mock_mcp_manager: MockMCPClientManager) -> PlanExecutor:
    """Create a PlanExecutor with mocks."""
    return PlanExecutor(llm=mock_llm, mcp_client_manager=mock_mcp_manager)


@pytest.fixture
def error_handler(mock_llm: MockLLM) -> ErrorRecoveryHandler:
    """Create an ErrorRecoveryHandler with mock LLM."""
    return ErrorRecoveryHandler(llm=mock_llm, error_recovery_strategy="retry_with_fallback")


class TestPlanExecutorInitialization:
    """Tests for PlanExecutor initialization."""

    def test_init_with_mcp_manager(self, mock_llm: MockLLM, mock_mcp_manager: MockMCPClientManager) -> None:
        """Test PlanExecutor initialization with MCP manager."""
        executor = PlanExecutor(llm=mock_llm, mcp_client_manager=mock_mcp_manager)

        assert executor.llm == mock_llm
        assert executor.mcp_client_manager == mock_mcp_manager
        assert executor.prompt_loader is not None

    def test_init_without_mcp_manager(self, mock_llm: MockLLM) -> None:
        """Test PlanExecutor initialization without MCP manager."""
        executor = PlanExecutor(llm=mock_llm)

        assert executor.llm == mock_llm
        assert executor.mcp_client_manager is None


class TestExecutePlan:
    """Tests for execute_plan method."""

    @pytest.mark.anyio
    async def test_execute_plan_single_llm_step(self, plan_executor: PlanExecutor, mock_llm: MockLLM) -> None:
        """Test executing a plan with a single LLM step."""
        plan = [{"step_id": 1, "description": "Analyze data", "tool": None, "dependencies": []}]

        mock_llm.response = "Analysis complete"

        results = await plan_executor.execute_plan(plan)

        assert results["task_complete"] is True
        assert len(results["step_results"]) == 1
        assert results["step_results"][1]["result"] == "Analysis complete"
        assert results["step_results"][1]["status"] == "success"
        assert len(results["errors"]) == 0

    @pytest.mark.anyio
    async def test_execute_plan_single_tool_step(
        self, plan_executor: PlanExecutor, mock_mcp_manager: MockMCPClientManager
    ) -> None:
        """Test executing a plan with a single tool step."""
        plan = [
            {"step_id": 1, "description": "Extract text", "tool": "ocr", "tool_args": {"page": 1}, "dependencies": []}
        ]

        results = await plan_executor.execute_plan(plan)

        assert results["task_complete"] is True
        assert len(results["step_results"]) == 1
        assert "Result from ocr" in results["step_results"][1]["result"]
        assert len(mock_mcp_manager.invoked_tools) == 1
        assert mock_mcp_manager.invoked_tools[0][0] == "ocr"

    @pytest.mark.anyio
    async def test_execute_plan_multiple_steps(
        self, plan_executor: PlanExecutor, mock_mcp_manager: MockMCPClientManager
    ) -> None:
        """Test executing a plan with multiple sequential steps."""
        plan = [
            {"step_id": 1, "description": "Step 1", "tool": "tool1", "tool_args": {}, "dependencies": []},
            {"step_id": 2, "description": "Step 2", "tool": "tool2", "tool_args": {}, "dependencies": [1]},
            {"step_id": 3, "description": "Step 3", "tool": "tool3", "tool_args": {}, "dependencies": [2]},
        ]

        results = await plan_executor.execute_plan(plan)

        assert results["task_complete"] is True
        assert len(results["step_results"]) == 3
        assert len(mock_mcp_manager.invoked_tools) == 3
        # Verify execution order
        assert mock_mcp_manager.invoked_tools[0][0] == "tool1"
        assert mock_mcp_manager.invoked_tools[1][0] == "tool2"
        assert mock_mcp_manager.invoked_tools[2][0] == "tool3"

    @pytest.mark.anyio
    async def test_execute_plan_with_dependencies(self, plan_executor: PlanExecutor) -> None:
        """Test executing a plan respects dependencies."""
        plan = [
            {"step_id": 1, "description": "First", "tool": "tool1", "dependencies": []},
            {"step_id": 2, "description": "Second", "tool": "tool2", "dependencies": [1]},
        ]

        results = await plan_executor.execute_plan(plan)

        # Should execute successfully respecting dependencies
        assert results["task_complete"] is True
        assert 1 in results["step_results"]
        assert 2 in results["step_results"]

    @pytest.mark.anyio
    async def test_execute_plan_unsatisfied_dependency(self, plan_executor: PlanExecutor) -> None:
        """Test executing a plan with unsatisfied dependencies fails."""
        # Step 2 depends on step 99 which doesn't exist
        plan = [
            {"step_id": 1, "description": "First", "tool": "tool1", "dependencies": []},
            {"step_id": 2, "description": "Second", "tool": "tool2", "dependencies": [99]},
        ]

        results = await plan_executor.execute_plan(plan)

        # Step 1 should succeed, step 2 should fail
        assert results["task_complete"] is False
        assert 1 in results["step_results"]
        assert results["step_results"][1]["status"] == "success"
        assert results["step_results"][2]["status"] == "failed"
        assert len(results["errors"]) == 1

    @pytest.mark.anyio
    async def test_execute_plan_tool_failure(
        self, plan_executor: PlanExecutor, mock_mcp_manager: MockMCPClientManager
    ) -> None:
        """Test executing a plan handles tool failures."""
        mock_mcp_manager.should_fail = True

        plan = [{"step_id": 1, "description": "Failing step", "tool": "failing_tool", "dependencies": []}]

        results = await plan_executor.execute_plan(plan)

        assert results["task_complete"] is False
        assert len(results["errors"]) == 1
        assert results["errors"][0]["step_id"] == 1
        assert results["step_results"][1]["status"] == "failed"

    @pytest.mark.anyio
    async def test_execute_plan_mixed_steps(
        self, plan_executor: PlanExecutor, mock_llm: MockLLM, mock_mcp_manager: MockMCPClientManager
    ) -> None:
        """Test executing a plan with both LLM and tool steps."""
        plan = [
            {"step_id": 1, "description": "Analyze", "tool": None, "dependencies": []},
            {"step_id": 2, "description": "Extract", "tool": "ocr", "tool_args": {}, "dependencies": [1]},
            {"step_id": 3, "description": "Summarize", "tool": None, "dependencies": [2]},
        ]

        results = await plan_executor.execute_plan(plan)

        assert results["task_complete"] is True
        assert len(results["step_results"]) == 3
        # Steps 1 and 3 should use LLM
        assert mock_llm.call_count == 2
        # Step 2 should use MCP tool
        assert len(mock_mcp_manager.invoked_tools) == 1

    @pytest.mark.anyio
    async def test_execute_plan_with_context(self, plan_executor: PlanExecutor, mock_llm: MockLLM) -> None:
        """Test executing a plan passes context to steps."""
        plan = [{"step_id": 1, "description": "Test", "tool": None, "dependencies": []}]
        context = {"user_id": "123", "document": "report.pdf"}

        results = await plan_executor.execute_plan(plan, context=context)

        assert results["context"] == context
        # Context should be passed to LLM step
        assert "user_id" in mock_llm.last_prompt or "document" in mock_llm.last_prompt

    @pytest.mark.anyio
    async def test_execute_plan_empty_plan(self, plan_executor: PlanExecutor) -> None:
        """Test executing an empty plan."""
        plan = []

        results = await plan_executor.execute_plan(plan)

        assert results["task_complete"] is True
        assert len(results["step_results"]) == 0
        assert len(results["errors"]) == 0


class TestInvokeMCPTool:
    """Tests for _invoke_mcp_tool method."""

    @pytest.mark.anyio
    async def test_invoke_mcp_tool_success(
        self, plan_executor: PlanExecutor, mock_mcp_manager: MockMCPClientManager
    ) -> None:
        """Test successful MCP tool invocation."""
        result = await plan_executor._invoke_mcp_tool("test_tool", {"arg": "value"})

        assert "Result from test_tool" in result
        assert len(mock_mcp_manager.invoked_tools) == 1
        assert mock_mcp_manager.invoked_tools[0] == ("test_tool", {"arg": "value"})

    @pytest.mark.anyio
    async def test_invoke_mcp_tool_without_manager(self, mock_llm: MockLLM) -> None:
        """Test tool invocation without MCP manager returns None."""
        executor = PlanExecutor(llm=mock_llm, mcp_client_manager=None)

        result = await executor._invoke_mcp_tool("test_tool", {})

        assert result is None

    @pytest.mark.anyio
    async def test_invoke_mcp_tool_failure(
        self, plan_executor: PlanExecutor, mock_mcp_manager: MockMCPClientManager
    ) -> None:
        """Test MCP tool invocation failure raises exception."""
        mock_mcp_manager.should_fail = True

        with pytest.raises(RuntimeError, match="Tool test_tool failed"):
            await plan_executor._invoke_mcp_tool("test_tool", {})


class TestExecuteLLMStep:
    """Tests for _execute_llm_step method."""

    def test_execute_llm_step(self, plan_executor: PlanExecutor, mock_llm: MockLLM) -> None:
        """Test executing LLM step."""
        mock_llm.response = "Step completed"
        step_results = {1: {"result": "Previous result"}}
        context = {"key": "value"}

        result = plan_executor._execute_llm_step("Test step", step_results, context)

        assert result == "Step completed"
        assert mock_llm.call_count == 1
        assert "Test step" in mock_llm.last_prompt


class TestErrorRecoveryHandlerInitialization:
    """Tests for ErrorRecoveryHandler initialization."""

    def test_init_retry_with_fallback(self, mock_llm: MockLLM) -> None:
        """Test ErrorRecoveryHandler initialization with retry_with_fallback strategy."""
        handler = ErrorRecoveryHandler(llm=mock_llm, error_recovery_strategy="retry_with_fallback")

        assert handler.llm == mock_llm
        assert handler.error_recovery_strategy == "retry_with_fallback"

    def test_init_abort_strategy(self, mock_llm: MockLLM) -> None:
        """Test ErrorRecoveryHandler initialization with abort strategy."""
        handler = ErrorRecoveryHandler(llm=mock_llm, error_recovery_strategy="abort")

        assert handler.error_recovery_strategy == "abort"


class TestHandleError:
    """Tests for handle_error method."""

    def test_handle_error_abort_strategy(self, mock_llm: MockLLM) -> None:
        """Test error handling with abort strategy."""
        handler = ErrorRecoveryHandler(llm=mock_llm, error_recovery_strategy="abort")
        error = RuntimeError("Test error")

        recovery = handler.handle_error(error, context={"step_id": 1})

        assert recovery["action"] == "abort"
        assert "error" in recovery
        assert recovery["error"]["error_type"] == "RuntimeError"

    def test_handle_error_skip_strategy(self, mock_llm: MockLLM) -> None:
        """Test error handling with skip strategy."""
        handler = ErrorRecoveryHandler(llm=mock_llm, error_recovery_strategy="skip")
        error = ValueError("Test error")

        recovery = handler.handle_error(error, context={"step_id": 1})

        assert recovery["action"] == "skip"
        assert "error" in recovery

    def test_handle_error_retry_strategy(self, mock_llm: MockLLM) -> None:
        """Test error handling with retry strategy."""
        handler = ErrorRecoveryHandler(llm=mock_llm, error_recovery_strategy="retry")
        error = ConnectionError("Network timeout")

        recovery = handler.handle_error(error, context={"step_id": 1, "retry_count": 0})

        assert recovery["action"] == "retry"
        assert recovery["retry_count"] == 1

    def test_handle_error_retry_max_exceeded(self, mock_llm: MockLLM) -> None:
        """Test error handling when max retries exceeded."""
        handler = ErrorRecoveryHandler(llm=mock_llm, error_recovery_strategy="retry")
        error = ConnectionError("Network timeout")

        # Simulate max retries (default is 3)
        recovery = handler.handle_error(error, context={"step_id": 1, "retry_count": 3})

        assert recovery["action"] == "abort"

    def test_handle_error_fallback_strategy(self, mock_llm: MockLLM) -> None:
        """Test error handling with fallback strategy."""
        handler = ErrorRecoveryHandler(llm=mock_llm, error_recovery_strategy="fallback")
        error = RuntimeError("Tool failed")

        recovery = handler.handle_error(error, context={"step_id": 1})

        # Fallback currently returns skip action
        assert recovery["action"] == "skip"
        assert mock_llm.call_count == 1  # LLM should be called for fallback

    def test_handle_error_retry_with_fallback_first_attempt(self, mock_llm: MockLLM) -> None:
        """Test retry_with_fallback strategy on first error."""
        handler = ErrorRecoveryHandler(llm=mock_llm, error_recovery_strategy="retry_with_fallback")
        error = RuntimeError("First failure")

        recovery = handler.handle_error(error, context={"step_id": 1, "retry_count": 0})

        # Should retry first
        assert recovery["action"] == "retry"
        assert recovery["retry_count"] == 1

    def test_handle_error_retry_with_fallback_exhausted(self, mock_llm: MockLLM) -> None:
        """Test retry_with_fallback strategy when retries exhausted."""
        handler = ErrorRecoveryHandler(llm=mock_llm, error_recovery_strategy="retry_with_fallback")
        error = RuntimeError("Still failing")

        recovery = handler.handle_error(error, context={"step_id": 1, "retry_count": 3})

        # Should fallback when retries exhausted
        assert recovery["action"] == "skip"  # Fallback currently returns skip
        assert mock_llm.call_count == 1  # LLM called for fallback

    def test_handle_error_unknown_strategy(self, mock_llm: MockLLM) -> None:
        """Test error handling with unknown strategy defaults to abort."""
        handler = ErrorRecoveryHandler(llm=mock_llm, error_recovery_strategy="unknown_strategy")
        error = RuntimeError("Test error")

        recovery = handler.handle_error(error, context={})

        assert recovery["action"] == "abort"

    def test_handle_error_without_context(self, mock_llm: MockLLM) -> None:
        """Test error handling without context."""
        handler = ErrorRecoveryHandler(llm=mock_llm, error_recovery_strategy="skip")
        error = RuntimeError("Test error")

        recovery = handler.handle_error(error)

        assert recovery["action"] == "skip"
        assert "error" in recovery


class TestHandleRetry:
    """Tests for _handle_retry method."""

    def test_handle_retry_under_limit(self, error_handler: ErrorRecoveryHandler) -> None:
        """Test retry when under retry limit."""
        error_info = {"error_type": "RuntimeError", "error_message": "Test"}
        context = {"retry_count": 1}

        recovery = error_handler._handle_retry(error_info, context)

        assert recovery["action"] == "retry"
        assert recovery["retry_count"] == 2

    def test_handle_retry_at_limit(self, error_handler: ErrorRecoveryHandler) -> None:
        """Test retry when at retry limit."""
        error_info = {"error_type": "RuntimeError", "error_message": "Test"}
        context = {"retry_count": 3}  # Default max is 3

        recovery = error_handler._handle_retry(error_info, context)

        assert recovery["action"] == "abort"

    def test_handle_retry_first_attempt(self, error_handler: ErrorRecoveryHandler) -> None:
        """Test retry on first attempt."""
        error_info = {"error_type": "RuntimeError", "error_message": "Test"}
        context = {"retry_count": 0}

        recovery = error_handler._handle_retry(error_info, context)

        assert recovery["action"] == "retry"
        assert recovery["retry_count"] == 1


class TestHandleFallback:
    """Tests for _handle_fallback method."""

    def test_handle_fallback_success(self, error_handler: ErrorRecoveryHandler, mock_llm: MockLLM) -> None:
        """Test fallback plan generation."""
        error = RuntimeError("Tool failed")
        error_info = {"error_type": "RuntimeError", "error_message": "Tool failed"}
        context = {"step_id": 1}

        mock_llm.response = "Fallback plan generated"

        recovery = error_handler._handle_fallback(error, error_info, context)

        # Currently fallback returns skip action
        assert recovery["action"] == "skip"
        assert mock_llm.call_count == 1

    def test_handle_fallback_llm_failure(self, error_handler: ErrorRecoveryHandler, mock_llm: MockLLM) -> None:
        """Test fallback when LLM fails."""
        error = RuntimeError("Tool failed")
        error_info = {"error_type": "RuntimeError", "error_message": "Tool failed"}
        context = {"step_id": 1}

        mock_llm.forward = MagicMock(side_effect=Exception("LLM error"))

        recovery = error_handler._handle_fallback(error, error_info, context)

        # Should gracefully handle LLM failure
        assert recovery["action"] == "skip"
