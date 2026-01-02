"""Demo script to showcase comprehensive LLM logging mechanism.

This script demonstrates how the logging mechanism in BaseLLM automatically
captures logs from any framework implementation (LangChain, LiteLLM, or custom).

Run with different log levels to see different output:
    uv run python examples/logging_demo.py
"""

import sys

from loguru import logger

from fluxibly.llm import LLM, BaseLLM, LLMConfig, register_llm_framework

# Configure logger to show structured logs
logger.remove()
logger.add(
    sys.stderr,
    format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan> | <level>{message}</level> | {extra}",
    level="DEBUG",
)


def demo_langchain():
    """Demo LangChain implementation with automatic logging."""
    logger.info("=" * 80)
    logger.info("DEMO: LangChain Framework Logging")
    logger.info("=" * 80)

    # Create LLM with LangChain framework (requires OPENAI_API_KEY env var)
    config = LLMConfig(framework="langchain", model="gpt-4o-mini", temperature=0.7, max_tokens=100)

    llm = LLM(config=config)

    # All these calls will be automatically logged by BaseLLM
    try:
        logger.info("Calling forward() - logs will be captured automatically")
        response = llm.forward("What is 2+2? Answer briefly.")
        logger.info(f"Response received: {response[:50]}...")
    except Exception:
        logger.exception("LangChain call failed (may need API key)")

    print()


def demo_litellm():
    """Demo LiteLLM implementation with automatic logging."""
    logger.info("=" * 80)
    logger.info("DEMO: LiteLLM Framework Logging")
    logger.info("=" * 80)

    # Create LLM with LiteLLM framework (requires OPENAI_API_KEY env var)
    config = LLMConfig(framework="litellm", model="gpt-4o-mini", temperature=0.7, max_tokens=100)

    llm = LLM(config=config)

    # All these calls will be automatically logged by BaseLLM
    try:
        logger.info("Calling forward() - logs will be captured automatically")
        response = llm.forward("What is the capital of France? Answer briefly.")
        logger.info(f"Response received: {response[:50]}...")
    except Exception:
        logger.exception("LiteLLM call failed (may need API key)")

    print()


def demo_custom_framework():
    """Demo custom framework implementation with automatic logging."""
    logger.info("=" * 80)
    logger.info("DEMO: Custom Framework Logging")
    logger.info("=" * 80)

    # Create a simple custom LLM implementation
    class CustomLLM(BaseLLM):
        """Custom LLM that returns mock responses."""

        def _forward_impl(self, prompt: str, **kwargs):
            """Mock implementation."""
            import time

            # Simulate processing time
            time.sleep(0.5)
            return f"Mock response to: {prompt[:30]}..."

        def _forward_stream_impl(self, prompt: str, **kwargs):
            """Mock streaming implementation."""
            import time

            words = ["Mock", "streaming", "response", "to", "your", "prompt"]
            for word in words:
                time.sleep(0.1)
                yield word + " "

    # Register custom framework
    register_llm_framework("custom", CustomLLM)

    # Create LLM with custom framework
    config = LLMConfig(framework="custom", model="mock-model-v1")

    llm = LLM(config=config)

    # All these calls will be automatically logged by BaseLLM
    logger.info("Calling forward() - logs will be captured automatically")
    response = llm.forward("This is a test prompt for custom framework")
    logger.info(f"Response received: {response}")

    print()

    logger.info("Calling forward_stream() - streaming logs will be captured automatically")
    chunks = []
    for chunk in llm.forward_stream("This is a streaming test"):
        chunks.append(chunk)

    logger.info(f"Streaming response: {''.join(chunks)}")

    print()


def demo_error_logging():
    """Demo error logging in custom framework."""
    logger.info("=" * 80)
    logger.info("DEMO: Error Logging")
    logger.info("=" * 80)

    # Create a custom LLM that raises an error
    class ErrorLLM(BaseLLM):
        """Custom LLM that simulates errors."""

        def _forward_impl(self, prompt: str, **kwargs):
            """Implementation that raises an error."""
            import time

            # Simulate some processing before error
            time.sleep(0.2)
            raise ValueError("Simulated API error for demonstration")

        def _forward_stream_impl(self, prompt: str, **kwargs):
            """Implementation that raises error during streaming."""
            yield "Starting"
            yield "stream"
            raise ConnectionError("Simulated connection error during streaming")

    # Register error framework
    register_llm_framework("error", ErrorLLM)

    # Test error logging in forward()
    config = LLMConfig(framework="error", model="error-model")
    llm = LLM(config=config)

    logger.info("Calling forward() that will fail - error logs will be captured")
    try:
        llm.forward("This will fail")
    except ValueError:
        logger.info("Error was caught and logged by BaseLLM")

    print()

    # Test error logging in forward_stream()
    logger.info("Calling forward_stream() that will fail - error logs will be captured")
    try:
        for _chunk in llm.forward_stream("This will fail during streaming"):
            pass
    except ConnectionError:
        logger.info("Streaming error was caught and logged by BaseLLM")

    print()


if __name__ == "__main__":
    logger.info("Starting LLM Logging Demonstration")
    logger.info("This demonstrates comprehensive logging that works for ANY framework implementation")
    print()

    # Demo custom framework (no API key needed)
    demo_custom_framework()

    # Demo error logging (no API key needed)
    demo_error_logging()

    # Demo real frameworks (these require API keys)
    logger.info("=" * 80)
    logger.info("To test real frameworks (LangChain/LiteLLM), set OPENAI_API_KEY env var and uncomment below:")
    logger.info("=" * 80)

    # Uncomment these if you have API keys configured:
    # demo_langchain()
    # demo_litellm()

    logger.info("=" * 80)
    logger.info("Demonstration Complete!")
    logger.info("Key features demonstrated:")
    logger.info("1. Automatic logging of all LLM calls (forward and forward_stream)")
    logger.info("2. Performance metrics (elapsed time, token counts)")
    logger.info("3. Request/response details at debug level")
    logger.info("4. Error logging with detailed context")
    logger.info("5. Works for ANY framework (LangChain, LiteLLM, Custom)")
    logger.info("=" * 80)
