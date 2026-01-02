"""Agent Base Class for Fluxibly Framework.

This module provides the foundational Agent class that combines an LLM with system prompts
and MCP (Model Context Protocol) tools. The Agent class handles basic prompt preparation
and simple MCP tool selection.

The Agent class serves as the standard building block for creating AI agents with
tool-calling capabilities. It provides:
- Integration with LLM for language understanding and generation
- System prompt management for agent behavior configuration
- MCP tool registry and basic selection logic
- Prompt preparation combining user input with system instructions
- Conversation history management and memory

For more complex orchestration with planning, iteration, and sophisticated tool
selection, use the OrchestratorAgent subclass.

All initialization parameters are configurable via config files.
"""

import json
from typing import TYPE_CHECKING, Any

from loguru import logger

from fluxibly.agent.config import AgentConfig
from fluxibly.agent.conversation import ConversationHistory, Message
from fluxibly.llm.base import LLM

if TYPE_CHECKING:
    from fluxibly.mcp_client.manager import MCPClientManager


class Agent:
    """Base Agent class combining LLM with system prompt and MCP tools.

    The Agent class is the primary building block for creating AI agents in the
    Fluxibly framework. It encapsulates:
    - An LLM for language understanding and generation
    - A system prompt that defines the agent's role and behavior
    - A list of available MCP tools the agent can use
    - Basic logic for selecting and invoking MCP tools
    - Conversation history management

    Design Philosophy:
    - Keep tool selection basic: Simple matching of user intent to available tools
    - Delegate complex orchestration: Use OrchestratorAgent for multi-step planning
    - Configurable behavior: All parameters loaded from config files
    - Composable: Agents can be combined and nested

    Workflow:
    1. User provides input prompt
    2. prepare_prompt() combines user prompt + system prompt + available MCP tools + history
    3. forward() sends prepared prompt to LLM
    4. LLM decides which (if any) MCP tools to call
    5. Agent executes selected MCP tool calls
    6. Results are returned to user
    7. Conversation is stored in history (if memory enabled)

    The Agent does NOT:
    - Perform multi-step planning or iterative refinement (use Orchestrator)
    - Implement complex MCP selection algorithms (use Orchestrator)
    - Synthesize results from multiple tool calls (use Orchestrator)

    Example:
        >>> import asyncio
        >>> from fluxibly.llm.base import LLMConfig
        >>> agent_config = AgentConfig(
        ...     name="research_agent",
        ...     llm=LLMConfig(model="gpt-4o", framework="langchain"),
        ...     system_prompt="You are a research assistant.",
        ...     mcp_servers=["web_search", "wikipedia"]
        ... )
        >>> agent = Agent(config=agent_config)
        >>> response = asyncio.run(agent.forward("What is the capital of France?"))
        >>> print(response)
        "Paris is the capital of France..."

    Attributes:
        config: AgentConfig object containing all agent parameters
        llm: LLM instance for language model interactions
        system_prompt: System instructions defining agent behavior
        mcp_servers: List of MCP server identifiers available to this agent
        conversation_history: ConversationHistory instance (if memory enabled)
    """

    def __init__(self, config: AgentConfig, mcp_client_manager: "MCPClientManager | None" = None) -> None:
        """Initialize the Agent with configuration.

        Args:
            config: AgentConfig object containing agent parameters including
                   LLM config, system prompt, and MCP server list.
            mcp_client_manager: Optional MCPClientManager instance for tool execution.
                              If None, Agent operates in LLM-only mode without MCP tools.

        Note:
            The MCP servers are referenced by name/ID. Actual MCP server
            connections and management are handled by MCPClientManager.
        """
        self.config = config
        self.llm = LLM(config=config.llm)
        self.system_prompt = config.system_prompt
        self.mcp_servers = config.mcp_servers
        self.mcp_client_manager = mcp_client_manager
        self._logger = logger.bind(agent=config.name)

        # Initialize conversation history if memory is enabled
        if config.enable_memory:
            # Calculate max_tokens from context_window if specified
            max_tokens = None
            if config.context_window:
                # Reserve some tokens for system prompt and current message
                max_tokens = int(config.context_window * 0.7)  # Use 70% for history

            self.conversation_history: ConversationHistory | None = ConversationHistory(
                max_messages=None,  # No hard limit on message count
                max_tokens=max_tokens,
            )
        else:
            self.conversation_history = None

    async def prepare_prompt(self, user_prompt: str, context: dict[str, Any] | None = None) -> str:
        """Prepare the complete prompt for the LLM.

        This method combines:
        1. System prompt (agent's role and instructions)
        2. Conversation history (if memory enabled)
        3. User prompt (the actual user request)
        4. Available MCP tools (based on mcp_servers list)
        5. Optional context (metadata, constraints, previous results, etc.)

        Args:
            user_prompt: The user's input/request
            context: Optional context dictionary containing:
                    - conversation_history: External conversation history (str or list)
                    - metadata: Additional information (dict or any)
                    - constraints: Execution constraints (list or str)
                    - previous_results: Results from previous operations

        Returns:
            str: Fully prepared prompt ready to send to LLM via forward()

        Note:
            This method performs BASIC MCP selection only. It:
            - Matches keywords in user prompt to MCP capabilities
            - Filters MCP list based on relevance
            - Does NOT perform complex planning or optimization
            - For advanced selection, use OrchestratorAgent.prepare_system()

        Example:
            >>> agent = Agent(config=agent_config)
            >>> prepared = await agent.prepare_prompt(
            ...     user_prompt="Search for recent AI papers",
            ...     context={"previous_results": [...]}
            ... )
            >>> # prepared now contains: system prompt + history + user prompt + relevant MCP tools
        """
        # Start with system prompt
        prompt_parts = [self.system_prompt]

        # Add conversation history from internal memory
        if self.conversation_history and len(self.conversation_history) > 0:
            history_text = self.conversation_history.format_for_prompt(include_system=False)
            if history_text:
                prompt_parts.append(f"\nConversation History:\n{history_text}")

        # Add context if provided (can override or supplement internal history)
        if context:
            # External conversation history (if provided, supplements internal)
            if "conversation_history" in context:
                external_history = context["conversation_history"]
                if external_history and isinstance(external_history, str):
                    prompt_parts.append(f"\nAdditional Context:\n{external_history}")
                elif external_history and isinstance(external_history, list):
                    # Handle list of messages
                    formatted_external = self._format_message_list(external_history)
                    if formatted_external:
                        prompt_parts.append(f"\nAdditional Context:\n{formatted_external}")

            # Add metadata/context information
            if "metadata" in context:
                metadata = context["metadata"]
                if metadata:
                    if isinstance(metadata, dict):
                        # Format metadata nicely
                        metadata_str = "\n".join(f"- {k}: {v}" for k, v in metadata.items())
                        prompt_parts.append(f"\nContext Information:\n{metadata_str}")
                    else:
                        prompt_parts.append(f"\nContext: {metadata}")

            # Add constraints if provided
            if "constraints" in context:
                constraints = context["constraints"]
                if constraints:
                    if isinstance(constraints, list):
                        constraints_str = "\n".join(f"- {c}" for c in constraints)
                        prompt_parts.append(f"\nConstraints:\n{constraints_str}")
                    else:
                        prompt_parts.append(f"\nConstraints: {constraints}")

            # Add previous results if provided
            if "previous_results" in context:
                results = context["previous_results"]
                if results:
                    prompt_parts.append(f"\nPrevious Results:\n{results}")

        # Add MCP tools if available
        if self.mcp_client_manager and self.mcp_servers:
            try:
                # Get all tools from manager
                all_tools = self.mcp_client_manager.get_all_tools()

                if all_tools:
                    # Select relevant tools using basic strategy
                    selected_tools = await self.select_mcp_tools(user_prompt, self.mcp_servers, context)

                    if selected_tools:
                        # Format tool descriptions
                        tool_descriptions = []
                        for tool in all_tools:
                            # Filter tools by selected servers
                            if any(server in selected_tools for server in self.mcp_servers):
                                tool_descriptions.append(
                                    f"- {tool.get('name', 'unknown')}: {tool.get('description', '')}"
                                )

                        if tool_descriptions:
                            prompt_parts.append("\nAvailable Tools:\n" + "\n".join(tool_descriptions))
            except Exception:
                self._logger.exception("Failed to add MCP tools to prompt")

        # Add user prompt
        prompt_parts.append(f"\nUser: {user_prompt}")

        return "\n".join(prompt_parts)

    async def forward(self, user_prompt: str, context: dict[str, Any] | None = None) -> str:
        """Execute the agent's main inference loop.

        This is the primary method for running the agent. It:
        1. Adds user message to conversation history (if memory enabled)
        2. Calls prepare_prompt() to create the complete prompt
        3. Sends prepared prompt to the LLM via llm.forward()
        4. Processes LLM response to check for MCP tool calls
        5. Executes any requested MCP tool calls
        6. Adds assistant response and tool results to history
        7. Returns final response to user

        The forward() method handles basic tool calling workflow:
        - LLM indicates which tools to call in its response
        - Agent invokes those tools via MCPClientManager
        - Results are incorporated into response

        For complex multi-step workflows with planning and iteration,
        use OrchestratorAgent.forward() instead.

        Args:
            user_prompt: The user's input/request
            context: Optional context dictionary (see prepare_prompt() for details)

        Returns:
            str: The agent's response, potentially incorporating MCP tool results

        Raises:
            Exception: If LLM call fails or MCP tool execution fails

        Example:
            >>> agent = Agent(config=agent_config)
            >>> response = await agent.forward(
            ...     user_prompt="What's the weather in Paris?",
            ...     context={"location": "Paris, France"}
            ... )
            >>> print(response)
            "The current weather in Paris is..."

        Note:
            This method is async to support async MCP operations.
        """
        try:
            # Add user message to conversation history if memory enabled
            if self.conversation_history is not None:
                self.conversation_history.add_user_message(user_prompt)

            # Step 1: Prepare prompt with available tools
            prepared_prompt = await self.prepare_prompt(user_prompt, context)
            self._logger.debug(f"Prepared prompt length: {len(prepared_prompt)} chars")

            # Step 2: If MCP tools available, ask LLM which to use
            if self.mcp_client_manager and self.mcp_servers:
                # Ask LLM to decide on tool usage
                tool_selection_prompt = (
                    f"{prepared_prompt}\n\n"
                    "Determine if any tools should be used for this task. "
                    'If yes, respond with JSON: {"tools": [{"name": "tool_name", "args": {...}}]}. '
                    'If no tools needed, respond with: {"tools": []}'
                )

                tool_decision = self.llm.forward(tool_selection_prompt)
                tools_to_use = self._parse_tool_decision(tool_decision)

                # Execute selected tools
                if tools_to_use:
                    tool_results = []
                    for tool_name, tool_args in tools_to_use:
                        result = await self._invoke_mcp_tool(tool_name, tool_args)
                        tool_results.append({tool_name: result})
                        self._logger.debug(f"Executed tool: {tool_name}")

                        # Add tool result to conversation history
                        if self.conversation_history is not None:
                            self.conversation_history.add_tool_result(tool_name, str(result), {"args": tool_args})

                    # Get final response with tool results
                    final_prompt = (
                        f"{prepared_prompt}\n\n"
                        f"Tool Execution Results:\n{tool_results}\n\n"
                        "Based on these results, provide your final answer:"
                    )
                    response = self.llm.forward(final_prompt)
                else:
                    # No tools needed, use initial response
                    response = tool_decision
            else:
                # No MCP available, direct LLM response
                response = self.llm.forward(prepared_prompt)

            # Add assistant response to conversation history
            if self.conversation_history is not None:
                self.conversation_history.add_assistant_message(response)

            self._logger.info("Agent completed successfully")
            return response

        except Exception:
            self._logger.exception("Agent forward failed")
            raise

    async def select_mcp_tools(
        self, user_prompt: str, available_servers: list[str], context: dict[str, Any] | None = None
    ) -> list[str]:
        """Perform basic MCP tool selection based on user prompt.

        This method implements simple tool selection logic:
        - LLM-based semantic matching for "auto" strategy
        - Filtering based on agent's configured mcp_servers list
        - Basic relevance scoring

        This is intentionally simple. For advanced selection algorithms
        (semantic matching, multi-step planning, optimization), use
        OrchestratorAgent which has more sophisticated selection logic.

        Args:
            user_prompt: The user's input/request
            available_servers: List of all available MCP server names
            context: Optional context for selection decisions

        Returns:
            list[str]: Selected MCP server names to include in this execution

        Selection Strategies (based on config.mcp_selection_strategy):
        - "all": Return all servers in agent's mcp_servers list
        - "auto": LLM-based semantic matching for relevance
        - "none": Return empty list (no tools)

        Example:
            >>> agent = Agent(config=agent_config)
            >>> selected = await agent.select_mcp_tools(
            ...     user_prompt="Search for Python documentation",
            ...     available_servers=["web_search", "code_analysis", "vision"]
            ... )
            >>> print(selected)
            ["web_search", "code_analysis"]  # vision not relevant

        Note:
            This method is called internally by prepare_prompt(). You typically
            don't need to call it directly unless implementing custom logic.
        """
        strategy = self.config.mcp_selection_strategy

        if strategy == "none":
            self._logger.debug("MCP selection strategy is 'none', returning no tools")
            return []

        if strategy == "all":
            selected = [s for s in self.mcp_servers if s in available_servers]
            self._logger.debug(f"MCP selection strategy is 'all', returning {len(selected)} tools")
            return selected

        # Auto strategy: LLM-based semantic matching
        if not self.mcp_client_manager:
            self._logger.warning("No MCP client manager available, returning all servers")
            return self.mcp_servers

        # Get all tools from manager
        try:
            all_tools = self.mcp_client_manager.get_all_tools()
        except Exception:
            self._logger.exception("Failed to get tools from MCP manager")
            return [s for s in self.mcp_servers if s in available_servers]

        if not all_tools:
            self._logger.warning("No tools available, returning all servers")
            return [s for s in self.mcp_servers if s in available_servers]

        # Format tool descriptions
        tool_descriptions = [f"- {tool.get('name', 'unknown')}: {tool.get('description', '')}" for tool in all_tools]

        # Ask LLM to select relevant tools
        selection_prompt = (
            f"Task: {user_prompt}\n\n"
            f"Available tools:\n" + "\n".join(tool_descriptions) + "\n\n"
            "Which tools are most relevant for this task? "
            'Respond with a JSON list of tool names: {"selected": ["tool1", "tool2"]}'
        )

        try:
            selection_response = self.llm.forward(selection_prompt)
            selected = self._parse_tool_selection(selection_response)
            self._logger.debug(f"LLM-selected {len(selected)} MCP tools: {selected}")
            return selected
        except Exception:
            self._logger.exception("Failed to perform LLM-based tool selection, returning all servers")
            return [s for s in self.mcp_servers if s in available_servers]

    async def _invoke_mcp_tool(self, tool_name: str, tool_args: dict[str, Any]) -> Any:
        """Internal method to invoke a single MCP tool.

        This method interfaces with MCPClientManager to execute a tool call.

        Args:
            tool_name: Name of the MCP tool to invoke
            tool_args: Arguments to pass to the tool

        Returns:
            Any: Tool execution result

        Note:
            This is an internal method. Tool invocation is typically
            handled automatically by forward().
        """
        if not self.mcp_client_manager:
            self._logger.warning("No MCP client manager available, skipping tool invocation")
            return None

        try:
            self._logger.debug(f"Invoking MCP tool '{tool_name}' with args: {tool_args}")
            result = await self.mcp_client_manager.invoke_tool(tool_name, tool_args)
            self._logger.debug("Tool invocation successful")
            return result
        except Exception:
            self._logger.exception("MCP tool invocation failed")
            raise

    def _parse_tool_decision(self, llm_response: str) -> list[tuple[str, dict[str, Any]]]:
        """Parse LLM response to extract tool names and arguments.

        Args:
            llm_response: LLM response containing tool decision

        Returns:
            list[tuple[str, dict[str, Any]]]: List of (tool_name, tool_args) tuples
        """
        try:
            data = json.loads(llm_response)
            tools = data.get("tools", [])
            return [(tool["name"], tool["args"]) for tool in tools]
        except (json.JSONDecodeError, KeyError, TypeError):
            self._logger.warning(f"Failed to parse tool decision: {llm_response}")
            return []

    def _parse_tool_selection(self, llm_response: str) -> list[str]:
        """Parse LLM response to extract selected tool names.

        Args:
            llm_response: LLM response containing tool selection

        Returns:
            list[str]: List of selected tool names
        """
        try:
            data = json.loads(llm_response)
            return data.get("selected", [])
        except (json.JSONDecodeError, KeyError):
            self._logger.warning(f"Failed to parse tool selection: {llm_response}")
            return []

    def _format_message_list(self, messages: list[dict[str, Any]]) -> str:
        """Format a list of message dictionaries for prompt inclusion.

        Args:
            messages: List of message dicts with 'role' and 'content' keys

        Returns:
            Formatted string representation of messages
        """
        formatted_lines = []
        for msg in messages:
            if not isinstance(msg, dict):
                continue

            role = msg.get("role", "unknown")
            content = msg.get("content", "")

            if role == "user":
                formatted_lines.append(f"User: {content}")
            elif role == "assistant":
                formatted_lines.append(f"Assistant: {content}")
            elif role == "system":
                formatted_lines.append(f"System: {content}")
            elif role == "tool":
                tool_name = msg.get("name", "unknown")
                formatted_lines.append(f"Tool ({tool_name}): {content}")

        return "\n".join(formatted_lines)

    def clear_conversation_history(self) -> None:
        """Clear the conversation history buffer.

        This is useful when starting a new conversation or resetting context.
        Only works if memory is enabled (enable_memory=True in config).
        """
        if self.conversation_history is not None:
            self.conversation_history.clear()
            self._logger.debug("Conversation history cleared")
        else:
            self._logger.warning("Cannot clear history: memory is not enabled")

    def get_conversation_history(self) -> list[Message]:
        """Get the current conversation history.

        Returns:
            List of Message objects, or empty list if memory not enabled

        Example:
            >>> history = agent.get_conversation_history()
            >>> for msg in history:
            ...     print(f"{msg.role}: {msg.content}")
        """
        if self.conversation_history is not None:
            return self.conversation_history.get_messages()
        return []

    def add_to_conversation_history(self, role: str, content: str, metadata: dict[str, Any] | None = None) -> None:
        """Manually add a message to conversation history.

        Args:
            role: Message role ("user", "assistant", "system", "tool")
            content: Message content
            metadata: Optional metadata dictionary

        Example:
            >>> agent.add_to_conversation_history(
            ...     "system",
            ...     "New constraint: responses must be under 100 words"
            ... )
        """
        if self.conversation_history is not None:
            self.conversation_history.add_message(role, content, metadata)
            self._logger.debug(f"Added {role} message to conversation history")
        else:
            self._logger.warning("Cannot add to history: memory is not enabled")

    @classmethod
    def from_config_dict(cls, config_dict: dict[str, Any]) -> "Agent":
        """Create an Agent instance from a configuration dictionary.

        This is a convenience method for loading agents from config files.

        Args:
            config_dict: Dictionary containing agent configuration parameters

        Returns:
            Agent: Initialized Agent instance

        Example:
            >>> config = {
            ...     "name": "research_agent",
            ...     "llm": {"model": "gpt-4o", "temperature": 0.7, "framework": "langchain"},
            ...     "system_prompt": "You are a research assistant.",
            ...     "mcp_servers": ["web_search"]
            ... }
            >>> agent = Agent.from_config_dict(config)
        """
        config = AgentConfig(**config_dict)
        return cls(config=config)

    def __repr__(self) -> str:
        """String representation of the Agent instance."""
        return f"Agent(name={self.config.name}, llm={self.llm.config.model}, mcp_servers={len(self.mcp_servers)})"
