"""Unit tests for Agent base class."""

import pytest

from fluxibly.agent.base import Agent
from fluxibly.agent.config import AgentConfig
from fluxibly.agent.conversation import ConversationHistory
from fluxibly.llm.base import LLMConfig


class MockLLM:
    """Mock LLM for testing."""

    def __init__(self, config: LLMConfig) -> None:
        self.config = config
        self.call_count = 0
        self.last_prompt = None

    def forward(self, prompt: str, **kwargs) -> str:  # noqa: ARG002
        """Mock forward method."""
        self.call_count += 1
        self.last_prompt = prompt
        return '{"tools": []}'


class MockMCPClientManager:
    """Mock MCP client manager for testing."""

    def __init__(self) -> None:
        self.tools = [
            {"name": "web_search", "description": "Search the web for information"},
            {"name": "calculator", "description": "Perform mathematical calculations"},
        ]
        self.invoked_tools = []

    def get_all_tools(self) -> list[dict]:
        """Get all available tools."""
        return self.tools

    async def invoke_tool(self, tool_name: str, tool_args: dict) -> str:
        """Mock tool invocation."""
        self.invoked_tools.append((tool_name, tool_args))
        return f"Result from {tool_name}"


@pytest.fixture
def basic_llm_config():
    """Create a basic LLM config for testing."""
    return LLMConfig(framework="langchain", model="gpt-4o")


@pytest.fixture
def basic_agent_config(basic_llm_config):
    """Create a basic agent config for testing."""
    return AgentConfig(
        name="test_agent",
        llm=basic_llm_config,
        system_prompt="You are a test assistant.",
        mcp_servers=["web_search", "calculator"],
        enable_memory=True,
        context_window=4000,
    )


@pytest.fixture
def agent_config_no_memory(basic_llm_config):
    """Create agent config without memory."""
    return AgentConfig(
        name="test_agent_no_memory",
        llm=basic_llm_config,
        system_prompt="You are a test assistant.",
        enable_memory=False,
    )


@pytest.fixture
def mock_mcp_manager():
    """Create a mock MCP client manager."""
    return MockMCPClientManager()


class TestAgentInitialization:
    """Tests for Agent initialization."""

    def test_agent_init_with_memory(self, basic_agent_config, monkeypatch):
        """Test agent initialization with memory enabled."""
        # Mock the LLM constructor
        monkeypatch.setattr("fluxibly.agent.base.LLM", lambda config: MockLLM(config))

        agent = Agent(config=basic_agent_config)

        assert agent.config == basic_agent_config
        assert agent.system_prompt == "You are a test assistant."
        assert agent.mcp_servers == ["web_search", "calculator"]
        assert agent.conversation_history is not None
        assert isinstance(agent.conversation_history, ConversationHistory)

    def test_agent_init_without_memory(self, agent_config_no_memory, monkeypatch):
        """Test agent initialization without memory."""
        monkeypatch.setattr("fluxibly.agent.base.LLM", lambda config: MockLLM(config))

        agent = Agent(config=agent_config_no_memory)

        assert agent.conversation_history is None

    def test_agent_init_with_context_window(self, basic_agent_config, monkeypatch):
        """Test that context window is properly set for conversation history."""
        monkeypatch.setattr("fluxibly.agent.base.LLM", lambda config: MockLLM(config))

        agent = Agent(config=basic_agent_config)

        # Should allocate 70% of context window for history
        expected_max_tokens = int(4000 * 0.7)
        assert agent.conversation_history is not None
        assert agent.conversation_history.max_tokens == expected_max_tokens

    def test_agent_init_with_mcp_manager(self, basic_agent_config, mock_mcp_manager, monkeypatch):
        """Test agent initialization with MCP client manager."""
        monkeypatch.setattr("fluxibly.agent.base.LLM", lambda config: MockLLM(config))

        agent = Agent(config=basic_agent_config, mcp_client_manager=mock_mcp_manager)

        assert agent.mcp_client_manager == mock_mcp_manager

    def test_from_config_dict(self, monkeypatch):
        """Test creating agent from config dictionary."""
        monkeypatch.setattr("fluxibly.agent.base.LLM", lambda config: MockLLM(config))

        config_dict = {
            "name": "dict_agent",
            "llm": {"framework": "langchain", "model": "gpt-4o"},
            "system_prompt": "Test prompt",
            "mcp_servers": ["tool1"],
        }

        agent = Agent.from_config_dict(config_dict)

        assert agent.config.name == "dict_agent"
        assert agent.system_prompt == "Test prompt"
        assert agent.mcp_servers == ["tool1"]


class TestConversationHistory:
    """Tests for conversation history management."""

    def test_add_user_message(self, basic_agent_config, monkeypatch):
        """Test adding user message to history."""
        monkeypatch.setattr("fluxibly.agent.base.LLM", lambda config: MockLLM(config))

        agent = Agent(config=basic_agent_config)
        agent.add_to_conversation_history("user", "Hello!")

        history = agent.get_conversation_history()
        assert len(history) == 1
        assert history[0].role == "user"
        assert history[0].content == "Hello!"

    def test_add_assistant_message(self, basic_agent_config, monkeypatch):
        """Test adding assistant message to history."""
        monkeypatch.setattr("fluxibly.agent.base.LLM", lambda config: MockLLM(config))

        agent = Agent(config=basic_agent_config)
        agent.add_to_conversation_history("assistant", "Hi there!")

        history = agent.get_conversation_history()
        assert len(history) == 1
        assert history[0].role == "assistant"
        assert history[0].content == "Hi there!"

    def test_add_message_with_metadata(self, basic_agent_config, monkeypatch):
        """Test adding message with metadata."""
        monkeypatch.setattr("fluxibly.agent.base.LLM", lambda config: MockLLM(config))

        agent = Agent(config=basic_agent_config)
        agent.add_to_conversation_history("user", "Test", metadata={"source": "test"})

        history = agent.get_conversation_history()
        assert history[0].metadata == {"source": "test"}

    def test_clear_conversation_history(self, basic_agent_config, monkeypatch):
        """Test clearing conversation history."""
        monkeypatch.setattr("fluxibly.agent.base.LLM", lambda config: MockLLM(config))

        agent = Agent(config=basic_agent_config)
        agent.add_to_conversation_history("user", "Message 1")
        agent.add_to_conversation_history("assistant", "Response 1")

        assert len(agent.get_conversation_history()) == 2

        agent.clear_conversation_history()
        assert len(agent.get_conversation_history()) == 0

    def test_conversation_history_without_memory(self, agent_config_no_memory, monkeypatch):
        """Test that conversation methods warn when memory disabled."""
        monkeypatch.setattr("fluxibly.agent.base.LLM", lambda config: MockLLM(config))

        agent = Agent(config=agent_config_no_memory)

        # Should not raise, just warn
        agent.add_to_conversation_history("user", "Test")
        agent.clear_conversation_history()

        # Should return empty list
        assert agent.get_conversation_history() == []


class TestPreparePrompt:
    """Tests for prepare_prompt method."""

    @pytest.mark.anyio
    async def test_prepare_prompt_basic(self, basic_agent_config, monkeypatch):
        """Test basic prompt preparation without context."""
        monkeypatch.setattr("fluxibly.agent.base.LLM", lambda config: MockLLM(config))

        agent = Agent(config=basic_agent_config)
        prompt = await agent.prepare_prompt("What is the weather?")

        assert "You are a test assistant." in prompt
        assert "What is the weather?" in prompt

    @pytest.mark.anyio
    async def test_prepare_prompt_with_conversation_history(self, basic_agent_config, monkeypatch):
        """Test prompt preparation includes conversation history."""
        monkeypatch.setattr("fluxibly.agent.base.LLM", lambda config: MockLLM(config))

        agent = Agent(config=basic_agent_config)
        agent.add_to_conversation_history("user", "Previous question")
        agent.add_to_conversation_history("assistant", "Previous answer")

        prompt = await agent.prepare_prompt("New question")

        assert "Conversation History:" in prompt
        assert "Previous question" in prompt
        assert "Previous answer" in prompt

    @pytest.mark.anyio
    async def test_prepare_prompt_with_metadata(self, basic_agent_config, monkeypatch):
        """Test prompt preparation with metadata context."""
        monkeypatch.setattr("fluxibly.agent.base.LLM", lambda config: MockLLM(config))

        agent = Agent(config=basic_agent_config)
        context = {"metadata": {"location": "Paris", "language": "French"}}

        prompt = await agent.prepare_prompt("Test", context=context)

        assert "Context Information:" in prompt
        assert "location: Paris" in prompt
        assert "language: French" in prompt

    @pytest.mark.anyio
    async def test_prepare_prompt_with_constraints(self, basic_agent_config, monkeypatch):
        """Test prompt preparation with constraints."""
        monkeypatch.setattr("fluxibly.agent.base.LLM", lambda config: MockLLM(config))

        agent = Agent(config=basic_agent_config)
        context = {"constraints": ["max 100 words", "be concise"]}

        prompt = await agent.prepare_prompt("Test", context=context)

        assert "Constraints:" in prompt
        assert "max 100 words" in prompt
        assert "be concise" in prompt

    @pytest.mark.anyio
    async def test_prepare_prompt_with_previous_results(self, basic_agent_config, monkeypatch):
        """Test prompt preparation with previous results."""
        monkeypatch.setattr("fluxibly.agent.base.LLM", lambda config: MockLLM(config))

        agent = Agent(config=basic_agent_config)
        context = {"previous_results": "Previous analysis found 3 issues"}

        prompt = await agent.prepare_prompt("Test", context=context)

        assert "Previous Results:" in prompt
        assert "Previous analysis found 3 issues" in prompt

    @pytest.mark.anyio
    async def test_prepare_prompt_with_external_history_string(self, basic_agent_config, monkeypatch):
        """Test prompt preparation with external history as string."""
        monkeypatch.setattr("fluxibly.agent.base.LLM", lambda config: MockLLM(config))

        agent = Agent(config=basic_agent_config)
        context = {"conversation_history": "User: Hi\nAssistant: Hello"}

        prompt = await agent.prepare_prompt("Test", context=context)

        assert "Additional Context:" in prompt
        assert "User: Hi" in prompt

    @pytest.mark.anyio
    async def test_prepare_prompt_with_external_history_list(self, basic_agent_config, monkeypatch):
        """Test prompt preparation with external history as list."""
        monkeypatch.setattr("fluxibly.agent.base.LLM", lambda config: MockLLM(config))

        agent = Agent(config=basic_agent_config)
        context = {
            "conversation_history": [
                {"role": "user", "content": "Question"},
                {"role": "assistant", "content": "Answer"},
            ]
        }

        prompt = await agent.prepare_prompt("Test", context=context)

        assert "Additional Context:" in prompt
        assert "User: Question" in prompt
        assert "Assistant: Answer" in prompt


class TestMCPToolSelection:
    """Tests for MCP tool selection."""

    @pytest.mark.anyio
    async def test_select_mcp_tools_strategy_none(self, basic_agent_config, monkeypatch):
        """Test MCP selection with 'none' strategy."""
        monkeypatch.setattr("fluxibly.agent.base.LLM", lambda config: MockLLM(config))

        config = basic_agent_config.model_copy()
        config.mcp_selection_strategy = "none"
        agent = Agent(config=config)

        selected = await agent.select_mcp_tools("Test task", ["web_search", "calculator"])

        assert selected == []

    @pytest.mark.anyio
    async def test_select_mcp_tools_strategy_all(self, basic_agent_config, monkeypatch):
        """Test MCP selection with 'all' strategy."""
        monkeypatch.setattr("fluxibly.agent.base.LLM", lambda config: MockLLM(config))

        config = basic_agent_config.model_copy()
        config.mcp_selection_strategy = "all"
        agent = Agent(config=config)

        selected = await agent.select_mcp_tools("Test task", ["web_search", "calculator", "vision"])

        # Should return only configured servers that are available
        assert set(selected) == {"web_search", "calculator"}

    @pytest.mark.anyio
    async def test_select_mcp_tools_no_manager(self, basic_agent_config, monkeypatch):
        """Test MCP selection with auto strategy but no manager."""
        monkeypatch.setattr("fluxibly.agent.base.LLM", lambda config: MockLLM(config))

        config = basic_agent_config.model_copy()
        config.mcp_selection_strategy = "auto"
        agent = Agent(config=config)  # No MCP manager

        selected = await agent.select_mcp_tools("Test task", ["web_search"])

        # Should fallback to returning all configured servers
        assert selected == agent.mcp_servers


class TestForward:
    """Tests for forward method."""

    @pytest.mark.anyio
    async def test_forward_basic(self, basic_agent_config, monkeypatch):
        """Test basic forward without MCP tools."""
        mock_llm = MockLLM(basic_agent_config.llm)
        monkeypatch.setattr("fluxibly.agent.base.LLM", lambda config: mock_llm)

        agent = Agent(config=basic_agent_config)
        response = await agent.forward("What is 2+2?")

        assert isinstance(response, str)
        assert mock_llm.call_count > 0

    @pytest.mark.anyio
    async def test_forward_adds_to_history(self, basic_agent_config, monkeypatch):
        """Test that forward adds messages to conversation history."""
        mock_llm = MockLLM(basic_agent_config.llm)
        mock_llm.forward = lambda prompt, **kwargs: "Test response"
        monkeypatch.setattr("fluxibly.agent.base.LLM", lambda config: mock_llm)

        agent = Agent(config=basic_agent_config)
        await agent.forward("Test question")

        history = agent.get_conversation_history()
        assert len(history) == 2  # User message + assistant response
        assert history[0].role == "user"
        assert history[0].content == "Test question"
        assert history[1].role == "assistant"
        assert history[1].content == "Test response"

    @pytest.mark.anyio
    async def test_forward_without_memory(self, agent_config_no_memory, monkeypatch):
        """Test forward without memory doesn't store history."""
        mock_llm = MockLLM(agent_config_no_memory.llm)
        mock_llm.forward = lambda prompt, **kwargs: "Test response"
        monkeypatch.setattr("fluxibly.agent.base.LLM", lambda config: mock_llm)

        agent = Agent(config=agent_config_no_memory)
        await agent.forward("Test question")

        # Should not have stored anything
        assert agent.get_conversation_history() == []


class TestUtilityMethods:
    """Tests for utility methods."""

    def test_format_message_list(self, basic_agent_config, monkeypatch):
        """Test formatting message list."""
        monkeypatch.setattr("fluxibly.agent.base.LLM", lambda config: MockLLM(config))

        agent = Agent(config=basic_agent_config)
        messages = [
            {"role": "user", "content": "Question"},
            {"role": "assistant", "content": "Answer"},
            {"role": "tool", "name": "calculator", "content": "42"},
        ]

        formatted = agent._format_message_list(messages)

        assert "User: Question" in formatted
        assert "Assistant: Answer" in formatted
        assert "Tool (calculator): 42" in formatted

    def test_format_message_list_with_invalid_messages(self, basic_agent_config, monkeypatch):
        """Test formatting message list with invalid entries."""
        monkeypatch.setattr("fluxibly.agent.base.LLM", lambda config: MockLLM(config))

        agent = Agent(config=basic_agent_config)
        messages = [
            {"role": "user", "content": "Valid"},
            "invalid_message",  # Should be skipped
            None,  # Should be skipped
        ]

        formatted = agent._format_message_list(messages)

        assert "User: Valid" in formatted
        # Invalid messages should be skipped without error

    def test_parse_tool_decision_valid_json(self, basic_agent_config, monkeypatch):
        """Test parsing valid tool decision JSON."""
        monkeypatch.setattr("fluxibly.agent.base.LLM", lambda config: MockLLM(config))

        agent = Agent(config=basic_agent_config)
        response = '{"tools": [{"name": "calculator", "args": {"expression": "2+2"}}]}'

        result = agent._parse_tool_decision(response)

        assert len(result) == 1
        assert result[0][0] == "calculator"
        assert result[0][1] == {"expression": "2+2"}

    def test_parse_tool_decision_invalid_json(self, basic_agent_config, monkeypatch):
        """Test parsing invalid tool decision JSON."""
        monkeypatch.setattr("fluxibly.agent.base.LLM", lambda config: MockLLM(config))

        agent = Agent(config=basic_agent_config)
        response = "invalid json"

        result = agent._parse_tool_decision(response)

        assert result == []

    def test_parse_tool_selection_valid(self, basic_agent_config, monkeypatch):
        """Test parsing valid tool selection."""
        monkeypatch.setattr("fluxibly.agent.base.LLM", lambda config: MockLLM(config))

        agent = Agent(config=basic_agent_config)
        response = '{"selected": ["web_search", "calculator"]}'

        result = agent._parse_tool_selection(response)

        assert result == ["web_search", "calculator"]

    def test_parse_tool_selection_invalid(self, basic_agent_config, monkeypatch):
        """Test parsing invalid tool selection."""
        monkeypatch.setattr("fluxibly.agent.base.LLM", lambda config: MockLLM(config))

        agent = Agent(config=basic_agent_config)
        response = "not json"

        result = agent._parse_tool_selection(response)

        assert result == []

    def test_repr(self, basic_agent_config, monkeypatch):
        """Test string representation."""
        mock_llm = MockLLM(basic_agent_config.llm)
        monkeypatch.setattr("fluxibly.agent.base.LLM", lambda config: mock_llm)

        agent = Agent(config=basic_agent_config)
        repr_str = repr(agent)

        assert "Agent" in repr_str
        assert "test_agent" in repr_str
        assert "gpt-4o" in repr_str
