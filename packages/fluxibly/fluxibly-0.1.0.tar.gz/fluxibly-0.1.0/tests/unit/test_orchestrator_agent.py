"""Unit tests for OrchestratorAgent."""

from unittest.mock import AsyncMock, MagicMock

import pytest

from fluxibly.llm.base import BaseLLM, LLMConfig
from fluxibly.orchestrator.agent import OrchestratorAgent, OrchestratorConfig


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


class MockMCPClientManager:
    """Mock MCP client manager for testing."""

    def __init__(self) -> None:
        self.invoked_tools = []

    async def invoke_tool(self, tool_name: str, tool_args: dict) -> str:
        """Mock tool invocation."""
        self.invoked_tools.append((tool_name, tool_args))
        return f"Result from {tool_name}"


@pytest.fixture
def orchestrator_config() -> OrchestratorConfig:
    """Create a basic OrchestratorConfig for testing."""
    return OrchestratorConfig(
        name="test_orchestrator",
        llm=LLMConfig(model="gpt-4o", framework="langchain"),
        system_prompt="You are a test orchestrator.",
        mcp_servers=["ocr", "translation", "calculator"],
        max_iterations=3,
        plan_refinement_enabled=True,
        result_synthesis_strategy="llm_synthesis",
    )


@pytest.fixture
def mock_mcp_manager() -> MockMCPClientManager:
    """Create a mock MCP client manager."""
    return MockMCPClientManager()


@pytest.fixture
def orchestrator_agent(orchestrator_config: OrchestratorConfig, mock_mcp_manager: MockMCPClientManager, monkeypatch):
    """Create an OrchestratorAgent with mocked LLM."""
    # Mock the LLM constructor in agent.base module (where Agent gets it from)
    monkeypatch.setattr("fluxibly.agent.base.LLM", lambda config: MockLLM(config))

    return OrchestratorAgent(config=orchestrator_config, mcp_client_manager=mock_mcp_manager)


class TestOrchestratorAgentInitialization:
    """Tests for OrchestratorAgent initialization."""

    def test_init_basic(self, orchestrator_config: OrchestratorConfig, monkeypatch):
        """Test basic OrchestratorAgent initialization."""
        monkeypatch.setattr("fluxibly.agent.base.LLM", lambda config: MockLLM(config))

        agent = OrchestratorAgent(config=orchestrator_config)

        assert agent.config == orchestrator_config
        assert agent.current_plan is None
        assert agent.iteration_count == 0
        assert agent.planner is not None
        assert agent.executor is not None
        assert agent.synthesizer is not None
        assert agent.mcp_selector is not None
        assert agent.error_handler is not None

    def test_init_with_mcp_manager(self, orchestrator_config: OrchestratorConfig, mock_mcp_manager, monkeypatch):
        """Test initialization with MCP client manager."""
        monkeypatch.setattr("fluxibly.agent.base.LLM", lambda config: MockLLM(config))

        agent = OrchestratorAgent(config=orchestrator_config, mcp_client_manager=mock_mcp_manager)

        assert agent.mcp_client_manager == mock_mcp_manager
        assert agent.executor.mcp_client_manager == mock_mcp_manager

    def test_init_components(self, orchestrator_agent: OrchestratorAgent):
        """Test that all components are properly initialized."""
        assert orchestrator_agent.planner.llm is not None
        assert orchestrator_agent.executor.llm is not None
        assert orchestrator_agent.synthesizer.llm is not None
        assert orchestrator_agent.mcp_selector.llm is not None
        assert orchestrator_agent.error_handler.llm is not None

    def test_from_config_dict(self, monkeypatch):
        """Test creating OrchestratorAgent from config dictionary."""
        monkeypatch.setattr("fluxibly.agent.base.LLM", lambda config: MockLLM(config))

        config_dict = {
            "name": "dict_orchestrator",
            "llm": {"framework": "langchain", "model": "gpt-4o"},
            "system_prompt": "Test prompt",
            "mcp_servers": ["tool1"],
            "max_iterations": 5,
        }

        agent = OrchestratorAgent.from_config_dict(config_dict)

        assert agent.config.name == "dict_orchestrator"
        assert agent.config.max_iterations == 5


class TestPrepareSystem:
    """Tests for prepare_system method."""

    def test_prepare_system_basic(self, orchestrator_agent: OrchestratorAgent):
        """Test basic system preparation."""
        user_prompt = "Extract and translate PDF"

        system_ctx = orchestrator_agent.prepare_system(user_prompt)

        assert "system_prompt" in system_ctx
        assert "selected_mcps" in system_ctx
        assert "planning_context" in system_ctx
        assert "execution_params" in system_ctx
        assert orchestrator_agent.system_prompt in system_ctx["system_prompt"]

    def test_prepare_system_with_context(self, orchestrator_agent: OrchestratorAgent):
        """Test system preparation with context."""
        user_prompt = "Process document"
        context = {"document_type": "invoice", "language": "spanish"}

        system_ctx = orchestrator_agent.prepare_system(user_prompt, context=context)

        assert system_ctx["planning_context"]["context"] == context
        assert system_ctx["planning_context"]["user_prompt"] == user_prompt

    def test_prepare_system_includes_orchestration_params(self, orchestrator_agent: OrchestratorAgent):
        """Test system preparation includes orchestration parameters."""
        system_ctx = orchestrator_agent.prepare_system("Test task")

        system_prompt = system_ctx["system_prompt"]
        assert "Max Iterations" in system_prompt
        assert "Plan Refinement" in system_prompt
        assert "Parallel Execution" in system_prompt


class TestForward:
    """Tests for forward method."""

    @pytest.mark.anyio
    async def test_forward_basic_single_iteration(self, orchestrator_agent: OrchestratorAgent, monkeypatch):
        """Test basic forward execution with single iteration."""
        # Mock planner methods
        mock_analysis = {
            "objectives": ["test"],
            "required_capabilities": ["ocr"],
            "complexity": "low",
            "user_prompt": "Test",
            "context": {},
        }
        orchestrator_agent.planner.analyze_task = MagicMock(return_value=mock_analysis)

        mock_plan = [{"step_id": 1, "description": "Test step", "tool": None, "dependencies": []}]
        orchestrator_agent.planner.generate_plan = MagicMock(return_value=mock_plan)
        orchestrator_agent.planner.refine_plan = MagicMock(return_value=None)

        # Mock executor
        mock_results = {
            "step_results": {1: {"result": "Success"}},
            "errors": [],
            "task_complete": True,
        }
        orchestrator_agent.executor.execute_plan = AsyncMock(return_value=mock_results)

        # Mock synthesizer
        orchestrator_agent.synthesizer.synthesize_results = MagicMock(return_value="Final result")

        response = await orchestrator_agent.forward("Test task")

        assert response == "Final result"
        assert orchestrator_agent.iteration_count == 1
        assert orchestrator_agent.planner.analyze_task.called
        assert orchestrator_agent.planner.generate_plan.called
        assert orchestrator_agent.synthesizer.synthesize_results.called

    @pytest.mark.anyio
    async def test_forward_multiple_iterations(self, orchestrator_agent: OrchestratorAgent, monkeypatch):
        """Test forward with multiple plan refinement iterations."""
        # Mock planner
        mock_analysis = {"objectives": ["test"], "user_prompt": "Test", "context": {}}
        orchestrator_agent.planner.analyze_task = MagicMock(return_value=mock_analysis)

        mock_plan = [{"step_id": 1, "description": "Test", "tool": None}]
        orchestrator_agent.planner.generate_plan = MagicMock(return_value=mock_plan)

        # First refinement returns a new plan, second returns None (complete)
        refined_plan = [{"step_id": 2, "description": "Refined", "tool": None}]
        orchestrator_agent.planner.refine_plan = MagicMock(side_effect=[refined_plan, None])

        # Mock executor - first execution not complete, second complete
        mock_results_incomplete = {"step_results": {}, "errors": [{"error": "test"}], "task_complete": False}
        mock_results_complete = {"step_results": {2: {"result": "Done"}}, "errors": [], "task_complete": True}
        orchestrator_agent.executor.execute_plan = AsyncMock(
            side_effect=[mock_results_incomplete, mock_results_complete]
        )

        # Mock synthesizer
        orchestrator_agent.synthesizer.synthesize_results = MagicMock(return_value="Final result")

        response = await orchestrator_agent.forward("Test task")

        assert response == "Final result"
        assert orchestrator_agent.iteration_count == 2
        assert orchestrator_agent.executor.execute_plan.call_count == 2

    @pytest.mark.anyio
    async def test_forward_max_iterations(self, orchestrator_agent: OrchestratorAgent):
        """Test forward stops at max iterations."""
        # Set max iterations to 2
        orchestrator_agent.config.max_iterations = 2

        # Mock planner
        mock_analysis = {"objectives": ["test"], "user_prompt": "Test", "context": {}}
        orchestrator_agent.planner.analyze_task = MagicMock(return_value=mock_analysis)

        mock_plan = [{"step_id": 1, "description": "Test", "tool": None}]
        orchestrator_agent.planner.generate_plan = MagicMock(return_value=mock_plan)

        # Always refine (never complete)
        orchestrator_agent.planner.refine_plan = MagicMock(return_value=mock_plan)

        # Never mark as complete
        mock_results = {"step_results": {}, "errors": [{"error": "test"}], "task_complete": False}
        orchestrator_agent.executor.execute_plan = AsyncMock(return_value=mock_results)

        orchestrator_agent.synthesizer.synthesize_results = MagicMock(return_value="Incomplete")

        await orchestrator_agent.forward("Test task")

        # Should stop after max_iterations
        assert orchestrator_agent.iteration_count == 2
        assert orchestrator_agent.executor.execute_plan.call_count == 2

    @pytest.mark.anyio
    async def test_forward_with_context(self, orchestrator_agent: OrchestratorAgent):
        """Test forward passes context through execution."""
        context = {"user_id": "123", "document": "test.pdf"}

        # Mock components
        mock_analysis = {"objectives": ["test"], "user_prompt": "Test", "context": context}
        orchestrator_agent.planner.analyze_task = MagicMock(return_value=mock_analysis)

        mock_plan = [{"step_id": 1, "description": "Test", "tool": None}]
        orchestrator_agent.planner.generate_plan = MagicMock(return_value=mock_plan)

        mock_results = {"step_results": {1: {"result": "Success"}}, "errors": [], "task_complete": True}
        orchestrator_agent.executor.execute_plan = AsyncMock(return_value=mock_results)

        orchestrator_agent.synthesizer.synthesize_results = MagicMock(return_value="Final")

        await orchestrator_agent.forward("Test", context=context)

        # Check context was passed to executor
        call_args = orchestrator_agent.executor.execute_plan.call_args
        assert "execution_history" in call_args[0][1]  # context parameter

    @pytest.mark.anyio
    async def test_forward_stores_execution_history(self, orchestrator_agent: OrchestratorAgent):
        """Test forward stores execution history in context."""
        # Mock components
        mock_analysis = {"objectives": ["test"], "user_prompt": "Test", "context": {}}
        orchestrator_agent.planner.analyze_task = MagicMock(return_value=mock_analysis)

        mock_plan = [{"step_id": 1, "description": "Test", "tool": None}]
        orchestrator_agent.planner.generate_plan = MagicMock(return_value=mock_plan)

        mock_results = {"step_results": {1: {"result": "Success"}}, "errors": [], "task_complete": True}
        orchestrator_agent.executor.execute_plan = AsyncMock(return_value=mock_results)

        orchestrator_agent.synthesizer.synthesize_results = MagicMock(return_value="Final")

        await orchestrator_agent.forward("Test")

        # Check execution history was populated
        call_args = orchestrator_agent.executor.execute_plan.call_args
        context = call_args[0][1]
        assert "execution_history" in context
        assert len(context["execution_history"]) > 0

    @pytest.mark.anyio
    async def test_forward_error_recovery(self, orchestrator_agent: OrchestratorAgent):
        """Test forward handles execution errors with error recovery."""
        # Mock planner
        mock_analysis = {"objectives": ["test"], "user_prompt": "Test", "context": {}}
        orchestrator_agent.planner.analyze_task = MagicMock(return_value=mock_analysis)

        mock_plan = [{"step_id": 1, "description": "Test", "tool": None}]
        orchestrator_agent.planner.generate_plan = MagicMock(return_value=mock_plan)
        orchestrator_agent.planner.refine_plan = MagicMock(return_value=None)

        # Executor raises exception - will trigger error recovery
        orchestrator_agent.executor.execute_plan = AsyncMock(side_effect=RuntimeError("Execution failed"))

        # Error handler returns abort action
        orchestrator_agent.error_handler.handle_error = MagicMock(return_value={"action": "abort", "error": {}})

        # Error handler should abort (raise the exception)
        with pytest.raises(RuntimeError, match="Execution failed"):
            await orchestrator_agent.forward("Test")

        assert orchestrator_agent.error_handler.handle_error.called


class TestOrchestratorConfig:
    """Tests for OrchestratorConfig."""

    def test_config_defaults(self):
        """Test OrchestratorConfig default values."""
        config = OrchestratorConfig(
            name="test", llm=LLMConfig(model="gpt-4o", framework="langchain"), system_prompt="Test"
        )

        assert config.max_iterations == 5
        assert config.plan_refinement_enabled is True
        assert config.result_synthesis_strategy == "llm_synthesis"
        assert config.enable_parallel_execution is True
        assert config.plan_validation_enabled is True
        assert config.error_recovery_strategy == "retry_with_fallback"

    def test_config_custom_values(self):
        """Test OrchestratorConfig with custom values."""
        config = OrchestratorConfig(
            name="test",
            llm=LLMConfig(model="gpt-4o", framework="langchain"),
            system_prompt="Test",
            max_iterations=10,
            plan_refinement_enabled=False,
            result_synthesis_strategy="concatenate",
            error_recovery_strategy="abort",
        )

        assert config.max_iterations == 10
        assert config.plan_refinement_enabled is False
        assert config.result_synthesis_strategy == "concatenate"
        assert config.error_recovery_strategy == "abort"


class TestUtilityMethods:
    """Tests for utility methods."""

    def test_repr(self, orchestrator_agent: OrchestratorAgent):
        """Test string representation."""
        repr_str = repr(orchestrator_agent)

        assert "OrchestratorAgent" in repr_str
        assert "test_orchestrator" in repr_str
        assert "gpt-4o" in repr_str
        assert str(len(orchestrator_agent.mcp_servers)) in repr_str


class TestIntegrationScenarios:
    """Integration-style tests for complete workflows."""

    @pytest.mark.anyio
    async def test_complete_workflow_no_refinement(self, orchestrator_agent: OrchestratorAgent):
        """Test complete workflow without plan refinement."""
        # Mock all components for a successful single-pass execution
        mock_analysis = {"objectives": ["extract_text"], "user_prompt": "Extract text", "context": {}}
        orchestrator_agent.planner.analyze_task = MagicMock(return_value=mock_analysis)

        mock_plan = [{"step_id": 1, "description": "Extract with OCR", "tool": "ocr", "tool_args": {}}]
        orchestrator_agent.planner.generate_plan = MagicMock(return_value=mock_plan)

        mock_results = {
            "step_results": {1: {"result": "Extracted text content"}},
            "errors": [],
            "task_complete": True,
        }
        orchestrator_agent.executor.execute_plan = AsyncMock(return_value=mock_results)

        orchestrator_agent.synthesizer.synthesize_results = MagicMock(return_value="Successfully extracted text")

        response = await orchestrator_agent.forward("Extract text from PDF")

        assert response == "Successfully extracted text"
        assert orchestrator_agent.iteration_count == 1

    @pytest.mark.anyio
    async def test_complete_workflow_with_refinement(self, orchestrator_agent: OrchestratorAgent):
        """Test complete workflow with plan refinement."""
        # Mock planner
        mock_analysis = {"objectives": ["process_doc"], "user_prompt": "Process", "context": {}}
        orchestrator_agent.planner.analyze_task = MagicMock(return_value=mock_analysis)

        initial_plan = [{"step_id": 1, "description": "Initial step", "tool": None}]
        refined_plan = [{"step_id": 2, "description": "Refined step", "tool": None}]

        orchestrator_agent.planner.generate_plan = MagicMock(return_value=initial_plan)
        orchestrator_agent.planner.refine_plan = MagicMock(side_effect=[refined_plan, None])

        # First execution has errors, second succeeds
        results_with_error = {"step_results": {}, "errors": [{"error": "failed"}], "task_complete": False}
        results_success = {"step_results": {2: {"result": "Success"}}, "errors": [], "task_complete": True}

        orchestrator_agent.executor.execute_plan = AsyncMock(side_effect=[results_with_error, results_success])

        orchestrator_agent.synthesizer.synthesize_results = MagicMock(return_value="Task completed after refinement")

        response = await orchestrator_agent.forward("Process document")

        assert response == "Task completed after refinement"
        assert orchestrator_agent.iteration_count == 2
