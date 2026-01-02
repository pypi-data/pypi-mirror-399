# Custom LLM Integration Guide

This guide explains how to integrate your own LLM provider or framework into Fluxibly using the custom LLM template.

## Overview

Fluxibly provides a pluggable architecture that allows you to integrate any LLM provider by:
1. Implementing two simple methods (`_forward_impl` and `_forward_stream_impl`)
2. Registering your implementation with a unique identifier
3. Using it like any built-in framework (LangChain, LiteLLM)

**What you get for free:**
- ✅ Comprehensive automatic logging (request/response, timing, errors)
- ✅ Performance metrics tracking (elapsed time, token counts, chunk statistics)
- ✅ Structured error handling and logging
- ✅ Debug-level detailed information
- ✅ Configuration management via YAML files

## Quick Start

### 1. Copy the Template

```bash
# Navigate to your project
cd fluxibly/llm/

# Copy the template to a new file
cp custom_llm.py my_provider_llm.py
```

### 2. Implement Your Provider

Edit `my_provider_llm.py`:

```python
from collections.abc import Generator
from typing import Any
import os

from fluxibly.llm.base import BaseLLM, LLMConfig, register_llm_framework


class MyProviderLLM(BaseLLM):
    """My custom LLM implementation."""

    def __init__(self, config: LLMConfig) -> None:
        super().__init__(config)

        # Initialize your API client
        api_key = config.api_key or os.getenv("MY_API_KEY")
        self.client = MyAPIClient(
            api_key=api_key,
            base_url=config.api_base,
            timeout=config.timeout,
        )

    def _forward_impl(self, prompt: str, **kwargs: Any) -> str:
        """Call your API and return the response text."""
        # Build request
        params = {
            "model": self.config.model,
            "prompt": prompt,
            "temperature": kwargs.get("temperature", self.config.temperature),
            "max_tokens": kwargs.get("max_tokens", self.config.max_tokens),
        }

        # Call API
        response = self.client.complete(**params)

        # Return text
        return response.text

    def _forward_stream_impl(self, prompt: str, **kwargs: Any) -> Generator[str, None, None]:
        """Stream responses from your API."""
        # Build request with streaming
        params = {
            "model": self.config.model,
            "prompt": prompt,
            "temperature": kwargs.get("temperature", self.config.temperature),
            "stream": True,
        }

        # Stream response
        for chunk in self.client.stream(**params):
            if chunk.text:
                yield chunk.text


# Register your implementation
register_llm_framework("myprovider", MyProviderLLM)
```

### 3. Enable Auto-Registration

Add your module to `fluxibly/llm/__init__.py`:

```python
# Import implementations to trigger registration
import fluxibly.llm.langchain_llm  # noqa: F401
import fluxibly.llm.litellm_llm  # noqa: F401
import fluxibly.llm.my_provider_llm  # noqa: F401  ← Add this line
```

### 4. Use Your Implementation

```python
from fluxibly.llm import LLM, LLMConfig

# Configure your LLM
config = LLMConfig(
    framework="myprovider",  # Your framework identifier
    model="your-model-name",
    temperature=0.7,
    api_key="your-api-key",
)

# Create instance
llm = LLM(config=config)

# Use it - logging happens automatically!
response = llm.forward("Hello, world!")
print(response)
```

## Template Structure

The [custom_llm.py](../fluxibly/llm/custom_llm.py) template provides:

```
CustomLLM
├── __init__()          # Initialize your client/connection
├── _forward_impl()     # Required: Implement synchronous calls
├── _forward_stream_impl()  # Optional: Implement streaming
└── [helper methods]    # Optional: Add provider-specific logic
```

### Required Methods

#### `_forward_impl(prompt: str, **kwargs) -> str`

**Purpose:** Make a synchronous call to your LLM and return the text response.

**What to implement:**
1. Build request parameters from `self.config` and `kwargs`
2. Call your API/service
3. Extract and return the text response
4. Let exceptions propagate (they'll be logged automatically)

**What NOT to do:**
- ❌ Don't add logging (it's automatic)
- ❌ Don't add try/except (error handling is automatic)
- ❌ Don't implement `forward()` (use `_forward_impl()` instead)

**Example:**
```python
def _forward_impl(self, prompt: str, **kwargs: Any) -> str:
    # Build parameters
    params = {
        "model": self.config.model,
        "prompt": prompt,
        "temperature": kwargs.get("temperature", self.config.temperature),
        "max_tokens": kwargs.get("max_tokens", self.config.max_tokens),
    }

    # Call API
    response = self.client.complete(**params)

    # Return text
    return response.text
```

### Optional Methods

#### `_forward_stream_impl(prompt: str, **kwargs) -> Generator[str, None, None]`

**Purpose:** Stream responses from your LLM token by token.

**What to implement:**
1. Build request parameters with streaming enabled
2. Call your streaming API
3. Yield each chunk's text content
4. Let exceptions propagate

**If your provider doesn't support streaming:**
- Leave the `NotImplementedError` - users will be told to use `forward()` instead

**Example:**
```python
def _forward_stream_impl(self, prompt: str, **kwargs: Any) -> Generator[str, None, None]:
    # Build parameters
    params = {
        "model": self.config.model,
        "prompt": prompt,
        "temperature": kwargs.get("temperature", self.config.temperature),
        "stream": True,
    }

    # Stream chunks
    for chunk in self.client.stream(**params):
        if chunk.text:
            yield chunk.text
```

## Configuration

### Using LLMConfig

All configuration is handled through `LLMConfig`:

```python
config = LLMConfig(
    # Required
    framework="myprovider",      # Your framework identifier
    model="your-model-name",     # Model identifier

    # Common parameters
    temperature=0.7,             # Sampling temperature (0.0-2.0)
    max_tokens=2048,             # Maximum tokens to generate
    top_p=0.9,                   # Nucleus sampling (0.0-1.0)
    frequency_penalty=0.0,       # Reduce repetition (-2.0 to 2.0)
    presence_penalty=0.0,        # Encourage diversity (-2.0 to 2.0)

    # API configuration
    api_key="your-api-key",      # API key (or use env var)
    api_base="https://api.com",  # Custom API endpoint
    timeout=60,                  # Request timeout (seconds)
    max_retries=3,               # Maximum retry attempts

    # Provider-specific parameters
    additional_params={
        "custom_param": "value",
        "another_param": 123,
    }
)
```

### Using YAML Configuration

Add to `config/framework.yaml`:

```yaml
llm:
  framework: "myprovider"
  model: "your-model-name"
  temperature: 0.7
  max_tokens: 2048
  api_key: null  # Use environment variable
  api_base: "https://your-api.com"

  # Provider-specific parameters
  additional_params:
    custom_param: "value"
    another_param: 123
```

Then load from config:

```python
import yaml
from fluxibly.llm import LLM, LLMConfig

# Load config
with open("config/framework.yaml") as f:
    config_data = yaml.safe_load(f)

# Create LLM
config = LLMConfig(**config_data["llm"])
llm = LLM(config=config)
```

## Common Patterns

### Pattern 1: Environment Variables for API Keys

```python
import os

def __init__(self, config: LLMConfig) -> None:
    super().__init__(config)

    # Try config first, then environment variable
    api_key = config.api_key or os.getenv("MY_PROVIDER_API_KEY")

    if not api_key:
        raise ValueError("API key required: set api_key in config or MY_PROVIDER_API_KEY env var")

    self.client = MyAPIClient(api_key=api_key)
```

### Pattern 2: Model Name Prefixes

```python
def _forward_impl(self, prompt: str, **kwargs: Any) -> str:
    # Add provider prefix if not present
    model_name = self.config.model
    if not model_name.startswith("provider/"):
        model_name = f"provider/{model_name}"

    params = {"model": model_name, "prompt": prompt}
    response = self.client.complete(**params)
    return response.text
```

### Pattern 3: Provider-Specific Parameters

```python
def _forward_impl(self, prompt: str, **kwargs: Any) -> str:
    # Build base parameters
    params = {
        "model": self.config.model,
        "prompt": prompt,
        "temperature": kwargs.get("temperature", self.config.temperature),
    }

    # Add standard optional parameters
    if self.config.max_tokens:
        params["max_tokens"] = self.config.max_tokens
    if self.config.top_p is not None:
        params["top_p"] = self.config.top_p

    # Merge provider-specific parameters from config
    params.update(self.config.additional_params)

    response = self.client.complete(**params)
    return response.text
```

### Pattern 4: Response Validation

```python
def _forward_impl(self, prompt: str, **kwargs: Any) -> str:
    response = self.client.complete(...)

    # Extract text
    text = response.text if hasattr(response, "text") else str(response)

    # Validate non-empty
    if not text or not text.strip():
        logger.warning("Empty response from API", model=self.config.model)
        return ""

    return text
```

### Pattern 5: Custom Retry Logic

```python
from time import sleep

def _forward_impl(self, prompt: str, **kwargs: Any) -> str:
    last_error = None

    for attempt in range(self.config.max_retries):
        try:
            response = self.client.complete(...)
            return response.text
        except TemporaryAPIError as e:
            last_error = e
            if attempt < self.config.max_retries - 1:
                # Exponential backoff
                sleep(2 ** attempt)
            continue

    # Re-raise last error after all retries
    raise last_error
```

## Automatic Logging

Your custom LLM gets comprehensive logging automatically:

### What Gets Logged

**Request Start (INFO):**
```
LLM request started | name=MyProviderLLM, framework=myprovider, model=my-model, prompt_length=42
```

**Request Complete (INFO):**
```
LLM request completed | elapsed_time=1.23s, prompt_length=42, response_length=128
```

**Request Details (DEBUG):**
```
LLM request details | prompt_preview="What is...", response_preview="The answer...", elapsed_time=1.234
```

**Request Failed (ERROR):**
```
LLM request failed | elapsed_time=0.50s, error_type=APIError, error_message="Rate limit exceeded"
```

### Streaming Logs

**Streaming Start (INFO):**
```
LLM streaming request started | name=MyProviderLLM, framework=myprovider, prompt_length=24
```

**Streaming Complete (INFO):**
```
LLM streaming completed | elapsed_time=3.45s, total_chunks=120, total_length=480
```

**Streaming Details (DEBUG):**
```
LLM streaming details | total_chunks=120, total_length=480, avg_chunk_size=4.0
```

## Testing Your Implementation

### Basic Test

```python
from fluxibly.llm import LLM, LLMConfig

# Create config
config = LLMConfig(
    framework="myprovider",
    model="test-model",
    temperature=0.7,
)

# Create LLM
llm = LLM(config=config)

# Test forward
print("Testing forward()...")
response = llm.forward("What is 2+2?")
print(f"Response: {response}")

# Test streaming
print("\nTesting forward_stream()...")
for chunk in llm.forward_stream("Count to 5"):
    print(chunk, end="")
print()
```

### Unit Tests

Create `tests/unit/test_myprovider_llm.py`:

```python
import pytest
from unittest.mock import Mock, patch

from fluxibly.llm import LLM, LLMConfig


@pytest.fixture
def config():
    return LLMConfig(
        framework="myprovider",
        model="test-model",
        temperature=0.7,
        max_tokens=100,
    )


def test_forward(config):
    """Test basic forward call."""
    llm = LLM(config=config)

    with patch.object(llm, '_forward_impl', return_value="test response"):
        response = llm.forward("test prompt")
        assert response == "test response"


def test_forward_stream(config):
    """Test streaming call."""
    llm = LLM(config=config)

    def mock_stream(*args, **kwargs):
        yield "chunk1"
        yield "chunk2"

    with patch.object(llm, '_forward_stream_impl', side_effect=mock_stream):
        chunks = list(llm.forward_stream("test prompt"))
        assert chunks == ["chunk1", "chunk2"]


def test_error_handling(config):
    """Test error logging."""
    llm = LLM(config=config)

    with patch.object(llm, '_forward_impl', side_effect=ValueError("API error")):
        with pytest.raises(ValueError, match="API error"):
            llm.forward("test prompt")
```

## Integration Checklist

Before deploying your custom LLM:

- [ ] **Implementation**
  - [ ] Implemented `_forward_impl()` with API call
  - [ ] Implemented `_forward_stream_impl()` or left as NotImplementedError
  - [ ] Registered framework with unique identifier
  - [ ] Added import in `__init__.py` for auto-registration

- [ ] **Configuration**
  - [ ] Handles API keys from config or environment
  - [ ] Supports all relevant LLMConfig parameters
  - [ ] Documents provider-specific parameters
  - [ ] Validates required configuration

- [ ] **Testing**
  - [ ] Tested with real API calls
  - [ ] Verified logging output (INFO, DEBUG, ERROR)
  - [ ] Tested error scenarios (rate limits, timeouts, etc.)
  - [ ] Added unit tests
  - [ ] Tested with both forward() and forward_stream()

- [ ] **Documentation**
  - [ ] Updated class docstring with supported models
  - [ ] Added configuration example
  - [ ] Documented any provider-specific quirks
  - [ ] Added usage example in comments

- [ ] **Code Quality**
  - [ ] Passes ruff formatting
  - [ ] Passes ruff linting
  - [ ] Passes pyright type checking
  - [ ] Follows existing code patterns

## Real-World Examples

### Example 1: OpenRouter Integration

```python
from collections.abc import Generator
from typing import Any
import os

import requests
from fluxibly.llm.base import BaseLLM, LLMConfig, register_llm_framework


class OpenRouterLLM(BaseLLM):
    """OpenRouter LLM implementation.

    Provides access to 100+ models through OpenRouter API.

    Configuration:
        config = LLMConfig(
            framework="openrouter",
            model="anthropic/claude-3-5-sonnet",
            api_key="your-key",
        )
    """

    def __init__(self, config: LLMConfig) -> None:
        super().__init__(config)

        self.api_key = config.api_key or os.getenv("OPENROUTER_API_KEY")
        self.base_url = config.api_base or "https://openrouter.ai/api/v1"

        if not self.api_key:
            raise ValueError("OpenRouter API key required")

    def _forward_impl(self, prompt: str, **kwargs: Any) -> str:
        url = f"{self.base_url}/chat/completions"

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

        data = {
            "model": self.config.model,
            "messages": [{"role": "user", "content": prompt}],
            "temperature": kwargs.get("temperature", self.config.temperature),
            "max_tokens": kwargs.get("max_tokens", self.config.max_tokens),
        }

        response = requests.post(url, headers=headers, json=data, timeout=self.config.timeout)
        response.raise_for_status()

        return response.json()["choices"][0]["message"]["content"]

    def _forward_stream_impl(self, prompt: str, **kwargs: Any) -> Generator[str, None, None]:
        url = f"{self.base_url}/chat/completions"

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

        data = {
            "model": self.config.model,
            "messages": [{"role": "user", "content": prompt}],
            "temperature": kwargs.get("temperature", self.config.temperature),
            "max_tokens": kwargs.get("max_tokens", self.config.max_tokens),
            "stream": True,
        }

        response = requests.post(url, headers=headers, json=data, stream=True, timeout=self.config.timeout)
        response.raise_for_status()

        for line in response.iter_lines():
            if line and line.startswith(b"data: "):
                chunk_data = json.loads(line[6:])
                if "choices" in chunk_data and chunk_data["choices"]:
                    content = chunk_data["choices"][0]["delta"].get("content")
                    if content:
                        yield content


register_llm_framework("openrouter", OpenRouterLLM)
```

### Example 2: Local Ollama Integration

```python
from collections.abc import Generator
from typing import Any

import requests
from fluxibly.llm.base import BaseLLM, LLMConfig, register_llm_framework


class OllamaLLM(BaseLLM):
    """Ollama local LLM implementation.

    Run LLMs locally with Ollama.

    Configuration:
        config = LLMConfig(
            framework="ollama",
            model="llama2",
            api_base="http://localhost:11434",  # Default Ollama URL
        )
    """

    def __init__(self, config: LLMConfig) -> None:
        super().__init__(config)
        self.base_url = config.api_base or "http://localhost:11434"

    def _forward_impl(self, prompt: str, **kwargs: Any) -> str:
        url = f"{self.base_url}/api/generate"

        data = {
            "model": self.config.model,
            "prompt": prompt,
            "temperature": kwargs.get("temperature", self.config.temperature),
            "stream": False,
        }

        response = requests.post(url, json=data, timeout=self.config.timeout)
        response.raise_for_status()

        return response.json()["response"]

    def _forward_stream_impl(self, prompt: str, **kwargs: Any) -> Generator[str, None, None]:
        url = f"{self.base_url}/api/generate"

        data = {
            "model": self.config.model,
            "prompt": prompt,
            "temperature": kwargs.get("temperature", self.config.temperature),
            "stream": True,
        }

        response = requests.post(url, json=data, stream=True, timeout=self.config.timeout)
        response.raise_for_status()

        for line in response.iter_lines():
            if line:
                chunk = json.loads(line)
                if "response" in chunk:
                    yield chunk["response"]


register_llm_framework("ollama", OllamaLLM)
```

## Troubleshooting

### Issue: "Framework not registered"

**Problem:** `ValueError: LLM framework 'myprovider' not registered`

**Solutions:**
1. Check that you called `register_llm_framework("myprovider", MyProviderLLM)`
2. Import your module in `__init__.py` for auto-registration
3. Verify the framework identifier matches between registration and config

### Issue: "NotImplementedError"

**Problem:** `NotImplementedError: Subclass must implement _forward_impl()`

**Solutions:**
1. Make sure you implemented `_forward_impl()` (not `forward()`)
2. Check for typos in method name
3. Verify you're inheriting from `BaseLLM`

### Issue: Logs not appearing

**Problem:** No logs from your LLM calls

**Solutions:**
1. Check log level is set to INFO or DEBUG
2. Verify logger configuration in your application
3. Make sure you're calling `forward()` not `_forward_impl()` directly

### Issue: Type checking errors

**Problem:** Pyright complains about method signatures

**Solutions:**
1. Match exact signature from `BaseLLM`:
   - `_forward_impl(self, prompt: str, **kwargs: Any) -> str`
   - `_forward_stream_impl(self, prompt: str, **kwargs: Any) -> Generator[str, None, None]`
2. Import types: `from collections.abc import Generator`, `from typing import Any`

## See Also

- [Custom LLM Template](../fluxibly/llm/custom_llm.py) - Template file with detailed comments
- [LLM Logging Documentation](./llm_logging.md) - Understanding automatic logging
- [LangChain Implementation](../fluxibly/llm/langchain_llm.py) - Example implementation
- [LiteLLM Implementation](../fluxibly/llm/litellm_llm.py) - Example implementation
- [CLAUDE.md](../CLAUDE.md) - Development guidelines
