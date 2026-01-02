"""Orchestrator Agent for complex task planning and execution.

This module implements the OrchestratorAgent, a specialized Agent subclass that
provides sophisticated task planning, iterative execution, and advanced MCP tool
orchestration capabilities.

The OrchestratorAgent extends the base Agent class with:
- Multi-step planning and plan refinement
- Advanced MCP tool selection and allocation
- Iterative execution with continuous plan upgrades
- Complex system prompt management
- Result synthesis across multiple tool calls

Use OrchestratorAgent when:
- Tasks require multi-step planning and coordination
- Complex MCP tool selection and orchestration is needed
- Iterative refinement and plan adjustment is necessary
- Multiple MCP tool results need to be synthesized

Use base Agent when:
- Simple, single-step tool calling is sufficient
- Basic MCP selection is adequate
- No planning or iteration is required

All initialization parameters are configurable via config files.
"""

from typing import TYPE_CHECKING, Any

from pydantic import Field

from fluxibly.agent.base import Agent, AgentConfig
from fluxibly.orchestrator.config.prompts import get_default_loader
from fluxibly.orchestrator.executor import ErrorRecoveryHandler, PlanExecutor
from fluxibly.orchestrator.planner import TaskPlanner
from fluxibly.orchestrator.selector import MCPSelector
from fluxibly.orchestrator.synthesizer import ResultSynthesizer

if TYPE_CHECKING:
    from fluxibly.mcp_client.manager import MCPClientManager


class OrchestratorConfig(AgentConfig):
    """Configuration for Orchestrator Agent initialization.

    Extends AgentConfig with additional parameters specific to orchestration.

    Attributes:
        max_iterations: Maximum planning/execution iterations
        plan_refinement_enabled: Whether to refine plan based on execution results
        result_synthesis_strategy: How to combine multiple tool results
        planning_agent: Optional separate agent for planning (can differ from execution agent)
        enable_parallel_execution: Execute independent plan steps in parallel
        plan_validation_enabled: Validate plan feasibility before execution
        error_recovery_strategy: How to handle and recover from failures
    """

    max_iterations: int = Field(default=5, description="Maximum planning/execution iterations")
    plan_refinement_enabled: bool = Field(default=True, description="Enable iterative plan refinement")
    result_synthesis_strategy: str = Field(
        default="llm_synthesis", description="Result synthesis strategy: 'llm_synthesis', 'concatenate', 'structured'"
    )
    planning_agent: AgentConfig | None = Field(default=None, description="Optional separate agent for planning")
    enable_parallel_execution: bool = Field(default=True, description="Execute independent steps in parallel")
    plan_validation_enabled: bool = Field(default=True, description="Validate plan before execution")
    error_recovery_strategy: str = Field(
        default="retry_with_fallback", description="Error recovery: 'retry_with_fallback', 'skip', 'abort'"
    )


class OrchestratorAgent(Agent):
    """Orchestrator Agent - specialized Agent for complex task orchestration.

    The OrchestratorAgent is a sophisticated extension of the base Agent class,
    designed for complex, multi-step tasks that require planning, coordination,
    and iterative refinement.

    Key Capabilities:
    1. Multi-step Planning: Break down complex tasks into executable steps
    2. Advanced MCP Selection: Sophisticated algorithms for tool selection
    3. Iterative Execution: Run, evaluate, and refine plans until task completion
    4. Result Synthesis: Intelligently combine outputs from multiple tools
    5. Error Recovery: Handle failures and adapt plans accordingly

    Workflow:
    1. User provides complex task
    2. prepare_system() creates detailed system prompt with MCP allocation strategy
    3. forward() initiates planning loop:
       a. Analyze task and generate execution plan
       b. Select and allocate appropriate MCP tools
       c. Execute plan steps (with parallelization if possible)
       d. Evaluate results and decide: complete or refine plan
       e. If refinement needed, update plan and iterate (up to max_iterations)
    4. Synthesize final results from all executions
    5. Return comprehensive response

    Differences from base Agent:
    - Agent: Simple, single-step tool calling with basic selection
    - Orchestrator: Multi-step planning, advanced selection, iterative execution

    Example:
        >>> from fluxibly.llm.base import LLMConfig
        >>> orchestrator_config = OrchestratorConfig(
        ...     name="document_processor",
        ...     llm=LLMConfig(model="gpt-4o", framework="langchain"),
        ...     system_prompt="You are an expert document processing orchestrator.",
        ...     mcp_servers=["ocr", "vision", "text_analysis"],
        ...     max_iterations=5,
        ...     plan_refinement_enabled=True
        ... )
        >>> orchestrator = OrchestratorAgent(config=orchestrator_config)
        >>> response = await orchestrator.forward(
        ...     user_prompt="Extract and analyze all data from this PDF invoice",
        ...     context={"document_path": "/path/to/invoice.pdf"}
        ... )

    Attributes:
        config: OrchestratorConfig with orchestration-specific parameters
        current_plan: The current execution plan (updated during iterations)
        iteration_count: Number of iterations executed so far
        planner: TaskPlanner instance for plan generation
        executor: PlanExecutor instance for plan execution
        synthesizer: ResultSynthesizer instance for result combination
        mcp_selector: MCPSelector instance for tool selection
        error_handler: ErrorRecoveryHandler instance for error management
    """

    def __init__(self, config: OrchestratorConfig, mcp_client_manager: "MCPClientManager | None" = None) -> None:
        """Initialize the Orchestrator Agent with configuration.

        Args:
            config: OrchestratorConfig object containing orchestrator parameters
                   including LLM config, system prompt, MCP servers, and
                   orchestration-specific settings.
            mcp_client_manager: Optional MCPClientManager instance for tool execution.

        Note:
            If planning_agent is specified in config, it will be used for planning
            operations while the main agent handles execution and synthesis.
        """
        super().__init__(config, mcp_client_manager=mcp_client_manager)
        self.config: OrchestratorConfig = config  # Type hint for orchestrator config
        self.current_plan: list[dict[str, Any]] | None = None
        self.iteration_count: int = 0

        # Initialize orchestrator components
        self.planner = TaskPlanner(self.llm, self.mcp_servers, mcp_client_manager)
        self.executor = PlanExecutor(self.llm, mcp_client_manager)
        self.synthesizer = ResultSynthesizer(self.llm, config.result_synthesis_strategy)
        self.mcp_selector = MCPSelector(self.llm)
        self.error_handler = ErrorRecoveryHandler(self.llm, config.error_recovery_strategy)

        # Load prompt templates
        self.prompt_loader = get_default_loader()

    def prepare_system(self, user_prompt: str, context: dict[str, Any] | None = None) -> dict[str, Any]:
        """Prepare complex system prompt and MCP allocation strategy.

        This method is more sophisticated than Agent.prepare(). It:
        1. Analyzes the user's task to understand requirements
        2. Creates a detailed system prompt with orchestration instructions
        3. Performs advanced MCP tool selection and allocation
        4. Prepares execution context with planning parameters

        Args:
            user_prompt: The user's complex task/request
            context: Optional context dictionary

        Returns:
            dict[str, Any]: Prepared system context containing:
                - system_prompt: Enhanced system instructions
                - selected_mcps: List of allocated MCP tools with priorities
                - planning_context: Context for plan generation
                - execution_params: Parameters for execution
        """
        context = context or {}

        # Perform advanced MCP selection using LLM-based semantic matching
        available_mcps = self.mcp_servers
        selected_mcps = self.mcp_selector.select_mcp_tools(user_prompt, available_mcps, context)

        # Build enhanced system prompt with orchestration instructions
        orchestration_instructions = self.prompt_loader.get_prompt("orchestration_instructions")
        enhanced_system_prompt = f"""{self.system_prompt}

{orchestration_instructions}

Available MCP Tools:
{self.mcp_selector.format_mcp_tools(selected_mcps)}

Orchestration Parameters:
- Max Iterations: {self.config.max_iterations}
- Plan Refinement: {"Enabled" if self.config.plan_refinement_enabled else "Disabled"}
- Parallel Execution: {"Enabled" if self.config.enable_parallel_execution else "Disabled"}
- Error Recovery: {self.config.error_recovery_strategy}
"""

        return {
            "system_prompt": enhanced_system_prompt,
            "selected_mcps": selected_mcps,
            "planning_context": {
                "user_prompt": user_prompt,
                "context": context,
                "available_tools": selected_mcps,
                "max_iterations": self.config.max_iterations,
            },
            "execution_params": {
                "enable_parallel": self.config.enable_parallel_execution,
                "timeout": self.config.mcp_timeout if hasattr(self.config, "mcp_timeout") else 30,
                "error_strategy": self.config.error_recovery_strategy,
            },
        }

    async def forward(self, user_prompt: str, context: dict[str, Any] | None = None) -> str:
        """Execute orchestrated multi-step task with planning and iteration.

        This overrides Agent.forward() with sophisticated orchestration logic.

        Args:
            user_prompt: The user's complex task/request
            context: Optional context dictionary

        Returns:
            str: Comprehensive response incorporating all tool results and iterations

        Raises:
            Exception: If maximum iterations exceeded without completion
            Exception: If critical MCP tool failures occur
        """
        context = context or {}

        # Include conversation history for stateful operation
        if self.config.enable_memory and hasattr(self, "conversation_history"):
            context["conversation_history"] = self.conversation_history

        # Store user message in conversation history
        if self.config.enable_memory and self.conversation_history is not None:
            self.conversation_history.add_user_message(user_prompt)

        context["execution_history"] = []
        self.iteration_count = 0

        # Step 1: Prepare system with advanced MCP selection
        _system_ctx = self.prepare_system(user_prompt, context)
        # TODO: Use system_ctx to enhance LLM calls with orchestration-specific prompts

        # Step 2: Analyze task to understand requirements
        task_analysis = self.planner.analyze_task(user_prompt, context)

        # Step 3: Generate initial plan (pass context for conversation history)
        self.current_plan = self.planner.generate_plan(task_analysis, context)

        # Step 3.5: Handle empty plan (follow-up questions that don't need tools)
        if not self.current_plan:  # None or empty list
            # Use LLM directly with conversation history to answer the question
            if self.config.enable_memory and self.conversation_history is not None:
                messages = self.conversation_history.get_messages()[-6:]
                history_parts = []

                for msg in messages:
                    role = msg.role.upper()
                    # Don't truncate for follow-up questions - we need full context
                    content = msg.content if len(msg.content) < 2000 else msg.content[:2000] + "..."
                    history_parts.append(f"{role}: {content}")

                history_text = "\n\n".join(history_parts)

                direct_prompt = f"""Based on the previous conversation, answer this follow-up question:

Previous Conversation:
{history_text}

Follow-up Question: {user_prompt}

IMPORTANT: Analyze the data that was already provided in the previous conversation.
For questions about "which is best", "which offers value", "which location", etc.,
compare the options that were already shown and provide a specific recommendation with reasoning.

Provide a direct, concise answer based on the information already available in the conversation history."""

                self._logger.debug(
                    f"Empty plan handler - using direct LLM query with history ({len(history_text)} chars)"
                )
                final_response = self.llm.forward(direct_prompt)

                # Store assistant response in conversation history
                if self.conversation_history is not None:
                    self.conversation_history.add_assistant_message(final_response)

                return final_response
            else:
                return "I don't have enough context to answer this question."

        # Step 4: Planning and execution loop
        execution_results = None
        while self.iteration_count < self.config.max_iterations:
            self.iteration_count += 1

            # Check that current_plan is not None before executing
            if self.current_plan is None:
                break

            try:
                # Execute the current plan
                execution_results = await self.executor.execute_plan(self.current_plan, context)

                # Add user_prompt to execution_results for synthesis
                execution_results["user_prompt"] = user_prompt

                # Store execution history
                context["execution_history"].append(
                    {
                        "iteration": self.iteration_count,
                        "plan": self.current_plan,
                        "results": execution_results,
                    }
                )

                # Check if task is complete
                if execution_results.get("task_complete", False):
                    break

                # If plan refinement is enabled, refine the plan for next iteration
                if self.config.plan_refinement_enabled and self.iteration_count < self.config.max_iterations:
                    refined_plan = self.planner.refine_plan(self.current_plan, execution_results)
                    if refined_plan is None:
                        # No refinement needed, task is complete
                        break
                    self.current_plan = refined_plan
                else:
                    # No refinement, exit loop
                    break

            except Exception as e:
                # Handle errors according to error recovery strategy
                recovery_action = self.error_handler.handle_error(
                    e, {"iteration": self.iteration_count, "plan": self.current_plan}
                )

                if recovery_action["action"] == "abort":
                    raise
                if recovery_action["action"] == "skip":
                    continue
                if recovery_action["action"] in ["retry", "fallback"]:
                    if "modified_plan" in recovery_action:
                        self.current_plan = recovery_action["modified_plan"]
                    continue

        # Step 5: Synthesize results from all iterations
        if execution_results is None:
            return "Task execution failed: No results generated"

        final_response = self.synthesizer.synthesize_results(execution_results)

        # Store assistant response in conversation history
        if self.config.enable_memory and self.conversation_history is not None:
            self.conversation_history.add_assistant_message(final_response)

        return final_response

    @classmethod
    def from_config_dict(cls, config_dict: dict[str, Any]) -> "OrchestratorAgent":
        """Create an OrchestratorAgent instance from a configuration dictionary.

        Args:
            config_dict: Dictionary containing orchestrator configuration parameters

        Returns:
            OrchestratorAgent: Initialized OrchestratorAgent instance
        """
        config = OrchestratorConfig(**config_dict)
        return cls(config=config)

    def __repr__(self) -> str:
        """String representation of the OrchestratorAgent instance."""
        return (
            f"OrchestratorAgent(name={self.config.name}, llm={self.llm.config.model}, "
            f"mcp_servers={len(self.mcp_servers)}, max_iterations={self.config.max_iterations})"
        )
