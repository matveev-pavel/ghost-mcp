# ghost-cms-mcp

> **Unofficial** MCP server for [Ghost CMS](https://ghost.org). Not affiliated with Ghost Foundation.

Manage posts, pages, tags and images through any MCP-compatible client (Claude Code, Claude Desktop, Cursor, OpenCode, etc.).

## Installation

```bash
uvx ghost-cms-mcp
```

Or install with pip:

```bash
pip install ghost-cms-mcp
```

## Configuration

You need a Ghost Admin API key. Get it from your Ghost Admin panel:

1. Go to **Settings → Integrations**
2. Create a new **Custom Integration**
3. Copy the **Admin API Key** (format: `id:secret`)

### Claude Code

```bash
claude mcp add ghost \
  -e GHOST_URL=https://your-blog.com \
  -e GHOST_ADMIN_KEY=your-id:your-secret \
  -- uvx ghost-cms-mcp
```

Or add to your project's `.mcp.json`:

```json
{
  "mcpServers": {
    "ghost": {
      "command": "uvx",
      "args": ["ghost-cms-mcp"],
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
      "args": ["ghost-cms-mcp"],
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
      "args": ["ghost-cms-mcp"],
      "env": {
        "GHOST_URL": "https://your-blog.com",
        "GHOST_ADMIN_KEY": "your-id:your-secret"
      }
    }
  }
}
```

### CLI

```bash
ghost-cms-mcp --url https://your-blog.com --key "your-id:your-secret"
```

Environment variables take priority over CLI arguments.

## Tool Selection

By default all tools are enabled. You can control which tools are available using presets or manual selection.

### Presets

| Preset | Tools | Description |
|--------|-------|-------------|
| `all` | posts, pages, tags, images | All tools (default) |
| `writer` | posts, tags, images | For authors: write, tag, upload images |
| `content` | posts, pages, tags, images | All content tools |
| `readonly` | posts, pages, tags, images | Only list/get operations, no create/update/delete |

Configure via env variable or CLI argument:

```json
{
  "mcpServers": {
    "ghost": {
      "command": "uvx",
      "args": ["ghost-cms-mcp"],
      "env": {
        "GHOST_URL": "https://your-blog.com",
        "GHOST_ADMIN_KEY": "your-id:your-secret",
        "GHOST_PRESET": "writer"
      }
    }
  }
}
```

Or via CLI:

```bash
ghost-cms-mcp --url https://your-blog.com --key "id:secret" --preset readonly
```

### Manual tool selection

Enable only specific tool groups:

```json
{
  "env": {
    "GHOST_URL": "https://your-blog.com",
    "GHOST_ADMIN_KEY": "your-id:your-secret",
    "GHOST_TOOLS": "posts,tags"
  }
}
```

Or via CLI:

```bash
ghost-cms-mcp --url https://your-blog.com --key "id:secret" --tools posts,tags
```

Available groups: `posts`, `pages`, `tags`, `images`

`GHOST_TOOLS` / `--tools` takes priority over `GHOST_PRESET` / `--preset`.

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
git clone https://github.com/matveev-pavel/ghost-mcp.git
cd ghost-mcp
uv sync --dev
uv run pytest
```

## License

MIT
