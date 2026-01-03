#!/usr/bin/env python3
"""
MCP Server for GitHub Actions Latest Versions

This server provides a tool to fetch the latest versions of GitHub Actions
from https://simonw.github.io/actions-latest/versions.txt
"""

import asyncio
import logging
from typing import Any

import httpx
from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import Tool, TextContent

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("actions-latest-mcp")

# The URL to fetch versions from
VERSIONS_URL = "https://simonw.github.io/actions-latest/versions.txt"

# Create server instance
app = Server("actions-latest-mcp")


@app.list_tools()
async def list_tools() -> list[Tool]:
    """List available tools."""
    return [
        Tool(
            name="latest_github_actions_versions",
            description=(
                "Returns a list of latest versions of all actions from the official "
                "GitHub Actions organization. This is useful for keeping your "
                "workflows up to date with the latest action versions."
            ),
            inputSchema={
                "type": "object",
                "properties": {}
            }
        )
    ]


@app.call_tool()
async def call_tool(name: str, arguments: Any) -> list[TextContent]:
    """Handle tool calls."""
    if name != "latest_github_actions_versions":
        raise ValueError(f"Unknown tool: {name}")

    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(VERSIONS_URL)
            response.raise_for_status()
            content = response.text
            
            return [
                TextContent(
                    type="text",
                    text=content
                )
            ]
    except httpx.HTTPError as e:
        error_msg = f"Failed to fetch versions.txt from {VERSIONS_URL}: {str(e)}"
        if hasattr(e, 'response') and e.response is not None:
            error_msg += f" (Status: {e.response.status_code})"
        logger.error(error_msg)
        return [
            TextContent(
                type="text",
                text=error_msg
            )
        ]
    except Exception as e:
        error_msg = f"Unexpected error: {str(e)}"
        logger.error(error_msg)
        return [
            TextContent(
                type="text",
                text=error_msg
            )
        ]


async def main():
    """Run the MCP server."""
    async with stdio_server() as (read_stream, write_stream):
        await app.run(
            read_stream,
            write_stream,
            app.create_initialization_options()
        )


def run():
    """Entry point for the server."""
    asyncio.run(main())


if __name__ == "__main__":
    run()
