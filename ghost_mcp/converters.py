"""Markdown to HTML conversion for Ghost API."""

import markdown


def markdown_to_html(md_content: str) -> str:
    """Convert Markdown content to HTML.

    Ghost API accepts HTML via ?source=html parameter
    and automatically converts it to Lexical format.
    """
    return markdown.markdown(
        md_content,
        extensions=["fenced_code", "tables", "toc"],
    )
