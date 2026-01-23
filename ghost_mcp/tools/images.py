"""MCP tools for Ghost image upload and site utilities."""

from pathlib import Path

from mcp.server.fastmcp import FastMCP

from ghost_mcp.client import GhostClient

ALLOWED_EXTENSIONS = {".jpg", ".jpeg", ".png", ".gif", ".webp", ".svg", ".ico"}
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10 MB


def register_image_tools(mcp: FastMCP, client: GhostClient, readonly: bool = False):
    """Register tools for images and site utilities."""

    if not readonly:

        @mcp.tool()
        async def ghost_upload_image(file_path: str) -> str:
            """Upload an image to Ghost and get its URL.

            Args:
                file_path: Absolute path to the image file
            """
            path = Path(file_path).resolve()

            if not path.exists():
                return "Error: file not found"

            if path.suffix.lower() not in ALLOWED_EXTENSIONS:
                return f"Error: unsupported file type '{path.suffix}'. Allowed: {', '.join(sorted(ALLOWED_EXTENSIONS))}"

            file_size = path.stat().st_size
            if file_size > MAX_FILE_SIZE:
                return f"Error: file too large ({file_size // 1024 // 1024}MB). Maximum: {MAX_FILE_SIZE // 1024 // 1024}MB"

            import mimetypes
            mime_type, _ = mimetypes.guess_type(str(path))
            if not mime_type:
                mime_type = "application/octet-stream"

            with path.open("rb") as f:
                files = {"file": (path.name, f.read(), mime_type)}

            result = await client.post("images/upload/", files=files)
            image_url = result["images"][0]["url"]

            return f"Image uploaded!\nURL: {image_url}"

    @mcp.tool()
    async def ghost_site_info() -> str:
        """Get Ghost site information (title, URL, version)."""
        result = await client.get("site/")
        site = result.get("site", {})

        lines = [
            f"Title: {site.get('title', 'n/a')}",
            f"Description: {site.get('description', 'n/a')}",
            f"URL: {site.get('url', 'n/a')}",
            f"Ghost version: {site.get('version', 'n/a')}",
            f"Locale: {site.get('locale', 'n/a')}",
        ]

        return "\n".join(lines)
