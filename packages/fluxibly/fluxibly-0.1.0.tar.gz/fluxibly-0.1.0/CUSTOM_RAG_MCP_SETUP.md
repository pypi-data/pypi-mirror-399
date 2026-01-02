## Custom RAG MCP Server - Complete Setup

Great discovery! The public Qdrant MCP server creates its own database and cannot use your existing Qdrant instance. This custom MCP server solves that by integrating directly with your existing RAG API.

## Problem Solved

**Issue**: Public `mcp-server-qdrant` creates a new database and doesn't connect to existing Qdrant collections.

**Solution**: Custom MCP server that calls your existing API endpoints:
- `POST /search` - Semantic search
- `POST /index/gcs` - Index documents from Google Cloud Storage

## What Was Created

### 1. Custom MCP Server

**Location**: `mcp_servers/custom_rag/`

**Files**:
- `server.py` - Main MCP server implementation
- `__init__.py` - Package initialization
- `pyproject.toml` - Package configuration
- `README.md` - Documentation

**Tools Provided**:
1. **rag-search** - Search the knowledge base
   - Parameters: `query`, `limit` (default: 10), `score_threshold` (default: 0.1)

2. **rag-index-gcs** - Index documents from GCS
   - Parameters: `gcs_path` (gs://...), `recursive` (default: true)

### 2. Configuration Updates

**File**: `config/mcp_servers.yaml`

```yaml
# Disabled public Qdrant MCP
qdrant:
  enabled: false  # Can't use existing database

# Enabled custom RAG MCP
custom_rag:
  command: "python"
  args: ["-m", "mcp_servers.custom_rag.server"]
  env:
    RAG_API_URL: "http://localhost:8000"
  enabled: true
  priority: 1
```

**File**: `config/profiles/rag_assistant.yaml`

```yaml
enabled_servers:
  - custom_rag  # Use custom RAG server

system_prompt: |
  You are a RAG assistant with access to a knowledge base API.

  Available Tools:
  - rag-search: Search the knowledge base
  - rag-index-gcs: Index documents from GCS
  ...
```

### 3. Test Script

**File**: `examples/test_custom_rag_mcp.py`

Tests:
1. Basic semantic search
2. Conversational queries with context
3. Multi-hop reasoning
4. GCS indexing (optional)

## How It Works

```
User Query
    ↓
Fluxibly WorkflowSession (profile: rag_assistant)
    ↓
OrchestratorAgent (with custom_rag MCP tools)
    ↓
Custom RAG MCP Server
    ↓
HTTP POST to your API (localhost:8000)
    ↓
Your RAG API (search/index endpoints)
    ↓
Existing Qdrant Database
```

## API Requirements

Your API must provide these endpoints:

### POST /search

**Request**:
```json
{
  "query": "public relations",
  "limit": 10,
  "score_threshold": 0.1
}
```

**Response**:
```json
{
  "results": [
    {
      "content": "Document text...",
      "score": 0.85,
      "metadata": {
        "file_name": "document.pdf",
        "file_path": "gs://bucket/path/"
      }
    }
  ]
}
```

### POST /index/gcs

**Request**:
```json
{
  "gcs_path": "gs://datanetwork-files-prod/test_data/",
  "recursive": true
}
```

**Response**:
```json
{
  "status": "success",
  "files_processed": 42,
  "files_indexed": 40,
  "errors": []
}
```

## Setup Instructions

### 1. Install Dependencies

```bash
# MCP dependencies
uv add mcp httpx

# Verify installation
python -c "import mcp, httpx; print('✓ Dependencies installed')"
```

### 2. Verify API is Running

```bash
# Test search endpoint
curl -X POST http://localhost:8000/search \
  -H 'Content-Type: application/json' \
  -d '{
    "query": "test",
    "limit": 5,
    "score_threshold": 0.1
  }'

# Should return JSON with results
```

### 3. Test MCP Server Standalone

```bash
# Run the MCP server directly
RAG_API_URL=http://localhost:8000 python -m mcp_servers.custom_rag.server

# Server should start and wait for MCP protocol messages
# Press Ctrl+C to stop
```

### 4. Test Through Fluxibly

```bash
# Run the test script
uv run python examples/test_custom_rag_mcp.py

# Or use directly in code:
python examples/test_custom_rag_mcp.py
```

## Usage Examples

### Simple Search

```python
from fluxibly import WorkflowSession

async with WorkflowSession(profile="rag_assistant") as session:
    response = await session.execute(
        "Search for information about public relations courses"
    )
    print(response)
```

### Advanced Search with Parameters

```python
async with WorkflowSession(profile="rag_assistant") as session:
    response = await session.execute(
        """
        Use rag-search to find documents about "learning outcomes"
        with limit=5 and score_threshold=0.3
        """
    )
    print(response)
```

### Index Documents from GCS

```python
async with WorkflowSession(profile="rag_assistant") as session:
    response = await session.execute(
        """
        Index new documents from Google Cloud Storage.
        Use rag-index-gcs with:
        - gcs_path: gs://datanetwork-files-prod/documents/
        - recursive: true
        """
    )
    print(response)
```

### Multi-turn Conversation

```python
async with WorkflowSession(profile="rag_assistant") as session:
    # First query
    response1 = await session.execute(
        "What courses are in the knowledge base?"
    )

    # Follow-up (uses context)
    response2 = await session.execute(
        "Tell me more about the learning objectives"
    )
```

## Troubleshooting

### Issue: "Connection refused to localhost:8000"

**Solution**: Make sure your RAG API is running:
```bash
# Check if API is running
curl http://localhost:8000/health  # or appropriate health endpoint

# Start your API if needed
# (your specific command to start the API)
```

### Issue: "Error: Unknown tool 'rag-search'"

**Solution**:
1. Check MCP server is enabled in `config/mcp_servers.yaml`
2. Verify `enabled_servers` in profile includes `custom_rag`
3. Restart your workflow session

### Issue: "No results found"

**Solutions**:
- Lower `score_threshold` (try 0.0 for all results)
- Increase `limit` to get more results
- Check that documents are indexed in your database
- Try different query phrasings

### Issue: MCP server not starting

**Solution**:
```bash
# Check dependencies
python -c "import mcp, httpx"

# Check module can be imported
python -c "from mcp_servers.custom_rag import server"

# Check environment variable
echo $RAG_API_URL  # Should show http://localhost:8000
```

## Testing Checklist

- [ ] RAG API running on localhost:8000
- [ ] `/search` endpoint returns results
- [ ] `/index/gcs` endpoint works (optional for initial testing)
- [ ] `mcp` and `httpx` packages installed
- [ ] OpenAI API key in `local.env`
- [ ] Custom MCP server enabled in `config/mcp_servers.yaml`
- [ ] Profile uses `custom_rag` in `enabled_servers`
- [ ] Test script runs successfully

## Next Steps

1. **Test the setup**:
   ```bash
   uv run python examples/test_custom_rag_mcp.py
   ```

2. **Verify search works**:
   - Run a simple search query
   - Check that results come from your existing database

3. **Try indexing** (if needed):
   - Use `rag-index-gcs` to add new documents
   - Verify they appear in search results

4. **Integrate into workflows**:
   - Use in your existing RAG examples
   - Build custom workflows with search + indexing

## Key Differences from Public MCP

| Aspect | Public `mcp-server-qdrant` | Custom `custom_rag` |
|--------|---------------------------|---------------------|
| Database | Creates its own | Uses your existing DB |
| Connection | Direct Qdrant client | HTTP API calls |
| Indexing | Built-in store tool | Your GCS indexing endpoint |
| Search | Built-in find tool | Your search endpoint |
| Flexibility | Fixed structure | Customizable to your API |

## Benefits

✅ Uses your existing database and data
✅ No data migration needed
✅ Works with your current indexing pipeline
✅ Fully customizable to your API structure
✅ Can add more tools/endpoints easily
✅ Integrates with Fluxibly workflows seamlessly

## File Structure

```
fluxibly/
├── config/
│   ├── mcp_servers.yaml          # MCP server configuration
│   └── profiles/
│       └── rag_assistant.yaml    # RAG profile with custom_rag
├── mcp_servers/
│   └── custom_rag/
│       ├── __init__.py           # Package init
│       ├── server.py             # MCP server implementation
│       ├── pyproject.toml        # Package config
│       └── README.md             # Server documentation
├── examples/
│   └── test_custom_rag_mcp.py   # Test script
└── CUSTOM_RAG_MCP_SETUP.md      # This file
```
