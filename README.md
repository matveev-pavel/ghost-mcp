# ghost-mcp

> **Unofficial** MCP server for [Ghost CMS](https://ghost.org). Not affiliated with Ghost Foundation.

Manage posts, pages, tags and images through any MCP-compatible client (Claude Code, Claude Desktop, Cursor, OpenCode, etc.).

## Installation

```bash
uvx ghost-mcp
```

Or install with pip:

```bash
pip install ghost-mcp
```

## Configuration

You need a Ghost Admin API key. Get it from your Ghost Admin panel:

1. Go to **Settings → Integrations**
2. Create a new **Custom Integration**
3. Copy the **Admin API Key** (format: `id:secret`)

### Claude Code

Add to your project's `.mcp.json`:

```json
{
  "mcpServers": {
    "ghost": {
      "command": "uvx",
      "args": ["ghost-mcp"],
      "env": {
        "GHOST_URL": "https://your-blog.com",
        "GHOST_ADMIN_KEY": "your-id:your-secret"
      }
    }
  }
}
```

### Claude Desktop

Add to `claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "ghost": {
      "command": "uvx",
      "args": ["ghost-mcp"],
      "env": {
        "GHOST_URL": "https://your-blog.com",
        "GHOST_ADMIN_KEY": "your-id:your-secret"
      }
    }
  }
}
```

### Cursor

Add to `.cursor/mcp.json` in your project root:

```json
{
  "mcpServers": {
    "ghost": {
      "command": "uvx",
      "args": ["ghost-mcp"],
      "env": {
        "GHOST_URL": "https://your-blog.com",
        "GHOST_ADMIN_KEY": "your-id:your-secret"
      }
    }
  }
}
```

### OpenCode

Add to your `opencode.json`:

```json
{
  "mcpServers": {
    "ghost": {
      "command": "uvx",
      "args": ["ghost-mcp"],
      "env": {
        "GHOST_URL": "https://your-blog.com",
        "GHOST_ADMIN_KEY": "your-id:your-secret"
      }
    }
  }
}
```

### CLI (alternative)

```bash
ghost-mcp --url https://your-blog.com --key "your-id:your-secret"
```

Environment variables take priority over CLI arguments.

## Available tools

### Posts
- `ghost_list_posts` — list posts with filtering by status and tag
- `ghost_get_post` — get post by ID or slug
- `ghost_create_post` — create post from Markdown
- `ghost_update_post` — update post fields (title, content, tags, SEO metadata, etc.)
- `ghost_delete_post` — delete post
- `ghost_publish_post` — publish a draft
- `ghost_unpublish_post` — revert to draft

### Pages
- `ghost_list_pages` — list pages
- `ghost_get_page` — get page by ID or slug
- `ghost_create_page` — create page from Markdown
- `ghost_update_page` — update page fields
- `ghost_delete_page` — delete page

### Tags
- `ghost_list_tags` — list all tags
- `ghost_create_tag` — create a new tag
- `ghost_delete_tag` — delete tag

### Images & Site
- `ghost_upload_image` — upload image and get URL
- `ghost_site_info` — get site metadata (title, version, etc.)

## Development

```bash
git clone https://github.com/pmatveev/ghost-mcp.git
cd ghost-mcp
uv sync --dev
uv run pytest
```

## License

MIT
