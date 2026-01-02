# Fluxibly Documentation

Welcome to the Fluxibly documentation!

## Table of Contents

1. [Getting Started](getting-started.md)
2. [Architecture Overview](architecture.md)
3. [Configuration Guide](configuration.md)
4. [Creating MCP Servers](mcp-servers.md)
5. [API Reference](api-reference.md)
6. [Development Guide](development.md)

## What is Fluxibly?

Fluxibly is a modular, extensible agentic framework built on LangGraph with an MCP-native approach. It transforms the traditional sub-agent pattern by implementing all specialized agents as independent MCP (Model Context Protocol) servers.

## Key Concepts

### Orchestrator Agent
The single LLM-powered agent that manages all MCP interactions, handling task analysis, tool selection, execution planning, and result synthesis.

### MCP Servers
Independent processes that implement the Model Context Protocol and expose specialized capabilities (OCR, vision, code execution, etc.) as tools.

### Unified Input Schema
A standardized input format for handling heterogeneous content types including images, documents, videos, and more.

### Configuration Profiles
Pre-configured settings optimized for specific use cases like document processing or development assistance.

## Quick Links

- [GitHub Repository](https://github.com/your-org/fluxibly)
- [Design Document](../Agentic_Framework_Design_Document_v0.2.docx)
- [MCP Protocol Documentation](https://modelcontextprotocol.io/)

## Getting Help

- Open an issue on GitHub
- Check the [FAQ](faq.md)
- Review example implementations in [mcp_servers/](../mcp_servers/)

---

**Note**: This documentation is under active development. Some sections may be incomplete.
