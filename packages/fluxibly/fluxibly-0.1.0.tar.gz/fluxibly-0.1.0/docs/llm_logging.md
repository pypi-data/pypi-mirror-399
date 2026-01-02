# LLM Comprehensive Logging

The Fluxibly framework provides comprehensive, automatic logging for all LLM operations through the `BaseLLM` class. This logging mechanism works seamlessly with any framework implementation (LangChain, LiteLLM, or custom frameworks).

## Features

The logging system automatically captures:

1. **Request Information**
   - Framework name (e.g., LangChain, LiteLLM, Custom)
   - Model identifier
   - Prompt length
   - Parameter overrides (temperature, max_tokens, etc.)

2. **Performance Metrics**
   - Elapsed time for each request
   - Response length (tokens/characters)
   - Streaming metrics (chunk count, total length, average chunk size)

3. **Detailed Debug Information**
   - Prompt preview (first 100 characters)
   - Response preview (first 100 characters)
   - Full timing information

4. **Error Tracking**
   - Error type and message
   - Elapsed time before failure
   - Context information (prompt length, chunks received)

## How It Works

The logging mechanism is built into `BaseLLM` using the **Template Method Pattern**:

```
┌─────────────────────────────────────────────────────┐
│                     BaseLLM                         │
│                                                     │
│  forward(prompt, **kwargs)                          │
│    ├── Log request started                          │
│    ├── Start timer                                  │
│    ├── Call _forward_impl() ← implemented by subclass│
│    ├── Calculate metrics                            │
│    ├── Log success/failure                          │
│    └── Return result                                │
│                                                     │
│  _forward_impl(prompt, **kwargs) ← OVERRIDE THIS   │
│    └── NotImplementedError                          │
└─────────────────────────────────────────────────────┘
                        │
                        │ inherits
                        ▼
        ┌───────────────────────────────┐
        │     LangChainLLM/LiteLLM      │
        │   /CustomFrameworkLLM         │
        │                               │
        │  _forward_impl()              │
        │    └── actual implementation  │
        └───────────────────────────────┘
```

### For Framework Developers

When creating a custom framework, you **MUST** implement:
- `_forward_impl()` instead of `forward()`
- `_forward_stream_impl()` instead of `forward_stream()`

The base class handles all logging automatically.

### For Framework Users

Simply use `forward()` and `forward_stream()` as normal - all logging happens automatically:

```python
from fluxibly.llm import LLM, LLMConfig

# Create any LLM (logging works automatically)
config = LLMConfig(framework="langchain", model="gpt-4o")
llm = LLM(config=config)

# All calls are logged automatically
response = llm.forward("What is AI?")  # Logged: request, timing, response length
```

## Log Levels

### INFO Level
Logs high-level operation information:
```
LLM request started | prompt_length=42, kwargs={}
LLM request completed | elapsed_time=0.51s, response_length=51
LLM streaming request started | prompt_length=24, kwargs={}
LLM streaming completed | total_chunks=6, total_length=39
```

### DEBUG Level
Logs detailed information including previews:
```
LLM request details | prompt_preview="What is AI?...", response_preview="AI is...", elapsed_time=0.51
LLM streaming details | total_chunks=6, avg_chunk_size=6.5
```

### ERROR Level
Logs failures with context:
```
LLM request failed | elapsed_time=0.20s, error_type=ValueError, error_message="API error"
LLM streaming failed | chunks_received=2, error_type=ConnectionError
```

## Configuration

### Logger Binding
Each LLM instance gets a bound logger with context:

```python
# In BaseLLM.__init__()
self.logger = loguru.logger.bind(
    name=self.__class__.__name__,  # e.g., "LangChainLLM"
    framework=config.framework,     # e.g., "langchain"
    model=config.model,             # e.g., "gpt-4o"
)
```

This ensures all logs include:
- Implementation class name
- Framework identifier
- Model identifier

### Custom Log Configuration

You can configure loguru to filter or format LLM logs:

```python
from loguru import logger

# Show only LLM-related logs
logger.add(
    "llm.log",
    filter=lambda record: "fluxibly.llm" in record["name"],
    level="INFO"
)

# Structured JSON logging
logger.add(
    "llm.json",
    serialize=True,
    filter=lambda record: "fluxibly.llm" in record["name"]
)

# Filter by framework
logger.add(
    "langchain.log",
    filter=lambda record: record["extra"].get("framework") == "langchain",
    level="DEBUG"
)
```

## Examples

### Example 1: Basic Logging
```python
from fluxibly.llm import LLM, LLMConfig

config = LLMConfig(framework="langchain", model="gpt-4o")
llm = LLM(config=config)

# Automatic logging of request/response
response = llm.forward("Hello")

# Logs:
# INFO: LLM request started | prompt_length=5
# INFO: LLM request completed | elapsed_time=1.23s, response_length=42
# DEBUG: LLM request details | prompt_preview="Hello", response_preview="Hi there!..."
```

### Example 2: Streaming Logs
```python
# Automatic logging of streaming operations
for chunk in llm.forward_stream("Tell me a story"):
    print(chunk, end="")

# Logs:
# INFO: LLM streaming request started | prompt_length=15
# INFO: LLM streaming completed | elapsed_time=3.45s, total_chunks=120, total_length=480
# DEBUG: LLM streaming details | avg_chunk_size=4.0
```

### Example 3: Error Logging
```python
try:
    response = llm.forward("This might fail")
except Exception as e:
    pass  # Error already logged by BaseLLM

# Logs:
# INFO: LLM request started
# ERROR: LLM request failed | elapsed_time=0.50s, error_type=APIError, error_message="Rate limit"
```

### Example 4: Custom Framework Logging
```python
from fluxibly.llm import BaseLLM, LLMConfig, register_llm_framework

class MyCustomLLM(BaseLLM):
    def _forward_impl(self, prompt: str, **kwargs) -> str:
        # Your implementation here
        return "response"

    def _forward_stream_impl(self, prompt: str, **kwargs):
        # Your streaming implementation
        yield "chunk"

# Register framework
register_llm_framework("mycustom", MyCustomLLM)

# Use with automatic logging
config = LLMConfig(framework="mycustom", model="my-model")
llm = LLM(config=config)

response = llm.forward("test")  # Fully logged automatically!

# Logs:
# INFO: LLM request started | name=MyCustomLLM, framework=mycustom, model=my-model
# INFO: LLM request completed | elapsed_time=0.10s
```

## Log Structure

Each log entry includes these fields in `extra`:

| Field | Description | Example |
|-------|-------------|---------|
| `name` | Implementation class name | `"LangChainLLM"` |
| `framework` | Framework identifier | `"langchain"` |
| `model` | Model identifier | `"gpt-4o"` |
| `prompt_length` | Length of input prompt | `42` |
| `response_length` | Length of response | `128` |
| `elapsed_time` | Time taken (formatted) | `"1.23s"` |
| `total_chunks` | Number of chunks (streaming) | `50` |
| `total_length` | Total response length (streaming) | `200` |
| `avg_chunk_size` | Average chunk size (streaming) | `4.0` |
| `error_type` | Exception class name (errors) | `"ValueError"` |
| `error_message` | Exception message (errors) | `"API timeout"` |

## Best Practices

### 1. Use Appropriate Log Levels
- **INFO**: Production monitoring, metrics, dashboards
- **DEBUG**: Development, troubleshooting, detailed analysis
- **ERROR**: Alert systems, error tracking

### 2. Filter Logs in Production
```python
# Production: INFO level only
logger.add("llm.log", level="INFO")

# Development: DEBUG level for detailed analysis
logger.add("llm.log", level="DEBUG")
```

### 3. Structured Logging for Analytics
```python
# JSON format for log aggregation tools
logger.add(
    "llm.json",
    serialize=True,
    format="{time} {level} {message} {extra}"
)
```

### 4. Monitor Performance Metrics
```python
# Track slow requests
logger.add(
    "slow_requests.log",
    filter=lambda r: float(r["extra"].get("elapsed_time", "0").rstrip("s")) > 5.0,
    level="WARNING"
)
```

### 5. Framework-Specific Logging
```python
# Separate logs per framework
logger.add(
    "langchain.log",
    filter=lambda r: r["extra"].get("framework") == "langchain"
)

logger.add(
    "litellm.log",
    filter=lambda r: r["extra"].get("framework") == "litellm"
)
```

## Integration with Observability Tools

### LangSmith
The logging system complements LangSmith tracing:
```python
# LangSmith for distributed tracing
# Fluxibly logs for local metrics and debugging
```

### Jaeger/OpenTelemetry
Combine with OpenTelemetry for full observability:
```python
# Use Fluxibly logs + OpenTelemetry spans
# for complete request lifecycle visibility
```

### Prometheus/Grafana
Export metrics from logs:
```python
# Parse elapsed_time, response_length from logs
# Create Prometheus metrics for dashboards
```

## Migration Guide

### From Old Implementations
If you have existing custom LLM implementations:

**Before:**
```python
class MyLLM(BaseLLM):
    def forward(self, prompt: str, **kwargs) -> str:
        logger.debug("Calling my LLM")
        try:
            result = self._call_api(prompt)
            logger.debug("Call successful")
            return result
        except Exception:
            logger.exception("Call failed")
            raise
```

**After:**
```python
class MyLLM(BaseLLM):
    def _forward_impl(self, prompt: str, **kwargs) -> str:
        # Remove manual logging - it's automatic now!
        return self._call_api(prompt)
```

### Benefits
- ✅ Less boilerplate code
- ✅ Consistent logging across all frameworks
- ✅ Automatic performance metrics
- ✅ Standardized error tracking
- ✅ Built-in request/response previews

## See Also

- [LLM Base Module](../fluxibly/llm/base.py) - Implementation details
- [LangChain Implementation](../fluxibly/llm/langchain_llm.py) - Example usage
- [LiteLLM Implementation](../fluxibly/llm/litellm_llm.py) - Example usage
- [Logging Demo](../examples/logging_demo.py) - Interactive demonstration
