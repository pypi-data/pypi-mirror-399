"""Custom RAG MCP Server for existing API endpoints.

This MCP server integrates with an existing RAG API that provides:
- Index endpoint: POST /index/gcs (for indexing from Google Cloud Storage)
- Search endpoint: POST /search (for semantic search)
"""

import json
import logging
import os
from typing import Any

import httpx
from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import Tool, TextContent

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("custom-rag-mcp")

# Get API endpoint from environment
API_BASE_URL = os.getenv("RAG_API_URL", "http://localhost:8000")

# Create MCP server
app = Server("custom-rag-server")


@app.list_tools()
async def list_tools() -> list[Tool]:
    """List available tools."""
    return [
        Tool(
            name="rag-search",
            description=(
                "Search the RAG knowledge base using semantic search. "
                "Returns relevant documents based on the query with similarity scores. "
                "Use this to find information from indexed documents."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "The search query to find relevant documents",
                    },
                    "limit": {
                        "type": "integer",
                        "description": "Maximum number of results to return (default: 10)",
                        "default": 10,
                        "minimum": 1,
                        "maximum": 100,
                    },
                    "score_threshold": {
                        "type": "number",
                        "description": "Minimum similarity score threshold (0.0-1.0, default: 0.1)",
                        "default": 0.1,
                        "minimum": 0.0,
                        "maximum": 1.0,
                    },
                },
                "required": ["query"],
            },
        ),
        Tool(
            name="rag-index-gcs",
            description=(
                "Index documents from Google Cloud Storage into the RAG knowledge base. "
                "This processes and embeds documents for semantic search. "
                "Use this to add new documents to the searchable knowledge base."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "gcs_path": {
                        "type": "string",
                        "description": "Google Cloud Storage path (e.g., 'gs://bucket-name/path/')",
                    },
                    "recursive": {
                        "type": "boolean",
                        "description": "Whether to recursively index subdirectories (default: true)",
                        "default": True,
                    },
                },
                "required": ["gcs_path"],
            },
        ),
    ]


@app.call_tool()
async def call_tool(name: str, arguments: Any) -> list[TextContent]:
    """Handle tool calls."""
    try:
        if name == "rag-search":
            return await handle_search(arguments)
        elif name == "rag-index-gcs":
            return await handle_index_gcs(arguments)
        else:
            return [
                TextContent(
                    type="text",
                    text=f"Error: Unknown tool '{name}'",
                )
            ]
    except Exception as e:
        logger.error(f"Error calling tool {name}: {e}", exc_info=True)
        return [
            TextContent(
                type="text",
                text=f"Error executing {name}: {str(e)}",
            )
        ]


async def handle_search(arguments: dict[str, Any]) -> list[TextContent]:
    """Handle RAG search requests.

    Args:
        arguments: Dict with 'query', optional 'limit', and 'score_threshold'

    Returns:
        List of TextContent with search results
    """
    query = arguments.get("query")
    limit = arguments.get("limit", 10)
    score_threshold = arguments.get("score_threshold", 0.1)

    if not query:
        return [TextContent(type="text", text="Error: 'query' parameter is required")]

    search_url = f"{API_BASE_URL}/search"
    payload = {
        "query": query,
        "limit": limit,
        "score_threshold": score_threshold,
    }

    logger.info(f"Searching: query='{query}', limit={limit}, threshold={score_threshold}")

    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(search_url, json=payload)
            response.raise_for_status()
            results = response.json()

        # Format results for display
        if isinstance(results, dict) and "results" in results:
            results_list = results["results"]
        elif isinstance(results, list):
            results_list = results
        else:
            results_list = [results]

        if not results_list:
            return [
                TextContent(
                    type="text",
                    text=f"No results found for query: '{query}'\n"
                    f"Try a different query or lower the score_threshold (current: {score_threshold})",
                )
            ]

        # Build formatted response
        response_text = f"Search Results for: '{query}'\n"
        response_text += f"Found {len(results_list)} result(s)\n"
        response_text += "=" * 70 + "\n\n"

        for i, result in enumerate(results_list, 1):
            # Handle your API's response format
            score = result.get("score", 0.0)
            content = result.get("content", "")
            vector_id = result.get("vector_id", "")
            file_id = result.get("file_id", "")

            response_text += f"Result {i} (Score: {score:.4f})\n"
            response_text += "-" * 70 + "\n"

            # Add content
            if content:
                # Truncate very long content
                if len(content) > 1000:
                    content = content[:1000] + "..."
                response_text += f"Content:\n{content}\n\n"

            # Add IDs if available
            if file_id:
                response_text += f"File ID: {file_id}\n"
            if vector_id:
                response_text += f"Vector ID: {vector_id}\n"

            # Add any other metadata
            metadata_keys = [k for k in result.keys() if k not in ["score", "content", "vector_id", "file_id"]]
            if metadata_keys:
                response_text += "Additional metadata:\n"
                for key in metadata_keys:
                    response_text += f"  {key}: {result[key]}\n"

            response_text += "\n"

        logger.info(f"Search completed: {len(results_list)} results")

        return [TextContent(type="text", text=response_text)]

    except httpx.HTTPError as e:
        error_msg = f"HTTP Error searching API: {str(e)}"
        if hasattr(e, "response") and e.response is not None:
            try:
                error_detail = e.response.json()
                error_msg += f"\nAPI Response: {json.dumps(error_detail, indent=2)}"
            except Exception:
                error_msg += f"\nAPI Response: {e.response.text}"

        logger.error(error_msg)
        return [TextContent(type="text", text=error_msg)]

    except Exception as e:
        error_msg = f"Error searching: {str(e)}"
        logger.error(error_msg, exc_info=True)
        return [TextContent(type="text", text=error_msg)]


async def handle_index_gcs(arguments: dict[str, Any]) -> list[TextContent]:
    """Handle GCS indexing requests.

    Args:
        arguments: Dict with 'gcs_path' and optional 'recursive'

    Returns:
        List of TextContent with indexing status
    """
    gcs_path = arguments.get("gcs_path")
    recursive = arguments.get("recursive", True)

    if not gcs_path:
        return [TextContent(type="text", text="Error: 'gcs_path' parameter is required")]

    if not gcs_path.startswith("gs://"):
        return [
            TextContent(
                type="text",
                text=f"Error: Invalid GCS path '{gcs_path}'. Must start with 'gs://'",
            )
        ]

    index_url = f"{API_BASE_URL}/index/gcs"
    payload = {"gcs_path": gcs_path, "recursive": recursive}

    logger.info(f"Indexing from GCS: path='{gcs_path}', recursive={recursive}")

    try:
        async with httpx.AsyncClient(timeout=300.0) as client:  # 5 min timeout for indexing
            response = await client.post(index_url, json=payload)
            response.raise_for_status()
            result = response.json()

        # Format response
        response_text = f"Indexing Results for: {gcs_path}\n"
        response_text += "=" * 70 + "\n\n"

        if isinstance(result, dict):
            # Handle your API's response format
            success = result.get("success", False)
            message = result.get("message", "")
            documents_indexed = result.get("documents_indexed", 0)
            file_ids = result.get("file_ids", [])

            response_text += f"Success: {success}\n"
            if message:
                response_text += f"Message: {message}\n"
            response_text += f"Documents indexed: {documents_indexed}\n"

            if file_ids:
                response_text += f"\nIndexed file IDs ({len(file_ids)}):\n"
                for file_id in file_ids[:20]:  # Show first 20 file IDs
                    response_text += f"  - {file_id}\n"
                if len(file_ids) > 20:
                    response_text += f"  ... and {len(file_ids) - 20} more\n"

            # Add any additional info
            extra_keys = [k for k in result.keys() if k not in ["success", "message", "documents_indexed", "file_ids"]]
            if extra_keys:
                response_text += "\nAdditional information:\n"
                for key in extra_keys:
                    response_text += f"  {key}: {result[key]}\n"
        else:
            response_text += f"Result: {json.dumps(result, indent=2)}\n"

        logger.info(f"Indexing completed: {gcs_path}")

        return [TextContent(type="text", text=response_text)]

    except httpx.HTTPError as e:
        error_msg = f"HTTP Error indexing from GCS: {str(e)}"
        if hasattr(e, "response") and e.response is not None:
            try:
                error_detail = e.response.json()
                error_msg += f"\nAPI Response: {json.dumps(error_detail, indent=2)}"
            except Exception:
                error_msg += f"\nAPI Response: {e.response.text}"

        logger.error(error_msg)
        return [TextContent(type="text", text=error_msg)]

    except Exception as e:
        error_msg = f"Error indexing from GCS: {str(e)}"
        logger.error(error_msg, exc_info=True)
        return [TextContent(type="text", text=error_msg)]


async def main() -> None:
    """Run the MCP server."""
    logger.info("Starting Custom RAG MCP Server")
    logger.info(f"API Base URL: {API_BASE_URL}")

    async with stdio_server() as (read_stream, write_stream):
        await app.run(read_stream, write_stream, app.create_initialization_options())


if __name__ == "__main__":
    import asyncio

    asyncio.run(main())
