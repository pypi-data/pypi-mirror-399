# Custom RAG MCP Server

A Model Context Protocol (MCP) server that integrates with an existing RAG API providing semantic search and document indexing capabilities.

## Features

- **Semantic Search**: Search indexed documents using natural language queries
- **GCS Indexing**: Index documents from Google Cloud Storage buckets
- **Flexible Configuration**: Configure API endpoint via environment variables

## Tools

### rag-search

Search the knowledge base using semantic search.

**Parameters:**
- `query` (string, required): The search query
- `limit` (integer, optional): Maximum number of results (default: 10, max: 100)
- `score_threshold` (number, optional): Minimum similarity score 0.0-1.0 (default: 0.1)

**Example:**
```json
{
  "query": "public relations course objectives",
  "limit": 5,
  "score_threshold": 0.3
}
```

### rag-index-gcs

Index documents from Google Cloud Storage.

**Parameters:**
- `gcs_path` (string, required): GCS path starting with `gs://`
- `recursive` (boolean, optional): Recursively index subdirectories (default: true)

**Example:**
```json
{
  "gcs_path": "gs://datanetwork-files-prod/documents/",
  "recursive": true
}
```

## Installation

### Local Development

```bash
# Install dependencies
cd mcp_servers/custom_rag
uv add mcp httpx

# Test the server
python -m custom_rag.server
```

### As Python Package

```bash
# From the mcp_servers/custom_rag directory
uv pip install -e .

# Run the server
custom-rag-mcp
```

## Configuration

Configure the API endpoint using environment variables:

```bash
export RAG_API_URL="http://localhost:8000"
```

Or in your MCP configuration:

```yaml
custom_rag:
  command: "python"
  args: ["-m", "mcp_servers.custom_rag.server"]
  env:
    RAG_API_URL: "http://localhost:8000"
  enabled: true
  priority: 1
```

## API Requirements

The server expects a RAG API with the following endpoints:

### POST /search

Search endpoint for semantic search.

**Request:**
```json
{
  "query": "search query",
  "limit": 10,
  "score_threshold": 0.1
}
```

**Response:**
```json
{
  "results": [
    {
      "content": "Document content...",
      "score": 0.85,
      "metadata": {
        "file_name": "document.pdf",
        "file_path": "gs://bucket/path/document.pdf"
      }
    }
  ]
}
```

### POST /index/gcs

Indexing endpoint for GCS documents.

**Request:**
```json
{
  "gcs_path": "gs://bucket/path/",
  "recursive": true
}
```

**Response:**
```json
{
  "status": "success",
  "files_processed": 42,
  "files_indexed": 40,
  "errors": []
}
```

## Usage with Fluxibly

Add to `config/mcp_servers.yaml`:

```yaml
mcp_servers:
  custom_rag:
    command: "python"
    args: ["-m", "mcp_servers.custom_rag.server"]
    env:
      RAG_API_URL: "http://localhost:8000"
    enabled: true
    priority: 1
    description: "Custom RAG server for existing API"
```

Then use in workflows:

```python
from fluxibly import WorkflowSession

async with WorkflowSession(profile="rag_assistant") as session:
    response = await session.execute(
        "Search the knowledge base for information about public relations"
    )
    print(response)
```

## Testing

Test the endpoints manually:

```bash
# Search
curl -X POST http://localhost:8000/search \
  -H 'Content-Type: application/json' \
  -d '{
    "query": "public relations",
    "limit": 10,
    "score_threshold": 0.1
  }'

# Index from GCS
curl -X POST http://localhost:8000/index/gcs \
  -H 'Content-Type: application/json' \
  -d '{
    "gcs_path": "gs://datanetwork-files-prod/test_data/",
    "recursive": true
  }'
```

## Logging

The server logs to stdout. Adjust logging level via Python's logging configuration:

```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

## Error Handling

The server handles:
- Invalid API responses
- Network errors
- Timeout errors (30s for search, 5min for indexing)
- Invalid parameters

Errors are returned as formatted text content to the MCP client.
