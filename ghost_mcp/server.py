"""MCP server for Ghost CMS."""

from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from mcp.server.fastmcp import FastMCP

from ghost_mcp.client import GhostClient
from ghost_mcp.tools.images import register_image_tools
from ghost_mcp.tools.pages import register_page_tools
from ghost_mcp.tools.posts import register_post_tools
from ghost_mcp.tools.tags import register_tag_tools

ALL_TOOL_GROUPS = {"posts", "pages", "tags", "images"}

PRESETS: dict[str, dict] = {
    "all": {"tools": ALL_TOOL_GROUPS, "readonly": False},
    "writer": {"tools": {"posts", "tags", "images"}, "readonly": False},
    "content": {"tools": {"posts", "pages", "tags", "images"}, "readonly": False},
    "readonly": {"tools": ALL_TOOL_GROUPS, "readonly": True},
}


def resolve_config(
    tools: str | None = None,
    preset: str | None = None,
) -> tuple[set[str], bool]:
    """Resolve tools and readonly from explicit tools list or preset name."""
    if tools:
        groups = {t.strip() for t in tools.split(",")}
        invalid = groups - ALL_TOOL_GROUPS
        if invalid:
            raise ValueError(
                f"Unknown tool groups: {', '.join(sorted(invalid))}. "
                f"Available: {', '.join(sorted(ALL_TOOL_GROUPS))}"
            )
        return groups, False

    if preset:
        if preset not in PRESETS:
            raise ValueError(
                f"Unknown preset '{preset}'. Available: {', '.join(sorted(PRESETS))}"
            )
        cfg = PRESETS[preset]
        return cfg["tools"], cfg["readonly"]

    return ALL_TOOL_GROUPS, False


def create_server(
    url: str,
    admin_key: str,
    tools: set[str] | None = None,
    readonly: bool = False,
) -> FastMCP:
    """Create and configure the MCP server."""
    if tools is None:
        tools = ALL_TOOL_GROUPS

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

    if "posts" in tools:
        register_post_tools(mcp, client, readonly=readonly)
    if "pages" in tools:
        register_page_tools(mcp, client, readonly=readonly)
    if "tags" in tools:
        register_tag_tools(mcp, client, readonly=readonly)
    if "images" in tools:
        register_image_tools(mcp, client, readonly=readonly)

    return mcp
