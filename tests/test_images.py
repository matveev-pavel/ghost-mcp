"""Tests for Ghost image upload and site info tools."""

import tempfile
from pathlib import Path

import respx

from tests.conftest import BASE_API


@respx.mock
async def test_upload_image(tools, tmp_path):
    image_file = tmp_path / "photo.png"
    image_file.write_bytes(b"\x89PNG\r\n\x1a\n" + b"\x00" * 100)

    respx.post(f"{BASE_API}/images/upload/").respond(json={
        "images": [{"url": "http://test.ghost.io/content/images/photo.png"}],
    })

    result = await tools["ghost_upload_image"](file_path=str(image_file))
    assert "Image uploaded" in result
    assert "http://test.ghost.io/content/images/photo.png" in result


async def test_upload_image_file_not_found(tools):
    result = await tools["ghost_upload_image"](file_path="/nonexistent/file.png")
    assert "Error" in result
    assert "not found" in result


@respx.mock
async def test_upload_image_jpeg(tools, tmp_path):
    image_file = tmp_path / "photo.jpg"
    image_file.write_bytes(b"\xff\xd8\xff" + b"\x00" * 50)

    respx.post(f"{BASE_API}/images/upload/").respond(json={
        "images": [{"url": "http://test.ghost.io/content/images/photo.jpg"}],
    })

    result = await tools["ghost_upload_image"](file_path=str(image_file))
    assert "Image uploaded" in result


@respx.mock
async def test_site_info(tools):
    respx.get(f"{BASE_API}/site/").respond(json={
        "site": {
            "title": "My Ghost Blog",
            "description": "A great blog",
            "url": "http://test.ghost.io",
            "version": "5.80.0",
            "locale": "ru",
        },
    })

    result = await tools["ghost_site_info"]()
    assert "My Ghost Blog" in result
    assert "A great blog" in result
    assert "http://test.ghost.io" in result
    assert "5.80.0" in result
    assert "ru" in result


@respx.mock
async def test_site_info_missing_fields(tools):
    respx.get(f"{BASE_API}/site/").respond(json={"site": {}})

    result = await tools["ghost_site_info"]()
    assert "n/a" in result
