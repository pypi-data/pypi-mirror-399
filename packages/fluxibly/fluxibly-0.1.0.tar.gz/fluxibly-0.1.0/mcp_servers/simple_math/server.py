"""Simple Math MCP Server for testing.

A minimal MCP server that provides basic math operations for testing the MCP client.
"""

import asyncio

from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import TextContent, Tool

# Create server instance
app = Server("simple-math")


@app.list_tools()
async def list_tools() -> list[Tool]:
    """List available math tools."""
    return [
        Tool(
            name="add",
            description="Add two numbers together",
            inputSchema={
                "type": "object",
                "properties": {
                    "a": {"type": "number", "description": "First number"},
                    "b": {"type": "number", "description": "Second number"},
                },
                "required": ["a", "b"],
            },
        ),
        Tool(
            name="multiply",
            description="Multiply two numbers together",
            inputSchema={
                "type": "object",
                "properties": {
                    "a": {"type": "number", "description": "First number"},
                    "b": {"type": "number", "description": "Second number"},
                },
                "required": ["a", "b"],
            },
        ),
        Tool(
            name="power",
            description="Raise a number to a power",
            inputSchema={
                "type": "object",
                "properties": {
                    "base": {"type": "number", "description": "Base number"},
                    "exponent": {"type": "number", "description": "Exponent"},
                },
                "required": ["base", "exponent"],
            },
        ),
    ]


@app.call_tool()
async def call_tool(name: str, arguments: dict) -> list[TextContent]:
    """Execute a math tool."""
    if name == "add":
        a = arguments["a"]
        b = arguments["b"]
        result = a + b
        return [TextContent(type="text", text=f"The sum of {a} and {b} is {result}")]

    elif name == "multiply":
        a = arguments["a"]
        b = arguments["b"]
        result = a * b
        return [TextContent(type="text", text=f"The product of {a} and {b} is {result}")]

    elif name == "power":
        base = arguments["base"]
        exponent = arguments["exponent"]
        result = base**exponent
        return [TextContent(type="text", text=f"{base} raised to the power of {exponent} is {result}")]

    else:
        raise ValueError(f"Unknown tool: {name}")


async def main():
    """Run the Simple Math MCP server."""
    async with stdio_server() as (read_stream, write_stream):
        await app.run(read_stream, write_stream, app.create_initialization_options())


if __name__ == "__main__":
    asyncio.run(main())
