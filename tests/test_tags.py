"""Tests for Ghost tag tools."""

import respx

from tests.conftest import BASE_API


@respx.mock
async def test_list_tags(tools):
    respx.get(f"{BASE_API}/tags/").respond(json={
        "tags": [
            {"id": "t1", "name": "Tech", "slug": "tech", "count": {"posts": 5}},
            {"id": "t2", "name": "AI", "slug": "ai", "count": {"posts": 3}},
        ],
    })

    result = await tools["ghost_list_tags"]()
    assert "Found tags: 2" in result
    assert "Tech" in result
    assert "AI" in result
    assert "posts: 5" in result
    assert "posts: 3" in result


@respx.mock
async def test_list_tags_custom_limit(tools):
    respx.get(f"{BASE_API}/tags/").respond(json={"tags": []})

    await tools["ghost_list_tags"](limit=10)
    request = respx.calls[0].request
    assert "limit=10" in str(request.url)


@respx.mock
async def test_list_tags_limit_capped(tools):
    respx.get(f"{BASE_API}/tags/").respond(json={"tags": []})

    await tools["ghost_list_tags"](limit=100)
    request = respx.calls[0].request
    assert "limit=50" in str(request.url)


@respx.mock
async def test_create_tag(tools):
    respx.post(f"{BASE_API}/tags/").respond(json={
        "tags": [{"id": "t3", "name": "New Tag", "slug": "new-tag"}],
    })

    result = await tools["ghost_create_tag"](
        name="New Tag",
        description="A new tag",
        slug="new-tag",
    )
    assert "Tag created" in result
    assert "t3" in result
    assert "New Tag" in result
    assert "new-tag" in result


@respx.mock
async def test_create_tag_minimal(tools):
    respx.post(f"{BASE_API}/tags/").respond(json={
        "tags": [{"id": "t4", "name": "Simple", "slug": "simple"}],
    })

    result = await tools["ghost_create_tag"](name="Simple")
    assert "Tag created" in result
    assert "Simple" in result


@respx.mock
async def test_delete_tag(tools):
    respx.delete(f"{BASE_API}/tags/t1/").respond(status_code=204)

    result = await tools["ghost_delete_tag"](id="t1")
    assert "t1" in result
    assert "deleted" in result
