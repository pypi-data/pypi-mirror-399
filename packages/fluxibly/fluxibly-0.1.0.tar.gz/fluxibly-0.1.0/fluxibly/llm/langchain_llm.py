"""LangChain LLM Implementation.

This module provides LangChain-based LLM implementation with support for:
- OpenAI models (GPT-4, GPT-3.5, etc.)
- Anthropic models (Claude 3.5, Claude 3, etc.)
- Full LangGraph compatibility
"""

from collections.abc import Generator
from typing import Any

import loguru
from langchain_anthropic import ChatAnthropic
from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.messages import HumanMessage
from langchain_openai import ChatOpenAI

from fluxibly.llm.base import BaseLLM, LLMConfig, register_llm_framework

logger = loguru.logger.bind(name=__name__)


class LangChainLLM(BaseLLM):
    """LangChain-based LLM implementation.

    This implementation uses LangChain's ChatModel abstraction to support
    various models and provides seamless integration with LangGraph.

    Supported providers:
    - OpenAI (gpt-4o, gpt-3.5-turbo, etc.)
    - Anthropic (claude-3-5-sonnet, claude-3-opus, etc.)
    - Custom OpenAI-compatible endpoints

    Attributes:
        config: LLMConfig object
        chat_model: LangChain ChatModel instance
    """

    def __init__(self, config: LLMConfig) -> None:
        """Initialize LangChain LLM.

        Args:
            config: LLMConfig object with model and parameters
        """
        super().__init__(config)
        self.chat_model = self._create_chat_model()

    def _create_chat_model(self) -> BaseChatModel:
        """Create appropriate LangChain ChatModel based on model name.

        Returns:
            BaseChatModel: Initialized chat model

        Raises:
            ValueError: If model provider is not supported
        """
        model_name = self.config.model.lower()

        # Build common kwargs
        kwargs: dict[str, Any] = {
            "temperature": self.config.temperature,
            "model_kwargs": {},
        }

        # Add optional parameters
        if self.config.max_tokens is not None:
            kwargs["max_tokens"] = self.config.max_tokens
        if self.config.timeout is not None:
            kwargs["timeout"] = self.config.timeout
        if self.config.max_retries is not None:
            kwargs["max_retries"] = self.config.max_retries

        # Add model-specific parameters
        if self.config.top_p is not None:
            kwargs["model_kwargs"]["top_p"] = self.config.top_p
        if self.config.frequency_penalty is not None:
            kwargs["model_kwargs"]["frequency_penalty"] = self.config.frequency_penalty
        if self.config.presence_penalty is not None:
            kwargs["model_kwargs"]["presence_penalty"] = self.config.presence_penalty

        # Merge additional parameters
        kwargs["model_kwargs"].update(self.config.additional_params)

        # Determine provider and create chat model
        if "gpt" in model_name or "o1" in model_name or model_name.startswith("openai/"):
            kwargs["model"] = self.config.model
            if self.config.api_key is not None:
                kwargs["api_key"] = self.config.api_key
            if self.config.api_base is not None:
                kwargs["base_url"] = self.config.api_base
            return ChatOpenAI(**kwargs)

        elif "claude" in model_name or model_name.startswith("anthropic/"):
            kwargs["model"] = self.config.model
            if self.config.api_key is not None:
                kwargs["api_key"] = self.config.api_key
            if self.config.api_base is not None:
                kwargs["base_url"] = self.config.api_base
            return ChatAnthropic(**kwargs)

        else:
            # Default to OpenAI for unknown models
            logger.warning(
                "Unknown model provider, defaulting to OpenAI-compatible API",
                model=self.config.model,
            )
            kwargs["model"] = self.config.model
            if self.config.api_key is not None:
                kwargs["api_key"] = self.config.api_key
            if self.config.api_base is not None:
                kwargs["base_url"] = self.config.api_base
            return ChatOpenAI(**kwargs)

    def _forward_impl(self, prompt: str, **kwargs: Any) -> str:
        """Forward prompt to LangChain ChatModel.

        Args:
            prompt: Input prompt string
            **kwargs: Optional parameter overrides (temperature, max_tokens)

        Returns:
            str: Generated text response

        Raises:
            Exception: If LLM call fails after retries
        """
        message = HumanMessage(content=prompt)

        # Build parameter overrides
        invoke_kwargs = {}
        if kwargs:
            config_overrides = {}
            if "temperature" in kwargs:
                config_overrides["temperature"] = kwargs["temperature"]
            if "max_tokens" in kwargs:
                config_overrides["max_tokens"] = kwargs["max_tokens"]

            if config_overrides:
                invoke_kwargs["config"] = {"configurable": config_overrides}

        # Invoke model
        response = self.chat_model.invoke([message], **invoke_kwargs)

        # Extract text content
        content = response.content
        if isinstance(content, str):
            result = content
        elif isinstance(content, list):
            result = "".join(str(block) if isinstance(block, str) else block.get("text", "") for block in content)
        else:
            result = str(content)

        if not result:
            logger.warning("LLM returned empty response", model=self.config.model)
            return ""

        return result

    def _forward_stream_impl(self, prompt: str, **kwargs: Any) -> Generator[str, None, None]:
        """Stream responses from LangChain ChatModel.

        Args:
            prompt: Input prompt string
            **kwargs: Optional parameter overrides

        Yields:
            str: Individual tokens or chunks
        """
        message = HumanMessage(content=prompt)

        # Build parameter overrides
        stream_kwargs = {}
        if kwargs:
            config_overrides = {}
            if "temperature" in kwargs:
                config_overrides["temperature"] = kwargs["temperature"]
            if "max_tokens" in kwargs:
                config_overrides["max_tokens"] = kwargs["max_tokens"]

            if config_overrides:
                stream_kwargs["config"] = {"configurable": config_overrides}

        # Stream response
        for chunk in self.chat_model.stream([message], **stream_kwargs):
            if hasattr(chunk, "content") and chunk.content:
                content = chunk.content
                if isinstance(content, str):
                    yield content
                elif isinstance(content, list):
                    for block in content:
                        if isinstance(block, str):
                            yield block
                        elif isinstance(block, dict) and "text" in block:
                            yield block["text"]


# Register this implementation
register_llm_framework("langchain", LangChainLLM)
