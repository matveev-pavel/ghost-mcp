"""Entry point for Ghost MCP server."""

import argparse
import os
import sys

from ghost_mcp.server import create_server


def main():
    parser = argparse.ArgumentParser(description="Ghost MCP Server")
    parser.add_argument("--url", help="Ghost blog URL (or env GHOST_URL)")
    parser.add_argument("--key", help="Admin API key id:secret (or env GHOST_ADMIN_KEY)")

    args = parser.parse_args()

    url = args.url or os.environ.get("GHOST_URL")
    key = args.key or os.environ.get("GHOST_ADMIN_KEY")

    if not url:
        print("Error: provide URL via --url or GHOST_URL env variable", file=sys.stderr)
        sys.exit(1)
    if not key:
        print("Error: provide key via --key or GHOST_ADMIN_KEY env variable", file=sys.stderr)
        sys.exit(1)

    mcp = create_server(url, key)
    mcp.run()


if __name__ == "__main__":
    main()
