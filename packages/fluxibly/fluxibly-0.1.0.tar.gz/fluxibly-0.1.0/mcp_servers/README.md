# MCP Servers

This directory contains example MCP server implementations that provide specialized capabilities to the framework.

## Available Servers

### Custom RAG Server (`custom_rag/`) ✅ **READY TO USE**

Integrates with your existing RAG API for semantic search and document indexing.

**Tools:**
- `rag-search` - Search the knowledge base with semantic search
- `rag-index-gcs` - Index documents from Google Cloud Storage

**Status**: ✅ Fully implemented and configured

**See**: [custom_rag/README.md](custom_rag/README.md) for detailed documentation

**Configuration**:
```yaml
custom_rag:
  command: "python"
  args: ["-m", "mcp_servers.custom_rag.server"]
  env:
    RAG_API_URL: "http://localhost:8000"
  enabled: true
```

---

### OCR Server (`ocr/`) ⚠️ **NOT YET IMPLEMENTED**

Provides optical character recognition capabilities for text extraction from images and documents.

**Planned Tools:**
- `extract_text` - Extract text from images
- `parse_document` - Parse document structure
- `detect_layout` - Detect layout elements

### Vision Server (`vision/`) ⚠️ **NOT YET IMPLEMENTED**

Provides computer vision and image understanding capabilities.

**Planned Tools:**
- `describe_image` - Generate image descriptions
- `detect_objects` - Detect and identify objects
- `analyze_scene` - Analyze scene composition

### Code Server (`code/`) ⚠️ **NOT YET IMPLEMENTED**

Provides code generation, execution, and analysis capabilities.

**Planned Tools:**
- `generate_code` - Generate code from descriptions
- `execute_code` - Execute code in sandbox
- `review_code` - Review code quality

### Research Server (`research/`) ⚠️ **NOT YET IMPLEMENTED**

Provides web search, data synthesis, and fact-checking capabilities.

**Planned Tools:**
- `web_search` - Search the web
- `synthesize_data` - Synthesize information
- `fact_check` - Verify factual claims

## Adding a New MCP Server

To add a new capability to the framework:

1. **Create Server Directory**
   ```bash
   mkdir mcp_servers/your_capability
   touch mcp_servers/your_capability/__init__.py
   touch mcp_servers/your_capability/server.py
   ```

2. **Implement MCP Server**
   ```python
   # mcp_servers/your_capability/server.py
   from mcp.server import Server
   from mcp.types import Tool, TextContent

   server = Server("your-capability")

   @server.list_tools()
   async def list_tools() -> list[Tool]:
       return [
           Tool(
               name="your_tool",
               description="Tool description",
               inputSchema={
                   "type": "object",
                   "properties": {...}
               }
           )
       ]

   @server.call_tool()
   async def call_tool(name: str, arguments: dict):
       if name == "your_tool":
           result = await process(arguments)
           return [TextContent(type="text", text=result)]
   ```

3. **Register in Configuration**
   Add to `config/mcp_servers.yaml`:
   ```yaml
   your_capability:
     command: "python"
     args: ["-m", "mcp_servers.your_capability.server"]
     env:
       YOUR_CONFIG: "value"
     enabled: true
     priority: 1
   ```

4. **Test Server**
   ```bash
   python -m mcp_servers.your_capability.server
   ```

5. **Use in Framework**
   The orchestrator will automatically discover and use your new tools!

## MCP Protocol Resources

- [MCP Documentation](https://modelcontextprotocol.io/)
- [MCP Python SDK](https://github.com/modelcontextprotocol/python-sdk)
- [Community Servers](https://github.com/modelcontextprotocol/servers)
