# Custom LLM Quick Start

**5-minute guide to integrating your own LLM provider into Fluxibly.**

## The Basics

You only need to implement **2 methods**:
1. `_forward_impl()` - Make an API call, return text
2. `_forward_stream_impl()` - Stream API call, yield chunks (optional)

Everything else (logging, metrics, errors) is automatic! ✨

## Minimal Example

```python
from collections.abc import Generator
from typing import Any
from fluxibly.llm.base import BaseLLM, LLMConfig, register_llm_framework


class MyLLM(BaseLLM):
    def __init__(self, config: LLMConfig) -> None:
        super().__init__(config)
        self.client = MyAPIClient(api_key=config.api_key)

    def _forward_impl(self, prompt: str, **kwargs: Any) -> str:
        response = self.client.complete(
            model=self.config.model,
            prompt=prompt,
            temperature=kwargs.get("temperature", self.config.temperature),
        )
        return response.text

    def _forward_stream_impl(self, prompt: str, **kwargs: Any) -> Generator[str, None, None]:
        for chunk in self.client.stream(model=self.config.model, prompt=prompt):
            yield chunk.text


register_llm_framework("myframework", MyLLM)
```

That's it! You now have:
- ✅ Automatic logging
- ✅ Performance metrics
- ✅ Error handling
- ✅ Configuration management

## Usage

```python
from fluxibly.llm import LLM, LLMConfig

config = LLMConfig(framework="myframework", model="my-model")
llm = LLM(config=config)

response = llm.forward("Hello!")  # Fully logged automatically
print(response)
```

## Key Rules

### ✅ DO
- Implement `_forward_impl()` (with underscore)
- Return plain strings
- Let exceptions propagate
- Use `self.config` for parameters
- Call `super().__init__(config)` first

### ❌ DON'T
- Don't implement `forward()` (without underscore)
- Don't add logging code
- Don't add try/except blocks
- Don't catch exceptions (they're logged automatically)

## Common Patterns

### Pattern: Environment Variables
```python
def __init__(self, config: LLMConfig) -> None:
    super().__init__(config)
    import os
    api_key = config.api_key or os.getenv("MY_API_KEY")
    self.client = MyClient(api_key=api_key)
```

### Pattern: Optional Parameters
```python
def _forward_impl(self, prompt: str, **kwargs: Any) -> str:
    params = {
        "model": self.config.model,
        "prompt": prompt,
        "temperature": kwargs.get("temperature", self.config.temperature),
    }

    if self.config.max_tokens:
        params["max_tokens"] = self.config.max_tokens

    params.update(self.config.additional_params)  # Provider-specific

    return self.client.complete(**params).text
```

### Pattern: Streaming Not Supported
```python
def _forward_stream_impl(self, prompt: str, **kwargs: Any) -> Generator[str, None, None]:
    # Just leave the NotImplementedError
    raise NotImplementedError("Streaming not supported")
    yield  # For type checker
```

## Full Template

See [custom_llm.py](../fluxibly/llm/custom_llm.py) for:
- Detailed implementation guide
- Complete docstrings
- Common patterns
- Real-world examples
- Troubleshooting tips

## Next Steps

1. **Copy template**: `cp fluxibly/llm/custom_llm.py fluxibly/llm/myprovider_llm.py`
2. **Implement methods**: Fill in `_forward_impl()` and optionally `_forward_stream_impl()`
3. **Register**: Add `register_llm_framework("myprovider", MyProviderLLM)` at bottom
4. **Auto-register**: Import in `fluxibly/llm/__init__.py`
5. **Test**: Run `llm.forward("test")` and check logs

## Need Help?

- 📖 [Full Guide](./custom_llm_guide.md) - Comprehensive integration guide
- 📝 [Template](../fluxibly/llm/custom_llm.py) - Detailed template with comments
- 📊 [Logging Docs](./llm_logging.md) - Understanding automatic logging
- 💻 [Examples](../fluxibly/llm/) - See langchain_llm.py and litellm_llm.py

## What You Get Automatically

### Logging
```
INFO: LLM request started | framework=myframework, model=my-model, prompt_length=42
INFO: LLM request completed | elapsed_time=1.23s, response_length=128
DEBUG: LLM request details | prompt_preview="Hello...", response_preview="Hi there..."
ERROR: LLM request failed | error_type=APIError, error_message="Rate limit"
```

### Performance Metrics
- Request/response timing
- Token/character counts
- Streaming chunk statistics
- Average chunk size

### Error Handling
- Automatic exception catching
- Structured error logging
- Error type and message capture
- Elapsed time on failure

### Configuration
- YAML-based config files
- Environment variable support
- Parameter override via kwargs
- Provider-specific parameters

---

**That's all you need to know! Start with the minimal example above and expand as needed.** 🚀
