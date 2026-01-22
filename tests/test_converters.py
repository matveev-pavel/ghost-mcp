"""Tests for Markdown to HTML conversion."""

from ghost_mcp.converters import markdown_to_html


def test_basic_paragraph():
    result = markdown_to_html("Hello world")
    assert "<p>Hello world</p>" in result


def test_heading():
    result = markdown_to_html("# Title")
    assert "<h1" in result
    assert "Title</h1>" in result


def test_bold_and_italic():
    result = markdown_to_html("**bold** and *italic*")
    assert "<strong>bold</strong>" in result
    assert "<em>italic</em>" in result


def test_fenced_code_block():
    md = "```python\nprint('hi')\n```"
    result = markdown_to_html(md)
    assert "<code" in result
    assert "print('hi')" in result


def test_table():
    md = "| A | B |\n|---|---|\n| 1 | 2 |"
    result = markdown_to_html(md)
    assert "<table>" in result
    assert "<td>1</td>" in result


def test_link():
    result = markdown_to_html("[click](http://example.com)")
    assert '<a href="http://example.com">click</a>' in result


def test_unordered_list():
    md = "- one\n- two\n- three"
    result = markdown_to_html(md)
    assert "<ul>" in result
    assert "<li>one</li>" in result


def test_empty_content():
    result = markdown_to_html("")
    assert result == ""


def test_multiline_content():
    md = "First paragraph.\n\nSecond paragraph."
    result = markdown_to_html(md)
    assert "<p>First paragraph.</p>" in result
    assert "<p>Second paragraph.</p>" in result
