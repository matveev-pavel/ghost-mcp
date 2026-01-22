"""Tests for GhostClient: JWT, errors, 204."""

import httpx
import pytest
import respx

from ghost_mcp.client import GhostClient, GhostAPIError
from tests.conftest import TEST_URL, TEST_KEY, BASE_API


def test_invalid_key_format():
    with pytest.raises(ValueError, match="Invalid API key format"):
        GhostClient(TEST_URL, "invalid-key-without-colon")


def test_base_url_trailing_slash():
    c = GhostClient(f"{TEST_URL}/", TEST_KEY)
    assert c.base_url == BASE_API


def test_generate_token(client):
    token = client._generate_token()
    assert isinstance(token, str)
    assert len(token) > 0

    import jwt

    decoded = jwt.decode(
        token,
        client.key_secret,
        algorithms=["HS256"],
        audience="/admin/",
    )
    assert "iat" in decoded
    assert "exp" in decoded
    assert decoded["exp"] - decoded["iat"] == 300


def test_headers(client):
    headers = client._headers()
    assert "Authorization" in headers
    assert headers["Authorization"].startswith("Ghost ")
    assert headers["Accept-Version"] == "v5.0"
    assert headers["Content-Type"] == "application/json"


@respx.mock
async def test_get_success(client):
    respx.get(f"{BASE_API}/posts/").respond(
        json={"posts": [{"id": "1", "title": "Test"}]}
    )
    result = await client.get("posts/")
    assert result["posts"][0]["title"] == "Test"


@respx.mock
async def test_post_success(client):
    respx.post(f"{BASE_API}/posts/").respond(
        json={"posts": [{"id": "1", "title": "New"}]}
    )
    result = await client.post("posts/", data={"posts": [{"title": "New"}]})
    assert result["posts"][0]["id"] == "1"


@respx.mock
async def test_put_success(client):
    respx.put(f"{BASE_API}/posts/abc/").respond(
        json={"posts": [{"id": "abc", "title": "Updated"}]}
    )
    result = await client.put("posts/abc/", data={"posts": [{"title": "Updated"}]})
    assert result["posts"][0]["title"] == "Updated"


@respx.mock
async def test_delete_returns_empty_on_204(client):
    respx.delete(f"{BASE_API}/posts/abc/").respond(status_code=204)
    result = await client.delete("posts/abc/")
    assert result == {}


@respx.mock
async def test_api_error_with_json_body(client):
    respx.get(f"{BASE_API}/posts/bad/").respond(
        status_code=404,
        json={"errors": [{"message": "Post not found"}]},
    )
    with pytest.raises(GhostAPIError) as exc_info:
        await client.get("posts/bad/")
    assert exc_info.value.status_code == 404
    assert "Post not found" in exc_info.value.message


@respx.mock
async def test_api_error_with_plain_text(client):
    respx.get(f"{BASE_API}/posts/bad/").respond(
        status_code=500,
        text="Internal Server Error",
    )
    with pytest.raises(GhostAPIError) as exc_info:
        await client.get("posts/bad/")
    assert exc_info.value.status_code == 500
    assert "Internal Server Error" in exc_info.value.message


@respx.mock
async def test_post_with_files(client):
    respx.post(f"{BASE_API}/images/upload/").respond(
        json={"images": [{"url": "http://test.ghost.io/img.png"}]}
    )
    result = await client.post(
        "images/upload/", files={"file": ("img.png", b"data", "image/png")}
    )
    assert result["images"][0]["url"] == "http://test.ghost.io/img.png"
