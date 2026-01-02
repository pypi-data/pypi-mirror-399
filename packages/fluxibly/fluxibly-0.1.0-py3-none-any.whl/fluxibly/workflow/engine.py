"""Workflow execution engine.

This module provides the WorkflowEngine class for orchestrating agent execution
with MCP tool integration and lifecycle management.
"""

from pathlib import Path
from typing import Any

from loguru import logger

from fluxibly.agent.base import Agent
from fluxibly.agent.config import AgentConfig
from fluxibly.agent.conversation import Message
from fluxibly.config.loader import ConfigLoader
from fluxibly.llm.base import LLMConfig
from fluxibly.mcp_client.manager import MCPClientManager
from fluxibly.orchestrator.agent import OrchestratorAgent, OrchestratorConfig
from fluxibly.workflow.config import WorkflowConfig


class WorkflowEngine:
    """Main orchestration engine for fluxibly workflows.

    Manages the complete lifecycle of agent execution including configuration loading,
    MCP manager initialization, agent instantiation, and session management.

    Attributes:
        config: WorkflowConfig instance
        mcp_manager: MCPClientManager instance (initialized during initialize())
        agent: Agent or OrchestratorAgent instance (created during initialize())

    Example:
        >>> config = WorkflowConfig(
        ...     name="my_workflow",
        ...     agent_type="orchestrator",
        ...     profile="development_assistant"
        ... )
        >>> engine = WorkflowEngine(config=config)
        >>> await engine.initialize()
        >>> response = await engine.execute("Hello, world!")
        >>> await engine.shutdown()
    """

    def __init__(
        self,
        config: WorkflowConfig | dict[str, Any] | None = None,
        profile: str | None = None,
    ) -> None:
        """Initialize workflow engine.

        Args:
            config: WorkflowConfig instance or dict. If None, creates default config.
            profile: Profile name to load. Overrides config.profile if provided.

        Example:
            >>> # From profile name
            >>> engine = WorkflowEngine(profile="development_assistant")
            >>>
            >>> # From config dict
            >>> engine = WorkflowEngine(config={
            ...     "name": "my_workflow",
            ...     "agent_type": "orchestrator",
            ...     "profile": "default"
            ... })
            >>>
            >>> # From WorkflowConfig
            >>> config = WorkflowConfig(name="my_workflow", agent_type="agent")
            >>> engine = WorkflowEngine(config=config)
        """
        # Handle config input
        if config is None:
            self.config = WorkflowConfig(name="default_workflow")
        elif isinstance(config, dict):
            self.config = WorkflowConfig(**config)
        else:
            self.config = config

        # Override profile if specified
        if profile is not None:
            self.config.profile = profile

        # Components (initialized in initialize())
        self.mcp_manager: MCPClientManager | None = None
        self.agent: Agent | OrchestratorAgent | None = None
        self._merged_config: dict[str, Any] | None = None
        self._initialized = False

        self._logger = logger.bind(workflow=self.config.name)

    async def initialize(self) -> None:
        """Initialize the workflow engine.

        Steps:
        1. Load and merge configuration (profile + framework defaults)
        2. Initialize MCPClientManager
        3. Create appropriate agent (Agent or OrchestratorAgent)

        Raises:
            FileNotFoundError: If configuration files not found
            ValueError: If configuration is invalid
            Exception: If initialization fails
        """
        if self._initialized:
            self._logger.warning("WorkflowEngine already initialized")
            return

        try:
            # Step 1: Load and merge configuration
            self._logger.info(f"Loading configuration for profile: {self.config.profile}")
            self._merged_config = self._load_profile_config()

            # Override agent_type from merged config if present in workflow section
            workflow_config = self._merged_config.get("workflow", {})
            if "agent_type" in workflow_config:
                self.config.agent_type = workflow_config["agent_type"]
                self._logger.debug(f"Agent type from profile: {self.config.agent_type}")

            # Step 2: Initialize MCP Manager
            self._logger.info(f"Initializing MCP client manager from: {self.config.mcp_config_path}")
            mcp_config_path = self._resolve_path(self.config.mcp_config_path)
            self.mcp_manager = MCPClientManager(str(mcp_config_path))
            await self.mcp_manager.initialize()

            # Step 3: Create agent
            self._logger.info(f"Creating agent of type: {self.config.agent_type}")
            self.agent = self._create_agent()

            self._initialized = True
            self._logger.info("WorkflowEngine initialization complete")

        except Exception:
            self._logger.exception("Failed to initialize WorkflowEngine")
            # Cleanup on failure
            if self.mcp_manager:
                try:
                    await self.mcp_manager.shutdown()
                except Exception:
                    self._logger.exception("Failed to shutdown MCP manager during cleanup")
            raise

    async def execute(self, prompt: str, context: dict[str, Any] | None = None) -> str:
        """Execute a single task.

        Args:
            prompt: User input/task
            context: Optional execution context

        Returns:
            Agent response

        Raises:
            RuntimeError: If engine not initialized
            Exception: If execution fails

        Example:
            >>> response = await engine.execute(
            ...     "What is the capital of France?",
            ...     context={"language": "en"}
            ... )
        """
        if not self._initialized or self.agent is None:
            raise RuntimeError("WorkflowEngine not initialized. Call initialize() first.")

        try:
            self._logger.debug(f"Executing task: {prompt[:50]}...")
            response = await self.agent.forward(prompt, context)
            self._logger.debug("Task execution completed successfully")
            return response

        except Exception:
            self._logger.exception("Task execution failed")
            raise

    async def execute_batch(
        self,
        prompts: list[str],
        contexts: list[dict[str, Any]] | None = None,
        preserve_state: bool = False,
    ) -> list[str]:
        """Execute multiple tasks.

        Args:
            prompts: List of user inputs/tasks
            contexts: Optional list of contexts (one per prompt, or None)
            preserve_state: If True and stateful, maintain conversation history
                          across batch items. If False, clear after each item.

        Returns:
            List of responses (one per prompt)

        Raises:
            RuntimeError: If engine not initialized
            ValueError: If contexts list length doesn't match prompts

        Example:
            >>> tasks = ["What is 2+2?", "What is 3+3?", "What is 4+4?"]
            >>> responses = await engine.execute_batch(tasks)
            >>>
            >>> # With contexts
            >>> contexts = [{"language": "en"}, {"language": "es"}, {"language": "fr"}]
            >>> responses = await engine.execute_batch(tasks, contexts)
            >>>
            >>> # With state preservation
            >>> prompts = ["Analyze this code", "Add type hints", "Add docstring"]
            >>> responses = await engine.execute_batch(prompts, preserve_state=True)
        """
        if not self._initialized or self.agent is None:
            raise RuntimeError("WorkflowEngine not initialized. Call initialize() first.")

        if contexts is not None and len(contexts) != len(prompts):
            raise ValueError(f"Context list length ({len(contexts)}) must match prompts length ({len(prompts)})")

        self._logger.info(f"Executing batch of {len(prompts)} tasks")
        results: list[str] = []

        for i, prompt in enumerate(prompts):
            context = contexts[i] if contexts else None

            try:
                self._logger.debug(f"Executing batch item {i + 1}/{len(prompts)}")
                result = await self.execute(prompt, context)
                results.append(result)

            except Exception:
                self._logger.exception(f"Failed to execute batch item {i + 1}")
                # Add error message to results and continue
                results.append(f"ERROR: Task {i + 1} failed - {prompt[:50]}...")

            # Clear state between batch items if not preserving state
            if not preserve_state and self.config.stateful and i < len(prompts) - 1:
                self.clear_session()
                self._logger.debug("Cleared session state between batch items")

        self._logger.info(f"Batch execution complete: {len(results)} results")
        return results

    async def shutdown(self) -> None:
        """Shutdown the workflow engine.

        Gracefully closes MCP connections and cleans up resources.

        Example:
            >>> await engine.shutdown()
        """
        self._logger.info("Shutting down WorkflowEngine")

        if self.mcp_manager:
            try:
                await self.mcp_manager.shutdown()
                self._logger.debug("MCP client manager shutdown complete")
            except Exception:
                self._logger.exception("Error shutting down MCP manager")

        self.agent = None
        self.mcp_manager = None
        self._initialized = False
        self._logger.info("WorkflowEngine shutdown complete")

    def clear_session(self) -> None:
        """Clear conversation history (stateful mode only).

        Only works if workflow is stateful and agent has conversation history enabled.

        Example:
            >>> engine.clear_session()
        """
        if not self.config.stateful:
            self._logger.warning("Cannot clear session: workflow is not stateful")
            return

        if self.agent:
            self.agent.clear_conversation_history()
            self._logger.debug("Session history cleared")
        else:
            self._logger.warning("Cannot clear session: agent not initialized")

    def get_session_history(self) -> list[Message]:
        """Get conversation history (stateful mode only).

        Returns:
            List of Message objects, or empty list if not stateful or not initialized

        Example:
            >>> history = engine.get_session_history()
            >>> for msg in history:
            ...     print(f"{msg.role}: {msg.content}")
        """
        if not self.config.stateful:
            self._logger.debug("Workflow is not stateful, returning empty history")
            return []

        if self.agent:
            return self.agent.get_conversation_history()

        return []

    @classmethod
    def from_profile(cls, profile_name: str, config_dir: str = "config") -> "WorkflowEngine":
        """Create WorkflowEngine from a profile.

        Factory method for creating an engine from a profile name.

        Args:
            profile_name: Name of profile to load
            config_dir: Configuration directory path

        Returns:
            WorkflowEngine instance (not yet initialized - call initialize())

        Example:
            >>> engine = WorkflowEngine.from_profile("development_assistant")
            >>> await engine.initialize()
        """
        config = WorkflowConfig(
            name=f"{profile_name}_workflow",
            profile=profile_name,
            config_dir=config_dir,
        )
        return cls(config=config)

    def _load_profile_config(self) -> dict[str, Any]:
        """Load and merge profile configuration.

        Returns:
            Merged configuration dictionary

        Raises:
            FileNotFoundError: If profile or framework config not found
            ValueError: If configuration is invalid
        """
        config_dir = Path(self.config.config_dir)
        loader = ConfigLoader(config_dir)

        try:
            merged_config = loader.load_profile(self.config.profile)
            self._logger.debug(f"Loaded profile: {self.config.profile}")
            return merged_config

        except Exception:
            self._logger.exception(f"Failed to load profile: {self.config.profile}")
            raise

    def _create_agent(self) -> Agent | OrchestratorAgent:
        """Create the appropriate agent based on configuration.

        Returns:
            Agent or OrchestratorAgent instance

        Raises:
            ValueError: If agent configuration is invalid
        """
        if self._merged_config is None:
            raise ValueError("Configuration not loaded. Call initialize() first.")

        try:
            # Extract agent configuration from merged config
            if self.config.agent_type == "orchestrator":
                agent_config = self._create_orchestrator_config()
                agent = OrchestratorAgent(config=agent_config, mcp_client_manager=self.mcp_manager)
                self._logger.debug("Created OrchestratorAgent")
            else:  # agent
                agent_config = self._create_agent_config()
                agent = Agent(config=agent_config, mcp_client_manager=self.mcp_manager)
                self._logger.debug("Created Agent")

            return agent

        except Exception:
            self._logger.exception("Failed to create agent")
            raise

    def _create_agent_config(self) -> AgentConfig:
        """Extract and create AgentConfig from merged configuration.

        Returns:
            AgentConfig instance
        """
        if self._merged_config is None:
            raise ValueError("Configuration not loaded")

        agent_dict = self._merged_config.get("agent", {})

        # Extract LLM config
        llm_dict = agent_dict.get("llm", self._merged_config.get("llm", {}))
        llm_config = LLMConfig(**llm_dict)

        # Create AgentConfig with stateful setting from workflow config
        agent_config_dict = {
            **agent_dict,
            "llm": llm_config,
            "enable_memory": self.config.stateful,  # Use workflow stateful setting
        }

        return AgentConfig(**agent_config_dict)

    def _create_orchestrator_config(self) -> OrchestratorConfig:
        """Extract and create OrchestratorConfig from merged configuration.

        Returns:
            OrchestratorConfig instance
        """
        if self._merged_config is None:
            raise ValueError("Configuration not loaded")

        orchestrator_dict = self._merged_config.get("orchestrator", {})

        # Extract LLM config
        llm_dict = orchestrator_dict.get("llm", self._merged_config.get("llm", {}))
        llm_config = LLMConfig(**llm_dict)

        # Create OrchestratorConfig with stateful setting from workflow config
        orchestrator_config_dict = {
            **orchestrator_dict,
            "llm": llm_config,
            "enable_memory": self.config.stateful,  # Use workflow stateful setting
        }

        return OrchestratorConfig(**orchestrator_config_dict)

    def _resolve_path(self, path: str) -> Path:
        """Resolve a path relative to config_dir.

        Args:
            path: Path string (can be relative or absolute)

        Returns:
            Resolved Path object
        """
        p = Path(path)
        if p.is_absolute():
            return p

        # Check if path already starts with config_dir
        # If path is "config/mcp_servers.yaml" and config_dir is "config",
        # return it as-is to avoid doubling to "config/config/mcp_servers.yaml"
        path_str = str(p)
        config_dir_prefix = f"{self.config.config_dir}/"
        if path_str.startswith(config_dir_prefix) or path_str == self.config.config_dir:
            return p

        # For simple paths like "mcp_servers.yaml", prepend config_dir
        return Path(self.config.config_dir) / path

    def __repr__(self) -> str:
        """String representation of WorkflowEngine."""
        agent_type = type(self.agent).__name__ if self.agent else "None"
        return (
            f"WorkflowEngine(name={self.config.name}, "
            f"profile={self.config.profile}, "
            f"agent_type={self.config.agent_type}, "
            f"agent={agent_type}, "
            f"initialized={self._initialized})"
        )


class WorkflowSession:
    """Context manager for stateful workflow sessions.

    Provides a convenient way to manage workflow lifecycle with automatic
    initialization and cleanup.

    Example:
        >>> async with WorkflowSession(profile="development_assistant") as session:
        ...     response1 = await session.execute("First task")
        ...     response2 = await session.execute("Follow up task")  # Has context
    """

    def __init__(
        self,
        profile: str = "default",
        config: WorkflowConfig | dict[str, Any] | None = None,
    ) -> None:
        """Initialize workflow session.

        Args:
            profile: Profile name to load (ignored if config provided)
            config: Optional WorkflowConfig or config dict

        Example:
            >>> # From profile
            >>> async with WorkflowSession(profile="development_assistant") as session:
            ...     await session.execute("Task")
            >>>
            >>> # From config
            >>> config = WorkflowConfig(name="my_workflow", agent_type="orchestrator")
            >>> async with WorkflowSession(config=config) as session:
            ...     await session.execute("Task")
        """
        self.engine = WorkflowEngine(config=config, profile=profile)

    async def __aenter__(self) -> "WorkflowSession":
        """Enter context manager - initialize engine.

        Returns:
            Self (WorkflowSession instance)
        """
        await self.engine.initialize()
        return self

    async def __aexit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> bool:
        """Exit context manager - shutdown engine.

        Args:
            exc_type: Exception type (if any)
            exc_val: Exception value (if any)
            exc_tb: Exception traceback (if any)

        Returns:
            False (don't suppress exceptions)
        """
        await self.engine.shutdown()
        return False

    async def execute(self, prompt: str, context: dict[str, Any] | None = None) -> str:
        """Execute a task within the session.

        Args:
            prompt: User input/task
            context: Optional execution context

        Returns:
            Agent response
        """
        return await self.engine.execute(prompt, context)

    async def execute_batch(
        self,
        prompts: list[str],
        contexts: list[dict[str, Any]] | None = None,
        preserve_state: bool = False,
    ) -> list[str]:
        """Execute multiple tasks within the session.

        Args:
            prompts: List of user inputs/tasks
            contexts: Optional list of contexts
            preserve_state: Whether to preserve state across batch items

        Returns:
            List of responses
        """
        return await self.engine.execute_batch(prompts, contexts, preserve_state)

    def clear_session(self) -> None:
        """Clear conversation history."""
        self.engine.clear_session()

    def get_session_history(self) -> list[Message]:
        """Get conversation history."""
        return self.engine.get_session_history()

    def __repr__(self) -> str:
        """String representation of WorkflowSession."""
        return f"WorkflowSession(engine={self.engine})"
