"""Entry point for Ghost MCP server."""

import argparse
import os
import sys

from ghost_mcp.server import create_server, resolve_config


def main():
    parser = argparse.ArgumentParser(description="Ghost CMS MCP Server")
    parser.add_argument("--url", help="Ghost blog URL (or env GHOST_URL)")
    parser.add_argument("--key", help="Admin API key id:secret (or env GHOST_ADMIN_KEY)")
    parser.add_argument("--tools", help="Tool groups to enable: posts,pages,tags,images (or env GHOST_TOOLS)")
    parser.add_argument("--preset", help="Preset: all, writer, content, readonly (or env GHOST_PRESET)")

    args = parser.parse_args()

    url = args.url or os.environ.get("GHOST_URL")
    key = args.key or os.environ.get("GHOST_ADMIN_KEY")
    tools_arg = args.tools or os.environ.get("GHOST_TOOLS")
    preset_arg = args.preset or os.environ.get("GHOST_PRESET")

    if not url:
        print("Error: provide URL via --url or GHOST_URL env variable", file=sys.stderr)
        sys.exit(1)
    if not key:
        print("Error: provide key via --key or GHOST_ADMIN_KEY env variable", file=sys.stderr)
        sys.exit(1)

    try:
        tools, readonly = resolve_config(tools_arg, preset_arg)
    except ValueError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)

    mcp = create_server(url, key, tools=tools, readonly=readonly)
    mcp.run()


if __name__ == "__main__":
    main()
