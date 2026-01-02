"""Unit tests for LLM module."""

from unittest.mock import MagicMock, patch

import pytest
from langchain_core.messages import AIMessage

from fluxibly.llm import LLM, BaseLLM, LLMConfig


@pytest.fixture
def llm_config() -> LLMConfig:
    """Create a test LLM configuration."""
    return LLMConfig(
        model="gpt-4o",
        temperature=0.7,
        max_tokens=100,
        timeout=30,
        max_retries=2,
    )


def test_llm_config_creation() -> None:
    """Test LLMConfig model creation with required fields."""
    config = LLMConfig(model="gpt-4o")
    assert config.model == "gpt-4o"
    assert config.temperature == 0.7  # default value
    assert config.timeout == 60  # default value
    assert config.max_retries == 3  # default value


def test_llm_config_with_all_fields() -> None:
    """Test LLMConfig with all optional fields."""
    config = LLMConfig(
        model="claude-3-5-sonnet-20241022",
        temperature=0.5,
        max_tokens=200,
        top_p=0.9,
        frequency_penalty=0.5,
        presence_penalty=0.5,
        api_key="test_key",
        api_base="https://api.example.com",
        timeout=120,
        max_retries=5,
        streaming=True,
        additional_params={"custom": "value"},
    )
    assert config.model == "claude-3-5-sonnet-20241022"
    assert config.temperature == 0.5
    assert config.max_tokens == 200
    assert config.streaming is True


@patch("fluxibly.llm.langchain_llm.ChatOpenAI")
def test_llm_initialization(mock_chat_openai: MagicMock, llm_config: LLMConfig) -> None:
    """Test LLM initialization."""
    llm = LLM(config=llm_config)
    assert llm.config == llm_config
    assert llm.config.model == "gpt-4o"
    assert hasattr(llm, "chat_model")
    mock_chat_openai.assert_called_once()


@patch("fluxibly.llm.langchain_llm.ChatOpenAI")
def test_llm_from_config_dict(mock_chat_openai: MagicMock) -> None:
    """Test creating LLM from config dictionary."""
    config_dict = {"model": "gpt-4o", "temperature": 0.8, "max_tokens": 150}
    llm = BaseLLM.from_config_dict(config_dict)
    assert llm.config.model == "gpt-4o"
    assert llm.config.temperature == 0.8
    assert llm.config.max_tokens == 150


@patch("fluxibly.llm.langchain_llm.ChatOpenAI")
def test_llm_repr(mock_chat_openai: MagicMock, llm_config: LLMConfig) -> None:
    """Test LLM string representation."""
    llm = LLM(config=llm_config)
    repr_str = repr(llm)
    assert "LangChainLLM" in repr_str
    assert "gpt-4o" in repr_str


@patch("fluxibly.llm.langchain_llm.ChatOpenAI")
def test_forward_success(mock_chat_openai: MagicMock, llm_config: LLMConfig) -> None:
    """Test successful LLM forward call."""
    # Mock the chat model instance
    mock_instance = MagicMock()
    mock_chat_openai.return_value = mock_instance

    # Mock the response
    mock_response = AIMessage(content="This is a test response")
    mock_instance.invoke.return_value = mock_response

    llm = LLM(config=llm_config)
    response = llm.forward("Test prompt")

    # Assertions
    assert response == "This is a test response"
    mock_instance.invoke.assert_called_once()


@patch("fluxibly.llm.langchain_llm.ChatOpenAI")
def test_forward_with_overrides(mock_chat_openai: MagicMock, llm_config: LLMConfig) -> None:
    """Test LLM forward call with parameter overrides."""
    mock_instance = MagicMock()
    mock_chat_openai.return_value = mock_instance
    mock_response = AIMessage(content="Response")
    mock_instance.invoke.return_value = mock_response

    llm = LLM(config=llm_config)
    llm.forward("Test prompt", temperature=0.3, max_tokens=50)

    # Verify invoke was called with config overrides
    mock_instance.invoke.assert_called_once()
    call_args = mock_instance.invoke.call_args
    assert "config" in call_args[1]
    assert call_args[1]["config"]["configurable"]["temperature"] == 0.3
    assert call_args[1]["config"]["configurable"]["max_tokens"] == 50


@patch("fluxibly.llm.langchain_llm.ChatOpenAI")
def test_forward_empty_response(mock_chat_openai: MagicMock, llm_config: LLMConfig) -> None:
    """Test LLM forward call with empty response."""
    mock_instance = MagicMock()
    mock_chat_openai.return_value = mock_instance
    mock_response = AIMessage(content="")
    mock_instance.invoke.return_value = mock_response

    llm = LLM(config=llm_config)
    response = llm.forward("Test prompt")

    assert response == ""


@patch("fluxibly.llm.langchain_llm.ChatOpenAI")
def test_forward_exception(mock_chat_openai: MagicMock, llm_config: LLMConfig) -> None:
    """Test LLM forward call with exception."""
    mock_instance = MagicMock()
    mock_chat_openai.return_value = mock_instance
    mock_instance.invoke.side_effect = Exception("API Error")

    llm = LLM(config=llm_config)
    with pytest.raises(Exception, match="API Error"):
        llm.forward("Test prompt")


@patch("fluxibly.llm.langchain_llm.ChatOpenAI")
def test_forward_stream_success(mock_chat_openai: MagicMock, llm_config: LLMConfig) -> None:
    """Test successful LLM streaming call."""
    mock_instance = MagicMock()
    mock_chat_openai.return_value = mock_instance

    # Create mock chunks
    chunks = [
        AIMessage(content="This "),
        AIMessage(content="is "),
        AIMessage(content="a "),
        AIMessage(content="stream"),
    ]
    mock_instance.stream.return_value = iter(chunks)

    llm = LLM(config=llm_config)
    result = list(llm.forward_stream("Test prompt"))

    # Assertions
    assert result == ["This ", "is ", "a ", "stream"]
    mock_instance.stream.assert_called_once()


@patch("fluxibly.llm.langchain_llm.ChatOpenAI")
def test_forward_stream_with_empty_content(mock_chat_openai: MagicMock, llm_config: LLMConfig) -> None:
    """Test streaming call with some empty content chunks."""
    mock_instance = MagicMock()
    mock_chat_openai.return_value = mock_instance

    chunks = [
        AIMessage(content="Hello"),
        AIMessage(content=""),  # Empty chunk, should be skipped
        AIMessage(content=" World"),
    ]
    mock_instance.stream.return_value = iter(chunks)

    llm = LLM(config=llm_config)
    result = list(llm.forward_stream("Test prompt"))

    assert result == ["Hello", " World"]


@patch("fluxibly.llm.langchain_llm.ChatOpenAI")
def test_forward_stream_exception(mock_chat_openai: MagicMock, llm_config: LLMConfig) -> None:
    """Test streaming call with exception."""
    mock_instance = MagicMock()
    mock_chat_openai.return_value = mock_instance
    mock_instance.stream.side_effect = Exception("Streaming Error")

    llm = LLM(config=llm_config)
    with pytest.raises(Exception, match="Streaming Error"):
        list(llm.forward_stream("Test prompt"))


def test_llm_config_validation() -> None:
    """Test LLMConfig field validation."""
    # Test invalid temperature (too high)
    with pytest.raises(ValueError):
        LLMConfig(model="gpt-4o", temperature=3.0)

    # Test invalid temperature (negative)
    with pytest.raises(ValueError):
        LLMConfig(model="gpt-4o", temperature=-1.0)

    # Test invalid top_p (too high)
    with pytest.raises(ValueError):
        LLMConfig(model="gpt-4o", top_p=1.5)


@patch("fluxibly.llm.langchain_llm.ChatOpenAI")
def test_forward_with_api_credentials(mock_chat_openai: MagicMock) -> None:
    """Test forward call with API credentials in config."""
    config = LLMConfig(
        model="gpt-4o",
        api_key="test_api_key",
        api_base="https://custom.api.com",
    )
    _llm = LLM(config=config)

    # Verify ChatOpenAI was initialized with correct parameters
    call_kwargs = mock_chat_openai.call_args[1]
    assert call_kwargs["api_key"] == "test_api_key"
    assert call_kwargs["base_url"] == "https://custom.api.com"


@patch("fluxibly.llm.langchain_llm.ChatOpenAI")
def test_forward_with_additional_params(mock_chat_openai: MagicMock) -> None:
    """Test forward call with additional parameters."""
    config = LLMConfig(
        model="gpt-4o",
        additional_params={"custom_param": "custom_value", "another": 123},
    )
    _llm = LLM(config=config)

    # Verify additional params were passed to model_kwargs
    call_kwargs = mock_chat_openai.call_args[1]
    assert call_kwargs["model_kwargs"]["custom_param"] == "custom_value"
    assert call_kwargs["model_kwargs"]["another"] == 123


@patch("fluxibly.llm.langchain_llm.ChatAnthropic")
def test_claude_model_initialization(mock_chat_anthropic: MagicMock) -> None:
    """Test that Claude models use ChatAnthropic."""
    config = LLMConfig(model="claude-3-5-sonnet-20241022", temperature=0.5)
    _llm = LLM(config=config)

    # Verify ChatAnthropic was called
    mock_chat_anthropic.assert_called_once()
    call_kwargs = mock_chat_anthropic.call_args[1]
    assert call_kwargs["model"] == "claude-3-5-sonnet-20241022"
    assert call_kwargs["temperature"] == 0.5


@patch("fluxibly.llm.langchain_llm.ChatOpenAI")
def test_openai_model_initialization(mock_chat_openai: MagicMock) -> None:
    """Test that OpenAI models use ChatOpenAI."""
    config = LLMConfig(model="gpt-4o", temperature=0.8)
    _llm = LLM(config=config)

    # Verify ChatOpenAI was called
    mock_chat_openai.assert_called_once()
    call_kwargs = mock_chat_openai.call_args[1]
    assert call_kwargs["model"] == "gpt-4o"
    assert call_kwargs["temperature"] == 0.8
