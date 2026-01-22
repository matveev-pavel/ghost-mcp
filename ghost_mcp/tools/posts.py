"""MCP tools for managing Ghost posts."""

import re

from mcp.server.fastmcp import FastMCP

from ghost_mcp.client import GhostClient
from ghost_mcp.converters import markdown_to_html

VALID_STATUSES = {"all", "published", "draft", "scheduled"}
TAG_SLUG_RE = re.compile(r"^[a-zA-Z0-9_-]+$")


def register_post_tools(mcp: FastMCP, client: GhostClient):
    """Register tools for working with posts."""

    @mcp.tool()
    async def ghost_list_posts(
        status: str = "all",
        tag: str | None = None,
        limit: int = 15,
        page: int = 1,
    ) -> str:
        """List Ghost posts.

        Args:
            status: Filter by status (all, published, draft, scheduled)
            tag: Filter by tag slug
            limit: Posts per page (max 15)
            page: Page number
        """
        if status not in VALID_STATUSES:
            return f"Error: invalid status '{status}'. Must be one of: {', '.join(sorted(VALID_STATUSES))}"

        params = {
            "limit": min(limit, 15),
            "page": page,
            "include": "tags,authors",
            "fields": "id,title,slug,status,published_at,updated_at,excerpt",
        }
        if status != "all":
            params["filter"] = f"status:{status}"
        if tag:
            if not TAG_SLUG_RE.match(tag):
                return "Error: invalid tag slug. Only alphanumeric, hyphens and underscores allowed."
            existing_filter = params.get("filter", "")
            tag_filter = f"tag:{tag}"
            params["filter"] = f"{existing_filter}+{tag_filter}" if existing_filter else tag_filter

        result = await client.get("posts/", params=params)
        posts = result.get("posts", [])
        meta = result.get("meta", {}).get("pagination", {})

        lines = [f"Found posts: {meta.get('total', len(posts))} (page {meta.get('page', 1)}/{meta.get('pages', 1)})"]
        for p in posts:
            tags = ", ".join(t["name"] for t in p.get("tags", []))
            lines.append(f"\n- [{p['status']}] {p['title']}")
            lines.append(f"  ID: {p['id']} | Slug: {p['slug']}")
            if tags:
                lines.append(f"  Tags: {tags}")
            if p.get("published_at"):
                lines.append(f"  Published: {p['published_at']}")

        return "\n".join(lines)

    @mcp.tool()
    async def ghost_get_post(
        id: str | None = None,
        slug: str | None = None,
    ) -> str:
        """Get a post by ID or slug.

        Args:
            id: Post ID
            slug: Post slug
        """
        if not id and not slug:
            return "Error: provide either id or slug"

        if id:
            endpoint = f"posts/{id}/"
        else:
            endpoint = f"posts/slug/{slug}/"

        params = {"include": "tags,authors", "formats": "html,lexical"}
        result = await client.get(endpoint, params=params)
        post = result["posts"][0]

        tags = ", ".join(t["name"] for t in post.get("tags", []))
        authors = ", ".join(a["name"] for a in post.get("authors", []))

        lines = [
            f"Title: {post['title']}",
            f"ID: {post['id']}",
            f"Slug: {post['slug']}",
            f"Status: {post['status']}",
            f"Tags: {tags or 'n/a'}",
            f"Authors: {authors or 'n/a'}",
            f"Excerpt: {post.get('custom_excerpt') or post.get('excerpt', 'n/a')}",
            f"URL: {post.get('url', 'n/a')}",
            f"Published: {post.get('published_at', 'n/a')}",
            f"Updated: {post.get('updated_at', 'n/a')}",
        ]
        if post.get("html"):
            lines.append(f"\nHTML content:\n{post['html']}")

        return "\n".join(lines)

    @mcp.tool()
    async def ghost_create_post(
        title: str,
        markdown_content: str,
        status: str = "draft",
        tags: list[str] | None = None,
        excerpt: str | None = None,
        slug: str | None = None,
        meta_title: str | None = None,
        meta_description: str | None = None,
        featured_image_url: str | None = None,
    ) -> str:
        """Create a new Ghost post from Markdown.

        Args:
            title: Post title
            markdown_content: Content in Markdown format
            status: Status (draft, published)
            tags: List of tag names
            excerpt: Short description
            slug: URL slug
            meta_title: SEO title (recommended ~60 characters)
            meta_description: SEO description (recommended ~145 characters)
            featured_image_url: Cover image URL
        """
        html = markdown_to_html(markdown_content)

        post_data: dict = {
            "title": title,
            "html": html,
            "status": status,
        }

        if tags:
            post_data["tags"] = [{"name": t} for t in tags]
        if excerpt:
            post_data["custom_excerpt"] = excerpt
        if slug:
            post_data["slug"] = slug
        if meta_title:
            post_data["meta_title"] = meta_title
        if meta_description:
            post_data["meta_description"] = meta_description
        if featured_image_url:
            post_data["feature_image"] = featured_image_url

        result = await client.post("posts/?source=html", data={"posts": [post_data]})
        post = result["posts"][0]

        return f"Post created!\nID: {post['id']}\nSlug: {post['slug']}\nStatus: {post['status']}\nURL: {post.get('url', 'n/a')}"

    @mcp.tool()
    async def ghost_update_post(
        id: str,
        title: str | None = None,
        markdown_content: str | None = None,
        tags: list[str] | None = None,
        excerpt: str | None = None,
        slug: str | None = None,
        meta_title: str | None = None,
        meta_description: str | None = None,
        featured_image_url: str | None = None,
    ) -> str:
        """Update an existing post.

        Args:
            id: Post ID (required)
            title: New title
            markdown_content: New content in Markdown
            tags: New tags
            excerpt: New excerpt
            slug: New slug
            meta_title: New SEO title (recommended ~60 characters)
            meta_description: New SEO description (recommended ~145 characters)
            featured_image_url: New cover image URL
        """
        current = await client.get(f"posts/{id}/")
        current_post = current["posts"][0]

        post_data: dict = {"updated_at": current_post["updated_at"]}

        if title:
            post_data["title"] = title
        if markdown_content:
            post_data["html"] = markdown_to_html(markdown_content)
        if tags is not None:
            post_data["tags"] = [{"name": t} for t in tags]
        if excerpt is not None:
            post_data["custom_excerpt"] = excerpt
        if slug:
            post_data["slug"] = slug
        if meta_title is not None:
            post_data["meta_title"] = meta_title
        if meta_description is not None:
            post_data["meta_description"] = meta_description
        if featured_image_url is not None:
            post_data["feature_image"] = featured_image_url

        endpoint = f"posts/{id}/" + ("?source=html" if markdown_content else "")
        result = await client.put(endpoint, data={"posts": [post_data]})
        post = result["posts"][0]

        return f"Post updated!\nID: {post['id']}\nTitle: {post['title']}\nStatus: {post['status']}"

    @mcp.tool()
    async def ghost_delete_post(id: str) -> str:
        """Delete a post by ID.

        Args:
            id: Post ID
        """
        await client.delete(f"posts/{id}/")
        return f"Post {id} deleted."

    @mcp.tool()
    async def ghost_publish_post(id: str) -> str:
        """Publish a draft post.

        Args:
            id: Post ID
        """
        current = await client.get(f"posts/{id}/")
        current_post = current["posts"][0]

        if current_post["status"] == "published":
            return f"Post {id} is already published."

        post_data = {
            "status": "published",
            "updated_at": current_post["updated_at"],
        }
        result = await client.put(f"posts/{id}/", data={"posts": [post_data]})
        post = result["posts"][0]

        return f"Post published!\nID: {post['id']}\nURL: {post.get('url', 'n/a')}"

    @mcp.tool()
    async def ghost_unpublish_post(id: str) -> str:
        """Unpublish a post (revert to draft).

        Args:
            id: Post ID
        """
        current = await client.get(f"posts/{id}/")
        current_post = current["posts"][0]

        if current_post["status"] == "draft":
            return f"Post {id} is already a draft."

        post_data = {
            "status": "draft",
            "updated_at": current_post["updated_at"],
        }
        result = await client.put(f"posts/{id}/", data={"posts": [post_data]})
        post = result["posts"][0]

        return f"Post unpublished.\nID: {post['id']}\nStatus: draft"
