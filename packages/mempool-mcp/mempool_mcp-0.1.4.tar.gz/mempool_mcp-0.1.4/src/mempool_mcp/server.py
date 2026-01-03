"""MCP server for Mempool.space Bitcoin explorer API."""

import asyncio
import json
import logging
import os
import sys

from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import Tool, TextContent

from .client import MempoolClient

# Disable logging to avoid interfering with MCP stdio communication
logging.basicConfig(level=logging.CRITICAL)


# Only expose the 3 tools we actually use (saves ~28k tokens of context)
ENABLED_TOOLS = [
    Tool(
        name="get_block_tip_height",
        description="Get the current block height (chain tip).",
        inputSchema={
            "type": "object",
            "properties": {},
            "required": [],
        },
    ),
    Tool(
        name="get_historical_price",
        description="Get historical Bitcoin price data.",
        inputSchema={
            "type": "object",
            "properties": {
                "currency": {
                    "type": "string",
                    "description": "Currency code (default: USD)",
                    "default": "USD",
                },
                "timestamp": {
                    "type": "integer",
                    "description": "Unix timestamp for historical price (optional)",
                },
            },
            "required": [],
        },
    ),
    Tool(
        name="get_mining_pools",
        description="Get mining pool statistics for a time interval. Shows pool distribution, block counts, and hashrate share.",
        inputSchema={
            "type": "object",
            "properties": {
                "interval": {
                    "type": "string",
                    "description": "Time interval: 24h, 3d, 1w, 1m, 3m, 6m, 1y, 2y, 3y, all (default: 1w)",
                    "default": "1w",
                },
            },
            "required": [],
        },
    ),
]


def get_all_tools() -> list[Tool]:
    """Get enabled tool definitions."""
    return ENABLED_TOOLS


async def handle_tool(name: str, arguments: dict, client: MempoolClient) -> list[TextContent]:
    """Handle the 3 enabled tools."""
    try:
        if name == "get_block_tip_height":
            result = await client.get_block_tip_height()
            return [TextContent(type="text", text=f"Current block height: {result}")]

        elif name == "get_historical_price":
            currency = arguments.get("currency", "USD")
            timestamp = arguments.get("timestamp")
            result = await client.get_historical_price(currency, timestamp)
            return [TextContent(type="text", text=json.dumps(result, indent=2))]

        elif name == "get_mining_pools":
            interval = arguments.get("interval", "1w")
            result = await client.get_mining_pools(interval)
            return [TextContent(type="text", text=json.dumps(result, indent=2))]

    except Exception as e:
        return [TextContent(type="text", text=f"Error: {str(e)}")]

    return [TextContent(type="text", text=f"Unknown tool: {name}")]


async def run_server() -> None:
    """Run the MCP server."""
    # Get base URL from environment (required)
    base_url = os.getenv("MEMPOOL_API_URL")

    if not base_url:
        print("ERROR: MEMPOOL_API_URL not set!", file=sys.stderr)
        sys.exit(1)

    # Initialize the API client
    client = MempoolClient(base_url)

    # Create the MCP server
    server = Server("mempool")

    # Register single consolidated list_tools handler
    @server.list_tools()
    async def list_tools() -> list[Tool]:
        return get_all_tools()

    # Register single consolidated call_tool handler
    @server.call_tool()
    async def call_tool(name: str, arguments: dict) -> list[TextContent]:
        return await handle_tool(name, arguments, client)

    # Run the server over stdio
    try:
        async with stdio_server() as (read_stream, write_stream):
            await server.run(
                read_stream,
                write_stream,
                server.create_initialization_options(),
            )
    finally:
        await client.close()


def main() -> None:
    """Entry point for the MCP server."""
    asyncio.run(run_server())


if __name__ == "__main__":
    main()
