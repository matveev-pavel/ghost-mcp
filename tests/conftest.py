"""Fixtures for Ghost MCP tests."""

import pytest

from ghost_mcp.client import GhostClient
from ghost_mcp.tools.posts import register_post_tools
from ghost_mcp.tools.pages import register_page_tools
from ghost_mcp.tools.tags import register_tag_tools
from ghost_mcp.tools.images import register_image_tools

TEST_URL = "http://test.ghost.io"
TEST_KEY = "testid1234567890:aabbccddee112233445566778899aabb"
BASE_API = f"{TEST_URL}/ghost/api/admin"


@pytest.fixture
def client():
    """GhostClient with test URL and key."""
    return GhostClient(TEST_URL, TEST_KEY)


@pytest.fixture
def tools(client):
    """Registered tool functions."""
    from mcp.server.fastmcp import FastMCP

    mcp = FastMCP("test")
    register_post_tools(mcp, client)
    register_page_tools(mcp, client)
    register_tag_tools(mcp, client)
    register_image_tools(mcp, client)

    tool_fns = {}
    for name, tool in mcp._tool_manager._tools.items():
        tool_fns[name] = tool.fn
    return tool_fns
