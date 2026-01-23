"""MCP tools for managing Ghost tags."""

from mcp.server.fastmcp import FastMCP

from ghost_mcp.client import GhostClient


def register_tag_tools(mcp: FastMCP, client: GhostClient, readonly: bool = False):
    """Register tools for working with tags."""

    @mcp.tool()
    async def ghost_list_tags(limit: int = 50) -> str:
        """List all tags.

        Args:
            limit: Maximum number of tags to return
        """
        params = {"limit": min(limit, 50), "include": "count.posts"}
        result = await client.get("tags/", params=params)
        tags = result.get("tags", [])

        lines = [f"Found tags: {len(tags)}"]
        for t in tags:
            count = t.get("count", {}).get("posts", 0)
            lines.append(f"- {t['name']} (slug: {t['slug']}, posts: {count}, id: {t['id']})")

        return "\n".join(lines)

    if readonly:
        return

    @mcp.tool()
    async def ghost_create_tag(
        name: str,
        description: str | None = None,
        slug: str | None = None,
    ) -> str:
        """Create a new tag.

        Args:
            name: Tag name
            description: Tag description
            slug: URL slug
        """
        tag_data: dict = {"name": name}
        if description:
            tag_data["description"] = description
        if slug:
            tag_data["slug"] = slug

        result = await client.post("tags/", data={"tags": [tag_data]})
        tag = result["tags"][0]

        return f"Tag created!\nID: {tag['id']}\nName: {tag['name']}\nSlug: {tag['slug']}"

    @mcp.tool()
    async def ghost_delete_tag(id: str) -> str:
        """Delete a tag by ID.

        Args:
            id: Tag ID
        """
        await client.delete(f"tags/{id}/")
        return f"Tag {id} deleted."
