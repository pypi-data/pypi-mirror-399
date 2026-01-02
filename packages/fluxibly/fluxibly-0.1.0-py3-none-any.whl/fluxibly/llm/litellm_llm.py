"""LiteLLM Implementation.

This module provides LiteLLM-based implementation with unified access to:
- 100+ LLM providers (OpenAI, Anthropic, Cohere, HuggingFace, etc.)
- Simplified provider abstraction
- Automatic provider detection from model name
"""

from collections.abc import Generator
from typing import Any

import litellm
import loguru

from fluxibly.llm.base import BaseLLM, LLMConfig, register_llm_framework

logger = loguru.logger.bind(name=__name__)


class LiteLLM(BaseLLM):
    """LiteLLM-based LLM implementation.

    This implementation uses LiteLLM to provide unified access to 100+ LLM
    providers through a single interface. LiteLLM automatically handles
    provider-specific APIs and authentication.

    Supported providers (examples):
    - OpenAI: gpt-4o, gpt-3.5-turbo
    - Anthropic: claude-3-5-sonnet-20241022, claude-3-opus
    - Cohere: command-r-plus
    - Replicate: llama-2-70b
    - HuggingFace: any model on HuggingFace
    - Together AI, Anyscale, Groq, and 90+ more

    Provider detection:
    - Automatic from model name (e.g., "claude-3-5-sonnet" -> Anthropic)
    - Or explicit with prefix (e.g., "anthropic/claude-3-5-sonnet")
    """

    def __init__(self, config: LLMConfig) -> None:
        """Initialize LiteLLM.

        Args:
            config: LLMConfig object with model and parameters
        """
        super().__init__(config)
        self._configure_litellm()

    def _configure_litellm(self) -> None:
        """Configure LiteLLM with settings from config."""
        # Set global LiteLLM settings
        if self.config.api_base:
            litellm.api_base = self.config.api_base

        # Disable verbose logging unless debug mode
        litellm.suppress_debug_info = True

    def _build_completion_kwargs(self, prompt: str, **overrides: Any) -> dict[str, Any]:
        """Build kwargs for litellm.completion() call.

        Args:
            prompt: Input prompt
            **overrides: Parameter overrides

        Returns:
            dict: kwargs for litellm.completion()
        """
        kwargs: dict[str, Any] = {
            "model": self.config.model,
            "messages": [{"role": "user", "content": prompt}],
            "temperature": overrides.get("temperature", self.config.temperature),
            "timeout": self.config.timeout,
            "max_retries": self.config.max_retries,
        }

        # Add optional parameters
        if self.config.max_tokens or "max_tokens" in overrides:
            kwargs["max_tokens"] = overrides.get("max_tokens", self.config.max_tokens)

        if self.config.top_p is not None:
            kwargs["top_p"] = self.config.top_p

        if self.config.frequency_penalty is not None:
            kwargs["frequency_penalty"] = self.config.frequency_penalty

        if self.config.presence_penalty is not None:
            kwargs["presence_penalty"] = self.config.presence_penalty

        # Add API credentials
        if self.config.api_key:
            kwargs["api_key"] = self.config.api_key

        # Add additional parameters
        kwargs.update(self.config.additional_params)

        return kwargs

    def _forward_impl(self, prompt: str, **kwargs: Any) -> str:
        """Forward prompt to LiteLLM.

        Args:
            prompt: Input prompt string
            **kwargs: Optional parameter overrides

        Returns:
            str: Generated text response

        Raises:
            Exception: If LLM call fails after retries
        """
        completion_kwargs = self._build_completion_kwargs(prompt, **kwargs)
        response = litellm.completion(**completion_kwargs)

        # Extract text from response
        if hasattr(response, "choices") and response.choices and len(response.choices) > 0:  # type: ignore
            result = response.choices[0].message.content or ""  # type: ignore
        else:
            result = ""

        if not result:
            logger.warning("LiteLLM returned empty response", model=self.config.model)
            return ""

        return result

    def _forward_stream_impl(self, prompt: str, **kwargs: Any) -> Generator[str, None, None]:
        """Stream responses from LiteLLM.

        Args:
            prompt: Input prompt string
            **kwargs: Optional parameter overrides

        Yields:
            str: Individual tokens or chunks
        """
        completion_kwargs = self._build_completion_kwargs(prompt, **kwargs)
        completion_kwargs["stream"] = True

        response = litellm.completion(**completion_kwargs)

        for chunk in response:  # type: ignore
            if hasattr(chunk, "choices") and chunk.choices and len(chunk.choices) > 0:  # type: ignore
                delta = chunk.choices[0].delta  # type: ignore
                if hasattr(delta, "content") and delta.content:
                    yield delta.content


# Register this implementation
register_llm_framework("litellm", LiteLLM)
