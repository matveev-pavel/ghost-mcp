"""MCP server for Ghost CMS."""

from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from mcp.server.fastmcp import FastMCP

from ghost_mcp.client import GhostClient
from ghost_mcp.tools.images import register_image_tools
from ghost_mcp.tools.pages import register_page_tools
from ghost_mcp.tools.posts import register_post_tools
from ghost_mcp.tools.tags import register_tag_tools


def create_server(url: str, admin_key: str) -> FastMCP:
    """Create and configure the MCP server."""
    client = GhostClient(url, admin_key)

    @asynccontextmanager
    async def lifespan(server: FastMCP) -> AsyncIterator[None]:
        try:
            yield
        finally:
            await client.close()

    mcp = FastMCP(
        "Ghost CMS",
        instructions=(
            "MCP server for managing Ghost CMS content. "
            "Create, edit, delete posts and pages, manage tags, and upload images."
        ),
        lifespan=lifespan,
    )

    register_post_tools(mcp, client)
    register_page_tools(mcp, client)
    register_tag_tools(mcp, client)
    register_image_tools(mcp, client)

    return mcp
