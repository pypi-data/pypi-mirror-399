"""LLM Base Module for Fluxibly Framework.

This module provides the foundational components for pluggable LLM implementations:
- BaseLLM: Base class for all LLM implementations
- LLMConfig: Configuration with framework selection
- LLMRegistry: Registry for LLM framework implementations
- LLM(): Factory function for creating LLM instances

Framework implementations must inherit from BaseLLM and override:
- forward(): Synchronous text generation
- forward_stream(): Streaming text generation

All initialization parameters are configurable via config files.
"""

import time
from collections.abc import Generator
from typing import Any

import loguru
from pydantic import BaseModel, Field

logger = loguru.logger.bind(name=__name__)


class LLMConfig(BaseModel):
    """Configuration for LLM initialization.

    All parameters can be loaded from config files (YAML/JSON).

    Attributes:
        framework: LLM framework to use ("langchain", "litellm")
        model: Model identifier (e.g., "gpt-4o", "claude-3-5-sonnet-20241022", "ollama/llama2")
        temperature: Controls randomness (0.0-2.0). Higher = more random
        max_tokens: Maximum tokens to generate in response
        top_p: Nucleus sampling parameter (0.0-1.0)
        frequency_penalty: Reduces repetition (-2.0 to 2.0)
        presence_penalty: Encourages topic diversity (-2.0 to 2.0)
        api_key: API key for proprietary models (optional, can use env var)
        api_base: Custom API endpoint (optional)
        timeout: Request timeout in seconds
        max_retries: Maximum number of retry attempts on failure
        streaming: Whether to stream responses
        additional_params: Any additional model-specific parameters
    """

    framework: str = Field(default="langchain", description="LLM framework ('langchain', 'litellm')")
    model: str = Field(..., description="Model identifier (e.g., 'gpt-4o', 'claude-3-5-sonnet-20241022')")
    temperature: float = Field(default=0.7, ge=0.0, le=2.0, description="Sampling temperature")
    max_tokens: int | None = Field(default=None, description="Maximum tokens to generate")
    top_p: float | None = Field(default=None, ge=0.0, le=1.0, description="Nucleus sampling parameter")
    frequency_penalty: float | None = Field(default=None, ge=-2.0, le=2.0, description="Frequency penalty")
    presence_penalty: float | None = Field(default=None, ge=-2.0, le=2.0, description="Presence penalty")
    api_key: str | None = Field(default=None, description="API key (can use env var)")
    api_base: str | None = Field(default=None, description="Custom API endpoint")
    timeout: int = Field(default=60, description="Request timeout in seconds")
    max_retries: int = Field(default=3, description="Maximum retry attempts")
    streaming: bool = Field(default=False, description="Enable streaming responses")
    additional_params: dict[str, Any] = Field(default_factory=dict, description="Additional model parameters")


class BaseLLM:
    """Base class for LLM implementations.

    All LLM implementations must inherit from this class and implement:
    - _forward_impl(): Synchronous text generation implementation
    - _forward_stream_impl(): Streaming text generation implementation

    The base class provides comprehensive logging that works for any framework.

    Design Philosophy:
    - Simple interface: Just forward prompts to underlying LLM
    - No complex logic: Prompt engineering happens in higher layers
    - Framework-agnostic: Each implementation handles its own framework
    - Comprehensive logging: Automatic logging of all LLM calls

    Example:
        >>> class MyLLM(BaseLLM):
        ...     def _forward_impl(self, prompt: str, **kwargs: Any) -> str:
        ...         return "response"
        ...     def _forward_stream_impl(self, prompt: str, **kwargs: Any) -> Generator[str, None, None]:
        ...         yield "response"
    """

    def __init__(self, config: LLMConfig) -> None:
        """Initialize the LLM with configuration.

        Args:
            config: LLMConfig object containing all parameters
        """
        self.config = config
        self.logger = loguru.logger.bind(
            name=self.__class__.__name__,
            framework=config.framework,
            model=config.model,
        )

    def forward(self, prompt: str, **kwargs: Any) -> str:
        """Forward a prompt to the LLM and return response.

        This method provides comprehensive logging and delegates to _forward_impl().

        Args:
            prompt: Input prompt string
            **kwargs: Optional parameter overrides

        Returns:
            str: Generated text response

        Raises:
            Exception: If LLM call fails after retries
        """
        # Log request
        self.logger.info(
            "LLM request started",
            prompt_length=len(prompt),
            kwargs=kwargs,
        )

        start_time = time.time()

        try:
            # Delegate to implementation
            result = self._forward_impl(prompt, **kwargs)

            # Calculate metrics
            elapsed_time = time.time() - start_time
            response_length = len(result) if result else 0

            # Log success
            self.logger.info(
                "LLM request completed",
                elapsed_time=f"{elapsed_time:.2f}s",
                prompt_length=len(prompt),
                response_length=response_length,
            )

            # Log detailed debug info
            self.logger.debug(
                "LLM request details",
                prompt_preview=prompt[:100] + "..." if len(prompt) > 100 else prompt,
                response_preview=result[:100] + "..." if response_length > 100 else result,
                elapsed_time=elapsed_time,
            )

            return result

        except Exception as e:
            # Calculate elapsed time even on failure
            elapsed_time = time.time() - start_time

            # Log failure with exception details
            self.logger.error(
                "LLM request failed",
                elapsed_time=f"{elapsed_time:.2f}s",
                prompt_length=len(prompt),
                error_type=type(e).__name__,
                error_message=str(e),
            )

            # Re-raise the exception for caller to handle
            raise

    def forward_stream(self, prompt: str, **kwargs: Any) -> Generator[str, None, None]:
        """Stream responses from the LLM token by token.

        This method provides comprehensive logging and delegates to _forward_stream_impl().

        Args:
            prompt: Input prompt string
            **kwargs: Optional parameter overrides

        Yields:
            str: Individual tokens or chunks

        Raises:
            Exception: If LLM streaming fails
        """
        # Log request
        self.logger.info(
            "LLM streaming request started",
            prompt_length=len(prompt),
            kwargs=kwargs,
        )

        start_time = time.time()
        total_chunks = 0
        total_length = 0

        try:
            # Delegate to implementation and track metrics
            for chunk in self._forward_stream_impl(prompt, **kwargs):
                total_chunks += 1
                total_length += len(chunk)
                yield chunk

            # Calculate metrics
            elapsed_time = time.time() - start_time

            # Log success
            self.logger.info(
                "LLM streaming completed",
                elapsed_time=f"{elapsed_time:.2f}s",
                prompt_length=len(prompt),
                total_chunks=total_chunks,
                total_length=total_length,
            )

            # Log detailed debug info
            self.logger.debug(
                "LLM streaming details",
                prompt_preview=prompt[:100] + "..." if len(prompt) > 100 else prompt,
                total_chunks=total_chunks,
                total_length=total_length,
                elapsed_time=elapsed_time,
                avg_chunk_size=total_length / total_chunks if total_chunks > 0 else 0,
            )

        except Exception as e:
            # Calculate elapsed time even on failure
            elapsed_time = time.time() - start_time

            # Log failure with exception details
            self.logger.error(
                "LLM streaming failed",
                elapsed_time=f"{elapsed_time:.2f}s",
                prompt_length=len(prompt),
                chunks_received=total_chunks,
                error_type=type(e).__name__,
                error_message=str(e),
            )

            # Re-raise the exception for caller to handle
            raise

    def _forward_impl(self, prompt: str, **kwargs: Any) -> str:
        """Implementation of forward prompt to LLM.

        Subclasses must override this method instead of forward().

        Args:
            prompt: Input prompt string
            **kwargs: Optional parameter overrides

        Returns:
            str: Generated text response

        Raises:
            NotImplementedError: Must be implemented by subclass
        """
        raise NotImplementedError("Subclass must implement _forward_impl()")

    def _forward_stream_impl(self, prompt: str, **kwargs: Any) -> Generator[str, None, None]:
        """Implementation of streaming responses from LLM.

        Subclasses must override this method instead of forward_stream().

        Args:
            prompt: Input prompt string
            **kwargs: Optional parameter overrides

        Yields:
            str: Individual tokens or chunks

        Raises:
            NotImplementedError: Must be implemented by subclass
        """
        raise NotImplementedError("Subclass must implement _forward_stream_impl()")
        yield  # Make this a generator for type checking

    @classmethod
    def from_config_dict(cls, config_dict: dict[str, Any]) -> "BaseLLM":
        """Create LLM instance from configuration dictionary.

        This method uses the factory function to create the appropriate
        implementation based on the framework field.

        Args:
            config_dict: Dictionary containing LLM configuration

        Returns:
            BaseLLM: Initialized LLM instance

        Example:
            >>> config = {"framework": "langchain", "model": "gpt-4o"}
            >>> llm = BaseLLM.from_config_dict(config)
        """
        config = LLMConfig(**config_dict)
        return LLM(config=config)

    def __repr__(self) -> str:
        """String representation."""
        return f"{self.__class__.__name__}(model={self.config.model})"


class LLMRegistry:
    """Registry for LLM framework implementations.

    Managing framework implementations.
    Frameworks must be explicitly registered before use.

    Example:
        >>> registry = LLMRegistry()
        >>> registry.register("myframework", MyLLM)
        >>> implementation = registry.get("myframework")
    """

    def __init__(self) -> None:
        """Initialize the registry."""
        self._implementations: dict[str, type[BaseLLM]] = {}

    def register(self, framework: str, implementation: type[BaseLLM]) -> None:
        """Register an LLM framework implementation.

        Args:
            framework: Framework name (e.g., "langchain", "litellm")
            implementation: BaseLLM subclass for this framework
        """
        self._implementations[framework] = implementation
        logger.debug("Registered LLM framework", framework=framework, implementation=implementation.__name__)

    def get(self, framework: str) -> type[BaseLLM]:
        """Get implementation for a framework.

        Args:
            framework: Framework name

        Returns:
            BaseLLM subclass for the framework

        Raises:
            ValueError: If framework is not registered
        """
        if framework not in self._implementations:
            available = list(self._implementations.keys())
            raise ValueError(f"LLM framework '{framework}' not registered. Available frameworks: {available}")
        return self._implementations[framework]

    def list_frameworks(self) -> list[str]:
        """List all registered frameworks.

        Returns:
            List of framework names
        """
        return list(self._implementations.keys())


# Global registry instance
_llm_registry = LLMRegistry()


def LLM(config: LLMConfig) -> BaseLLM:
    """Factory function to create LLM instances.

    This function provides backward compatibility by acting as a drop-in
    replacement for the old LLM class. It reads the framework field from
    config and returns the appropriate implementation.

    Args:
        config: LLMConfig with framework field

    Returns:
        BaseLLM instance (LangChainLLM, LiteLLM, etc.)

    Raises:
        ValueError: If framework is not registered

    Example:
        >>> config = LLMConfig(framework="langchain", model="gpt-4o")
        >>> llm = LLM(config=config)  # Returns LangChainLLM instance
        >>> response = llm.forward("Hello")
    """
    implementation_class = _llm_registry.get(config.framework)
    return implementation_class(config=config)


def register_llm_framework(framework: str, implementation: type[BaseLLM]) -> None:
    """Register an LLM framework implementation.

    Public API for registering custom LLM frameworks.

    Args:
        framework: Framework name
        implementation: BaseLLM subclass

    Example:
        >>> class MyLLM(BaseLLM):
        ...     def forward(self, prompt: str, **kwargs: Any) -> str:
        ...         return "response"
        ...     def forward_stream(self, prompt: str, **kwargs: Any) -> Generator[str, None, None]:
        ...         yield "response"
        >>> register_llm_framework("custom", MyLLM)
    """
    _llm_registry.register(framework, implementation)
