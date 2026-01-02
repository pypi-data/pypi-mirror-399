# feat: Complete agent framework initialization with orchestration and MCP integration

## Summary

This PR establishes the foundational architecture for the Fluxibly agent framework, implementing a complete end-to-end workflow system with orchestration capabilities and MCP client integration.

## Key Changes

### Configuration Framework
- Added YAML-based configuration system for framework settings, MCP servers, orchestrator prompts, and user profiles
- Implemented configuration loader with environment variable support
- Added `.env.example` for documentation

### Agent System Refactoring
- Refactored agent base class for better maintainability
- Extracted agent configuration and conversation history into dedicated modules
- Enhanced agent initialization with dynamic type configuration

### Orchestration System
- Implemented modular orchestration with planner, executor, synthesizer, and selector components
- Added centralized prompt configuration system
- Enhanced orchestrator agent with conversation history support

### MCP Client Integration
- Implemented comprehensive MCP client manager with lifecycle management
- Added simple math MCP server as example
- Integrated MCP servers with configuration system

### Workflow Engine
- Built end-to-end workflow execution engine
- Implemented stateful context management for multi-turn conversations
- Added workflow configuration management

### Testing Infrastructure
- Added comprehensive unit tests for all new components
- Total coverage: 4,365 lines across 8 test files
- Validates configuration loading, agent initialization, orchestration, MCP lifecycle, and workflow execution

## Statistics

- **38 files changed**: 7,077 insertions, 497 deletions
- **Net addition**: 6,580 lines

## Architecture Improvements

- Modular design with separated concerns
- Configuration-driven approach for flexibility
- Reduced agent base class complexity (260 lines removed)
- Type hints and comprehensive docstrings throughout
