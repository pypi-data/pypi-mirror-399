"""LLM module for Fluxibly framework.

This module provides pluggable LLM implementations supporting multiple frameworks.

Public API:
- LLM: Factory function for creating LLM instances
- BaseLLM: Base class for custom implementations
- LLMConfig: Configuration model
- register_llm_framework: Register custom frameworks

Available frameworks:
- langchain: LangChain-based (OpenAI, Anthropic via LangChain)
- litellm: LiteLLM-based (100+ providers unified)
"""

# Import implementations to trigger registration
import fluxibly.llm.langchain_llm  # noqa: F401
import fluxibly.llm.litellm_llm  # noqa: F401
from fluxibly.llm.base import LLM, BaseLLM, LLMConfig, register_llm_framework

__all__ = [
    "LLM",
    "BaseLLM",
    "LLMConfig",
    "register_llm_framework",
]
