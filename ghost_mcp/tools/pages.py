"""MCP tools for managing Ghost pages."""

from mcp.server.fastmcp import FastMCP

from ghost_mcp.client import GhostClient
from ghost_mcp.converters import markdown_to_html

VALID_STATUSES = {"all", "published", "draft"}


def register_page_tools(mcp: FastMCP, client: GhostClient, readonly: bool = False):
    """Register tools for working with pages."""

    @mcp.tool()
    async def ghost_list_pages(
        status: str = "all",
        limit: int = 15,
        page: int = 1,
    ) -> str:
        """List Ghost pages.

        Args:
            status: Filter by status (all, published, draft)
            limit: Pages per page (max 15)
            page: Page number
        """
        if status not in VALID_STATUSES:
            return f"Error: invalid status '{status}'. Must be one of: {', '.join(sorted(VALID_STATUSES))}"

        params = {
            "limit": min(limit, 15),
            "page": page,
            "include": "tags",
            "fields": "id,title,slug,status,published_at,updated_at",
        }
        if status != "all":
            params["filter"] = f"status:{status}"

        result = await client.get("pages/", params=params)
        pages = result.get("pages", [])
        meta = result.get("meta", {}).get("pagination", {})

        lines = [f"Found pages: {meta.get('total', len(pages))}"]
        for p in pages:
            lines.append(f"\n- [{p['status']}] {p['title']}")
            lines.append(f"  ID: {p['id']} | Slug: {p['slug']}")

        return "\n".join(lines)

    @mcp.tool()
    async def ghost_get_page(
        id: str | None = None,
        slug: str | None = None,
    ) -> str:
        """Get a page by ID or slug.

        Args:
            id: Page ID
            slug: Page slug
        """
        if not id and not slug:
            return "Error: provide either id or slug"

        endpoint = f"pages/{id}/" if id else f"pages/slug/{slug}/"
        params = {"include": "tags", "formats": "html"}
        result = await client.get(endpoint, params=params)
        page = result["pages"][0]

        lines = [
            f"Title: {page['title']}",
            f"ID: {page['id']}",
            f"Slug: {page['slug']}",
            f"Status: {page['status']}",
            f"URL: {page.get('url', 'n/a')}",
        ]
        if page.get("html"):
            lines.append(f"\nHTML content:\n{page['html']}")

        return "\n".join(lines)

    if readonly:
        return

    @mcp.tool()
    async def ghost_create_page(
        title: str,
        markdown_content: str,
        status: str = "draft",
        tags: list[str] | None = None,
        slug: str | None = None,
        meta_title: str | None = None,
        meta_description: str | None = None,
    ) -> str:
        """Create a new Ghost page from Markdown.

        Args:
            title: Page title
            markdown_content: Content in Markdown format
            status: Status (draft, published)
            tags: List of tag names
            slug: URL slug
            meta_title: SEO title (recommended ~60 characters)
            meta_description: SEO description (recommended ~145 characters)
        """
        html = markdown_to_html(markdown_content)
        page_data: dict = {"title": title, "html": html, "status": status}

        if tags:
            page_data["tags"] = [{"name": t} for t in tags]
        if slug:
            page_data["slug"] = slug
        if meta_title:
            page_data["meta_title"] = meta_title
        if meta_description:
            page_data["meta_description"] = meta_description

        result = await client.post("pages/?source=html", data={"pages": [page_data]})
        page = result["pages"][0]

        return f"Page created!\nID: {page['id']}\nSlug: {page['slug']}\nStatus: {page['status']}"

    @mcp.tool()
    async def ghost_update_page(
        id: str,
        title: str | None = None,
        markdown_content: str | None = None,
        tags: list[str] | None = None,
        slug: str | None = None,
        meta_title: str | None = None,
        meta_description: str | None = None,
    ) -> str:
        """Update a page.

        Args:
            id: Page ID (required)
            title: New title
            markdown_content: New content in Markdown
            tags: New tags
            slug: New slug
            meta_title: New SEO title (recommended ~60 characters)
            meta_description: New SEO description (recommended ~145 characters)
        """
        current = await client.get(f"pages/{id}/")
        current_page = current["pages"][0]

        page_data: dict = {"updated_at": current_page["updated_at"]}

        if title:
            page_data["title"] = title
        if markdown_content:
            page_data["html"] = markdown_to_html(markdown_content)
        if tags is not None:
            page_data["tags"] = [{"name": t} for t in tags]
        if slug:
            page_data["slug"] = slug
        if meta_title is not None:
            page_data["meta_title"] = meta_title
        if meta_description is not None:
            page_data["meta_description"] = meta_description

        endpoint = f"pages/{id}/" + ("?source=html" if markdown_content else "")
        result = await client.put(endpoint, data={"pages": [page_data]})
        page = result["pages"][0]

        return f"Page updated!\nID: {page['id']}\nTitle: {page['title']}"

    @mcp.tool()
    async def ghost_delete_page(id: str) -> str:
        """Delete a page by ID.

        Args:
            id: Page ID
        """
        await client.delete(f"pages/{id}/")
        return f"Page {id} deleted."
