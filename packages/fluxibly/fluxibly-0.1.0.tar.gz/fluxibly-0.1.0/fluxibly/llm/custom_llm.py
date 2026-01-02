"""Custom LLM Implementation Template.

This template provides a complete guide for creating your own LLM framework
implementation in Fluxibly. Follow the instructions and implement the required
methods to integrate any LLM provider.

HOW TO USE THIS TEMPLATE:
1. Copy this file to a new file (e.g., my_provider_llm.py)
2. Replace "CustomLLM" with your provider name (e.g., "OpenRouterLLM", "HuggingFaceLLM")
3. Implement _forward_impl() and _forward_stream_impl() methods
4. Register your implementation at the bottom of the file
5. Import your module in __init__.py to enable auto-registration

IMPORTANT DESIGN PRINCIPLES:
- Inherit from BaseLLM
- Implement _forward_impl() instead of forward()
- Implement _forward_stream_impl() instead of forward_stream()
- All logging is handled automatically by BaseLLM
- All error handling is automatic (just let exceptions propagate)
- Keep implementation focused on API calls only
"""

from collections.abc import Generator
from typing import Any

import loguru

from fluxibly.llm.base import BaseLLM, LLMConfig, register_llm_framework

logger = loguru.logger.bind(name=__name__)


class CustomLLM(BaseLLM):
    """Custom LLM implementation template.

    Replace this class name and docstring with your provider name.
    Example: OpenRouterLLM, HuggingFaceLLM, LocalLLM, etc.

    This implementation provides [DESCRIBE YOUR PROVIDER]:
    - [Feature 1: e.g., Access to 100+ models]
    - [Feature 2: e.g., Local inference support]
    - [Feature 3: e.g., Custom API endpoint]

    Supported models (examples):
    - [Model 1: e.g., mistral-7b]
    - [Model 2: e.g., llama-2-70b]
    - [Model 3: e.g., custom models]

    Configuration example:
        >>> config = LLMConfig(
        ...     framework="custom",  # Your framework identifier
        ...     model="your-model-name",
        ...     temperature=0.7,
        ...     max_tokens=2048,
        ...     api_key="your-api-key",  # Optional
        ...     api_base="https://your-api.com",  # Optional
        ... )
        >>> llm = LLM(config=config)
        >>> response = llm.forward("Hello!")

    Attributes:
        config: LLMConfig object
        [Add any additional attributes your implementation needs]
    """

    def __init__(self, config: LLMConfig) -> None:
        """Initialize your custom LLM.

        Args:
            config: LLMConfig object with model and parameters

        IMPLEMENTATION GUIDE:
        1. Call super().__init__(config) first (required)
        2. Initialize your API client/connection
        3. Set up any provider-specific configuration
        4. Store any necessary state in instance variables
        """
        # Required: Call parent constructor
        super().__init__(config)

        # TODO: Initialize your API client here
        # Example:
        # self.client = YourAPIClient(
        #     api_key=config.api_key or os.getenv("YOUR_API_KEY"),
        #     base_url=config.api_base,
        #     timeout=config.timeout,
        # )

        # TODO: Set up provider-specific configuration
        # Example:
        # self.client.set_retry_config(max_retries=config.max_retries)

        logger.debug(
            "Initialized custom LLM",
            model=config.model,
            api_base=config.api_base,
            # Add other relevant config info
        )

    def _forward_impl(self, prompt: str, **kwargs: Any) -> str:
        """Forward prompt to your LLM provider.

        IMPORTANT: This is the ONLY method you need to implement for basic functionality.
        DO NOT implement forward() - it's handled by BaseLLM with automatic logging.

        Args:
            prompt: Input prompt string
            **kwargs: Optional parameter overrides
                - temperature: Override config temperature
                - max_tokens: Override config max_tokens
                - [Add any custom parameters your API supports]

        Returns:
            str: Generated text response (just return the text, logging is automatic)

        Raises:
            Exception: Any exception from your API (will be logged automatically)

        IMPLEMENTATION GUIDE:
        1. Build request parameters from self.config and kwargs
        2. Call your API/service
        3. Extract and return the text response
        4. Let exceptions propagate (they will be logged automatically)
        5. DO NOT add logging code (it's automatic)
        6. DO NOT add try/except (error handling is automatic)

        EXAMPLE IMPLEMENTATION:
            # Build parameters
            request_params = {
                "model": self.config.model,
                "prompt": prompt,
                "temperature": kwargs.get("temperature", self.config.temperature),
                "max_tokens": kwargs.get("max_tokens", self.config.max_tokens),
            }

            # Call API
            response = self.client.complete(**request_params)

            # Extract and return text
            return response.text
        """
        # TODO: Implement your API call here
        # Remove the NotImplementedError and add your implementation

        raise NotImplementedError(
            "You must implement _forward_impl() in your custom LLM class.\n"
            "See the docstring and template comments above for guidance.\n"
            "\n"
            "Quick example:\n"
            "    request_params = {'model': self.config.model, 'prompt': prompt}\n"
            "    response = self.client.complete(**request_params)\n"
            "    return response.text"
        )

        # EXAMPLE IMPLEMENTATION (uncomment and modify):
        # # Build request parameters
        # request_params = {
        #     "model": self.config.model,
        #     "messages": [{"role": "user", "content": prompt}],
        #     "temperature": kwargs.get("temperature", self.config.temperature),
        #     "max_tokens": kwargs.get("max_tokens", self.config.max_tokens),
        #     "timeout": self.config.timeout,
        # }
        #
        # # Add optional parameters if configured
        # if self.config.top_p is not None:
        #     request_params["top_p"] = self.config.top_p
        # if self.config.frequency_penalty is not None:
        #     request_params["frequency_penalty"] = self.config.frequency_penalty
        # if self.config.presence_penalty is not None:
        #     request_params["presence_penalty"] = self.config.presence_penalty
        #
        # # Add API credentials if needed
        # if self.config.api_key:
        #     request_params["api_key"] = self.config.api_key
        #
        # # Merge additional parameters from config
        # request_params.update(self.config.additional_params)
        #
        # # Call your API
        # response = self.client.complete(**request_params)
        #
        # # Extract text from response
        # if hasattr(response, "text"):
        #     result = response.text
        # elif hasattr(response, "content"):
        #     result = response.content
        # else:
        #     result = str(response)
        #
        # # Handle empty responses
        # if not result:
        #     logger.warning("API returned empty response", model=self.config.model)
        #     return ""
        #
        # return result

    def _forward_stream_impl(self, prompt: str, **kwargs: Any) -> Generator[str, None, None]:
        """Stream responses from your LLM provider.

        IMPORTANT: This method is OPTIONAL if your provider doesn't support streaming.
        If not implemented, users will get a NotImplementedError when calling forward_stream().
        DO NOT implement forward_stream() - it's handled by BaseLLM with automatic logging.

        Args:
            prompt: Input prompt string
            **kwargs: Optional parameter overrides (same as _forward_impl)

        Yields:
            str: Individual tokens or chunks (just yield the text, metrics are automatic)

        Raises:
            Exception: Any exception from your API (will be logged automatically)
            NotImplementedError: If streaming is not supported by your provider

        IMPLEMENTATION GUIDE:
        1. Build request parameters (similar to _forward_impl)
        2. Call your streaming API endpoint
        3. Iterate over response chunks
        4. Yield each chunk's text content
        5. Let exceptions propagate (they will be logged automatically)
        6. DO NOT add logging code (it's automatic)
        7. DO NOT add try/except (error handling is automatic)
        8. Chunk metrics (count, size, timing) are tracked automatically

        EXAMPLE IMPLEMENTATION:
            # Build parameters with streaming enabled
            request_params = {
                "model": self.config.model,
                "prompt": prompt,
                "temperature": kwargs.get("temperature", self.config.temperature),
                "stream": True,
            }

            # Call streaming API
            for chunk in self.client.stream(**request_params):
                if chunk.text:
                    yield chunk.text
        """
        # TODO: Implement your streaming API call here
        # If your provider doesn't support streaming, you can leave this as NotImplementedError

        raise NotImplementedError(
            "Streaming is not implemented for this custom LLM.\n"
            "If your provider supports streaming, implement _forward_stream_impl().\n"
            "If not, users should use forward() instead of forward_stream().\n"
            "\n"
            "Quick example:\n"
            "    request_params = {'model': self.config.model, 'prompt': prompt, 'stream': True}\n"
            "    for chunk in self.client.stream(**request_params):\n"
            "        if chunk.text:\n"
            "            yield chunk.text"
        )

        # EXAMPLE IMPLEMENTATION (uncomment and modify):
        # # Build request parameters
        # request_params = {
        #     "model": self.config.model,
        #     "messages": [{"role": "user", "content": prompt}],
        #     "temperature": kwargs.get("temperature", self.config.temperature),
        #     "max_tokens": kwargs.get("max_tokens", self.config.max_tokens),
        #     "stream": True,  # Enable streaming
        # }
        #
        # # Add optional parameters
        # if self.config.top_p is not None:
        #     request_params["top_p"] = self.config.top_p
        #
        # if self.config.api_key:
        #     request_params["api_key"] = self.config.api_key
        #
        # # Call streaming API
        # for chunk in self.client.stream(**request_params):
        #     # Extract text from chunk
        #     if hasattr(chunk, "text") and chunk.text:
        #         yield chunk.text
        #     elif hasattr(chunk, "content") and chunk.content:
        #         yield chunk.content
        #     elif hasattr(chunk, "delta") and hasattr(chunk.delta, "content"):
        #         if chunk.delta.content:
        #             yield chunk.delta.content

    # OPTIONAL: Add helper methods for your implementation
    # Example:
    # def _build_request_params(self, prompt: str, **kwargs: Any) -> dict[str, Any]:
    #     """Build request parameters for API calls."""
    #     return {...}
    #
    # def _validate_config(self) -> None:
    #     """Validate configuration specific to your provider."""
    #     if not self.config.api_key:
    #         raise ValueError("API key is required for CustomLLM")


# ============================================================================
# REGISTRATION
# ============================================================================
# Register your implementation with a unique framework identifier.
# Users will use this identifier in their config files.
#
# Example config usage:
#   config = LLMConfig(framework="custom", model="your-model")
#
# IMPORTANT: Change "custom" to your provider name (lowercase, no spaces)
# Examples: "openrouter", "huggingface", "local", "azure", etc.
#
# Uncomment the line below after implementing your class:
# register_llm_framework("custom", CustomLLM)


# ============================================================================
# TESTING YOUR IMPLEMENTATION
# ============================================================================
# Once you've implemented your custom LLM, test it:
#
# from fluxibly.llm import LLM, LLMConfig
#
# # Create config
# config = LLMConfig(
#     framework="custom",  # Your framework identifier
#     model="your-model-name",
#     temperature=0.7,
#     api_key="your-api-key",
# )
#
# # Create LLM instance
# llm = LLM(config=config)
#
# # Test forward()
# response = llm.forward("Hello, how are you?")
# print(response)
#
# # Test forward_stream() (if implemented)
# for chunk in llm.forward_stream("Tell me a story"):
#     print(chunk, end="")
#
# All logging, metrics, and error handling happen automatically!


# ============================================================================
# INTEGRATION CHECKLIST
# ============================================================================
# Before using your custom LLM in production:
#
# [ ] Implemented _forward_impl() with your API call
# [ ] Implemented _forward_stream_impl() (or left as NotImplementedError)
# [ ] Registered framework with unique identifier
# [ ] Tested with real API calls
# [ ] Verified logging output (INFO, DEBUG, ERROR levels)
# [ ] Handled API-specific parameters in config.additional_params
# [ ] Documented supported models in class docstring
# [ ] Added configuration example in class docstring
# [ ] (Optional) Imported module in __init__.py for auto-registration
# [ ] (Optional) Added tests in tests/unit/test_llm.py


# ============================================================================
# COMMON PATTERNS AND TIPS
# ============================================================================

# TIP 1: Using environment variables for API keys
# Instead of requiring api_key in config, use environment variables:
#
#     import os
#     api_key = config.api_key or os.getenv("YOUR_API_KEY_ENV_VAR")

# TIP 2: Provider-specific parameters
# Use config.additional_params for provider-specific options:
#
#     config = LLMConfig(
#         framework="custom",
#         model="model-name",
#         additional_params={
#             "custom_param": "value",
#             "another_param": 123,
#         }
#     )
#     # Then in your implementation:
#     request_params.update(self.config.additional_params)

# TIP 3: Model name prefixes
# Some providers use prefixes for model names:
#
#     model_name = self.config.model
#     if not model_name.startswith("provider/"):
#         model_name = f"provider/{model_name}"

# TIP 4: Retry logic
# If your client doesn't support retries, implement simple retry logic:
#
#     from time import sleep
#     for attempt in range(self.config.max_retries):
#         try:
#             return self.client.complete(...)
#         except TemporaryError as e:
#             if attempt == self.config.max_retries - 1:
#                 raise
#             sleep(2 ** attempt)  # Exponential backoff

# TIP 5: Response validation
# Always check for empty responses:
#
#     if not result or not result.strip():
#         logger.warning("Empty response", model=self.config.model)
#         return ""

# TIP 6: Token counting (optional)
# If you want to track token usage, add it to logs:
#
#     logger.info(
#         "Token usage",
#         input_tokens=response.usage.input_tokens,
#         output_tokens=response.usage.output_tokens,
#     )


# ============================================================================
# EXAMPLE: Real-world Custom LLM Implementation
# ============================================================================
# Here's a complete example using a hypothetical "OpenRouter" provider:

"""
from collections.abc import Generator
from typing import Any
import os

import openrouter  # Hypothetical client library
from fluxibly.llm.base import BaseLLM, LLMConfig, register_llm_framework


class OpenRouterLLM(BaseLLM):
    \"\"\"OpenRouter LLM implementation.

    Provides access to 100+ models through OpenRouter API.

    Supported models:
    - openai/gpt-4o
    - anthropic/claude-3-5-sonnet
    - mistralai/mistral-large
    - And many more...

    Configuration:
        >>> config = LLMConfig(
        ...     framework="openrouter",
        ...     model="anthropic/claude-3-5-sonnet",
        ...     temperature=0.7,
        ...     max_tokens=2048,
        ... )
        >>> llm = LLM(config=config)
    \"\"\"

    def __init__(self, config: LLMConfig) -> None:
        super().__init__(config)

        # Initialize client
        api_key = config.api_key or os.getenv("OPENROUTER_API_KEY")
        self.client = openrouter.Client(
            api_key=api_key,
            base_url=config.api_base,
            timeout=config.timeout,
            max_retries=config.max_retries,
        )

    def _forward_impl(self, prompt: str, **kwargs: Any) -> str:
        # Build parameters
        params = {
            "model": self.config.model,
            "messages": [{"role": "user", "content": prompt}],
            "temperature": kwargs.get("temperature", self.config.temperature),
            "max_tokens": kwargs.get("max_tokens", self.config.max_tokens),
        }

        # Add optional parameters
        if self.config.top_p is not None:
            params["top_p"] = self.config.top_p

        params.update(self.config.additional_params)

        # Call API
        response = self.client.chat.complete(**params)
        return response.choices[0].message.content or ""

    def _forward_stream_impl(self, prompt: str, **kwargs: Any) -> Generator[str, None, None]:
        # Build parameters with streaming
        params = {
            "model": self.config.model,
            "messages": [{"role": "user", "content": prompt}],
            "temperature": kwargs.get("temperature", self.config.temperature),
            "max_tokens": kwargs.get("max_tokens", self.config.max_tokens),
            "stream": True,
        }

        # Stream response
        for chunk in self.client.chat.complete(**params):
            if chunk.choices[0].delta.content:
                yield chunk.choices[0].delta.content


# Register implementation
register_llm_framework("openrouter", OpenRouterLLM)
"""
