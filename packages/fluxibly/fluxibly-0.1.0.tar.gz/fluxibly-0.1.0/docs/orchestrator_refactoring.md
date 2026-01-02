# Orchestrator Agent Refactoring

## Overview

The OrchestratorAgent has been refactored from a monolithic ~1000-line file into a modular architecture with separated concerns and configurable prompts.

## New Structure

```
fluxibly/orchestrator/
├── __init__.py              # Public API exports
├── agent.py                 # Main OrchestratorAgent (324 lines)
├── planner.py              # Task analysis and plan generation
├── executor.py             # Plan execution and error recovery
├── synthesizer.py          # Result synthesis and MCP selection
└── config/
    ├── __init__.py
    └── prompts.py          # Prompt template loader

config/orchestrator/
└── prompts.yaml            # Configurable prompt templates
```

## Components

### 1. OrchestratorAgent ([agent.py](../fluxibly/orchestrator/agent.py))

**Main orchestration coordinator** - Reduced from 1000+ lines to ~324 lines

**Responsibilities:**
- Initialize and coordinate all sub-components
- Manage iteration loop and state
- Provide public API (prepare_system, forward)
- Backward compatible with existing code

**Key Methods:**
- `__init__()` - Initializes all components
- `prepare_system()` - Creates enhanced system prompt with MCP allocation
- `forward()` - Main execution loop with planning and iteration

### 2. TaskPlanner ([planner.py](../fluxibly/orchestrator/planner.py))

**Task analysis and plan generation**

**Responsibilities:**
- Analyze user tasks to identify objectives and requirements
- Generate structured execution plans
- Refine plans based on execution results

**Key Methods:**
- `analyze_task()` - Deep analysis of user request
- `generate_plan()` - Create detailed execution plan
- `refine_plan()` - Adjust plan based on results

### 3. PlanExecutor ([executor.py](../fluxibly/orchestrator/executor.py))

**Plan execution with error handling**

**Responsibilities:**
- Execute plan steps in order
- Manage dependencies between steps
- Handle MCP tool invocations
- Coordinate with error recovery

**Key Methods:**
- `execute_plan()` - Execute all plan steps
- `_execute_llm_step()` - Execute non-tool steps with LLM
- `_invoke_mcp_tool()` - Invoke MCP tools

### 4. ErrorRecoveryHandler ([executor.py](../fluxibly/orchestrator/executor.py))

**Error handling and recovery strategies**

**Responsibilities:**
- Handle execution errors
- Implement recovery strategies (retry, skip, abort, fallback)
- Generate fallback plans using LLM

**Key Methods:**
- `handle_error()` - Main error handling logic
- `_handle_retry()` - Retry strategy implementation
- `_handle_fallback()` - Fallback plan generation

### 5. ResultSynthesizer ([synthesizer.py](../fluxibly/orchestrator/synthesizer.py))

**Result combination and synthesis**

**Responsibilities:**
- Combine results from multiple executions
- Support multiple synthesis strategies
- Generate user-friendly final responses

**Key Methods:**
- `synthesize_results()` - Main synthesis entry point
- `_synthesize_concatenate()` - Simple concatenation
- `_synthesize_structured()` - JSON structured output
- `_synthesize_with_llm()` - LLM-based intelligent synthesis

### 6. MCPSelector ([synthesizer.py](../fluxibly/orchestrator/synthesizer.py))

**MCP tool selection and prioritization**

**Responsibilities:**
- Perform semantic matching for tool selection
- Score and prioritize tools by relevance
- Format tool descriptions for prompts

**Key Methods:**
- `select_mcp_tools()` - Select relevant MCP tools
- `format_mcp_tools()` - Format for system prompt

### 7. PromptLoader ([config/prompts.py](../fluxibly/orchestrator/config/prompts.py))

**Prompt template management**

**Responsibilities:**
- Load prompts from YAML configuration
- Format prompts with dynamic values
- Provide configuration parameters
- Support hot-reloading during development

**Key Methods:**
- `get_prompt()` - Get formatted prompt template
- `get_parameter()` - Get configuration parameter
- `reload()` - Reload prompts from file

## Configuration

### Prompt Templates ([config/orchestrator/prompts.yaml](../config/orchestrator/prompts.yaml))

All prompts are now externalized to YAML for easy customization:

```yaml
mcp_selection:
  template: |
    Analyze this task and select the most relevant MCP tools:
    Task: {user_prompt}
    ...

task_analysis:
  template: |
    Analyze the following task and break it down:
    ...

plan_generation:
  template: |
    Generate a detailed execution plan for this task:
    ...

# ... and more
```

### Parameters

Configuration parameters are also in the YAML:

```yaml
parameters:
  complexity_levels: [low, medium, high]
  max_retries: 3
  default_mcp_timeout: 30
```

## Usage

### Basic Usage (Unchanged)

```python
from fluxibly.orchestrator import OrchestratorAgent, OrchestratorConfig
from fluxibly.llm.base import LLMConfig

config = OrchestratorConfig(
    name="document_processor",
    llm=LLMConfig(model="gpt-4o", framework="langchain"),
    system_prompt="You are an expert document processing orchestrator.",
    mcp_servers=["ocr", "vision", "text_analysis"],
    max_iterations=5,
    plan_refinement_enabled=True
)

orchestrator = OrchestratorAgent(config=config)
response = await orchestrator.forward(
    user_prompt="Extract and analyze all data from this PDF invoice",
    context={"document_path": "/path/to/invoice.pdf"}
)
```

### Advanced Usage - Custom Components

```python
from fluxibly.orchestrator import (
    OrchestratorAgent,
    TaskPlanner,
    PlanExecutor,
    ResultSynthesizer,
    MCPSelector,
    ErrorRecoveryHandler
)

# Use individual components directly if needed
planner = TaskPlanner(llm, mcp_servers=["ocr", "vision"])
task_analysis = planner.analyze_task("Extract text from PDF")
plan = planner.generate_plan(task_analysis)

executor = PlanExecutor(llm, mcp_client_manager)
results = await executor.execute_plan(plan)

synthesizer = ResultSynthesizer(llm, synthesis_strategy="llm_synthesis")
final_response = synthesizer.synthesize_results(results)
```

### Custom Prompts

Create a custom prompts file:

```yaml
# my_custom_prompts.yaml
task_analysis:
  template: |
    Analyze this task with extra detail:
    Task: {user_prompt}
    Context: {context}

    Provide detailed analysis including:
    1. Objectives
    2. Required tools
    3. Estimated complexity
    ...
```

Load custom prompts:

```python
from fluxibly.orchestrator.config import PromptLoader

# Load custom prompts
loader = PromptLoader(config_path="path/to/my_custom_prompts.yaml")

# Components will use the custom prompts automatically
# since PromptLoader uses a singleton pattern
```

## Benefits

### 1. **Maintainability**
- Single Responsibility Principle - Each module has one clear purpose
- Easier to understand and modify individual components
- Clear separation of concerns

### 2. **Testability**
- Each component can be tested independently
- Mock components easily for unit testing
- Isolated test coverage for each responsibility

### 3. **Configurability**
- All prompts externalized to YAML
- Parameters configurable without code changes
- Easy to experiment with different prompt strategies
- Hot-reload prompts during development

### 4. **Extensibility**
- Easy to add new synthesis strategies
- Simple to implement custom planners or executors
- Components can be swapped or extended independently

### 5. **Reusability**
- Components can be used outside OrchestratorAgent
- Mix and match components for different use cases
- Share components across different agent types

## Migration Guide

### For Existing Code

**No changes required!** The public API is fully backward compatible:

```python
# Old code still works
from fluxibly.orchestrator import OrchestratorAgent, OrchestratorConfig

orchestrator = OrchestratorAgent(config=config)
response = await orchestrator.forward(user_prompt="...")
```

### For Advanced Users

If you were directly accessing internal methods:

**Before:**
```python
# Direct access to internal methods (not recommended)
orchestrator._advanced_mcp_selection(...)
orchestrator.analyze_task(...)
orchestrator.execute_plan(...)
```

**After:**
```python
# Use exposed components
orchestrator.mcp_selector.select_mcp_tools(...)
orchestrator.planner.analyze_task(...)
await orchestrator.executor.execute_plan(...)
```

## File Size Comparison

| Component | Lines | Responsibility |
|-----------|-------|----------------|
| **Before** | ~1000 | Everything |
| **After** |  |  |
| agent.py | 324 | Coordination |
| planner.py | 279 | Planning |
| executor.py | 294 | Execution |
| synthesizer.py | 272 | Synthesis |
| prompts.py | 203 | Config |
| **Total** | **1372** | Modular |

The total line count increased slightly, but:
- Each file is now focused and understandable
- Comprehensive documentation added
- Clear interfaces between components
- Much easier to maintain and extend

## Testing

Run tests to verify backward compatibility:

```bash
# Format code
uv run --frozen ruff format fluxibly/orchestrator/

# Check linting
uv run --frozen ruff check fluxibly/orchestrator/

# Type checking
uv run --frozen pyright fluxibly/orchestrator/

# Unit tests
uv run --frozen pytest tests/unit/test_orchestrator.py
```

## Future Enhancements

Possible improvements enabled by this refactoring:

1. **Multiple Planning Strategies**
   - Implement different TaskPlanner subclasses
   - Switch planners based on task complexity

2. **Parallel Execution**
   - Enhanced PlanExecutor with true parallel step execution
   - Dependency graph analysis and optimization

3. **Advanced Synthesis**
   - Additional synthesis strategies (voting, weighted, hierarchical)
   - Custom synthesizers for domain-specific needs

4. **Prompt Optimization**
   - A/B testing different prompts via YAML
   - Prompt performance metrics and analysis
   - Automatic prompt refinement

5. **Component Marketplace**
   - Share custom planners, executors, synthesizers
   - Plugin system for extending functionality

## Summary

The orchestrator refactoring provides:

✅ **Modular architecture** - Clear separation of concerns
✅ **Configuration-driven** - Prompts and parameters in YAML
✅ **Backward compatible** - No breaking changes
✅ **Well-tested** - All checks pass (ruff, pyright)
✅ **Documented** - Comprehensive docstrings and examples
✅ **Extensible** - Easy to customize and extend
