"""Tests for Ghost post tools."""

import respx

from tests.conftest import BASE_API


@respx.mock
async def test_list_posts(tools):
    respx.get(f"{BASE_API}/posts/").respond(json={
        "posts": [
            {
                "id": "p1",
                "title": "First Post",
                "slug": "first-post",
                "status": "published",
                "published_at": "2024-01-01T00:00:00.000Z",
                "tags": [{"name": "tech"}],
            }
        ],
        "meta": {"pagination": {"total": 1, "page": 1, "pages": 1}},
    })

    result = await tools["ghost_list_posts"]()
    assert "Found posts: 1" in result
    assert "First Post" in result
    assert "p1" in result
    assert "tech" in result


@respx.mock
async def test_list_posts_with_filters(tools):
    respx.get(f"{BASE_API}/posts/").respond(json={
        "posts": [],
        "meta": {"pagination": {"total": 0, "page": 1, "pages": 1}},
    })

    result = await tools["ghost_list_posts"](status="draft", tag="news", limit=5, page=2)
    assert "Found posts: 0" in result

    request = respx.calls[0].request
    assert "status%3Adraft" in str(request.url)
    assert "tag%3Anews" in str(request.url)


@respx.mock
async def test_get_post_by_id(tools):
    respx.get(f"{BASE_API}/posts/p1/").respond(json={
        "posts": [{
            "id": "p1",
            "title": "My Post",
            "slug": "my-post",
            "status": "published",
            "tags": [{"name": "ai"}],
            "authors": [{"name": "Pavel"}],
            "custom_excerpt": "About AI",
            "url": "http://test.ghost.io/my-post/",
            "published_at": "2024-01-01",
            "updated_at": "2024-01-02",
            "html": "<p>Content</p>",
        }],
    })

    result = await tools["ghost_get_post"](id="p1")
    assert "My Post" in result
    assert "ai" in result
    assert "Pavel" in result
    assert "About AI" in result
    assert "<p>Content</p>" in result


@respx.mock
async def test_get_post_by_slug(tools):
    respx.get(f"{BASE_API}/posts/slug/my-post/").respond(json={
        "posts": [{
            "id": "p1",
            "title": "My Post",
            "slug": "my-post",
            "status": "draft",
            "tags": [],
            "authors": [],
            "url": "/my-post/",
            "published_at": None,
            "updated_at": "2024-01-02",
        }],
    })

    result = await tools["ghost_get_post"](slug="my-post")
    assert "My Post" in result
    assert "draft" in result


async def test_get_post_no_params(tools):
    result = await tools["ghost_get_post"]()
    assert "Error" in result


@respx.mock
async def test_create_post(tools):
    respx.post(f"{BASE_API}/posts/").respond(json={
        "posts": [{
            "id": "new1",
            "slug": "new-post",
            "status": "draft",
            "url": "/new-post/",
        }],
    })

    result = await tools["ghost_create_post"](
        title="New Post",
        markdown_content="# Hello\n\nWorld",
        tags=["tech", "ai"],
        excerpt="A new post",
        slug="new-post",
        meta_description="SEO desc",
        featured_image_url="http://img.com/pic.jpg",
    )

    assert "Post created" in result
    assert "new1" in result
    assert "new-post" in result

    request = respx.calls[0].request
    assert "source=html" in str(request.url)


@respx.mock
async def test_create_post_minimal(tools):
    respx.post(f"{BASE_API}/posts/").respond(json={
        "posts": [{"id": "new2", "slug": "min", "status": "draft", "url": "/min/"}],
    })

    result = await tools["ghost_create_post"](
        title="Minimal",
        markdown_content="Content",
    )
    assert "Post created" in result
    assert "new2" in result


@respx.mock
async def test_update_post(tools):
    respx.get(f"{BASE_API}/posts/p1/").respond(json={
        "posts": [{"id": "p1", "updated_at": "2024-01-01T00:00:00.000Z"}],
    })
    respx.put(f"{BASE_API}/posts/p1/").respond(json={
        "posts": [{"id": "p1", "title": "Updated Title", "status": "draft"}],
    })

    result = await tools["ghost_update_post"](
        id="p1",
        title="Updated Title",
        markdown_content="New **content**",
    )
    assert "Post updated" in result
    assert "Updated Title" in result

    put_request = respx.calls[1].request
    assert "source=html" in str(put_request.url)


@respx.mock
async def test_update_post_without_content(tools):
    respx.get(f"{BASE_API}/posts/p1/").respond(json={
        "posts": [{"id": "p1", "updated_at": "2024-01-01T00:00:00.000Z"}],
    })
    respx.put(f"{BASE_API}/posts/p1/").respond(json={
        "posts": [{"id": "p1", "title": "New Title", "status": "published"}],
    })

    result = await tools["ghost_update_post"](id="p1", title="New Title")
    assert "Post updated" in result

    put_request = respx.calls[1].request
    assert "source=html" not in str(put_request.url)


@respx.mock
async def test_delete_post(tools):
    respx.delete(f"{BASE_API}/posts/p1/").respond(status_code=204)

    result = await tools["ghost_delete_post"](id="p1")
    assert "p1" in result
    assert "deleted" in result


@respx.mock
async def test_publish_post(tools):
    respx.get(f"{BASE_API}/posts/p1/").respond(json={
        "posts": [{"id": "p1", "status": "draft", "updated_at": "2024-01-01T00:00:00.000Z"}],
    })
    respx.put(f"{BASE_API}/posts/p1/").respond(json={
        "posts": [{"id": "p1", "url": "http://test.ghost.io/post/"}],
    })

    result = await tools["ghost_publish_post"](id="p1")
    assert "published" in result
    assert "p1" in result


@respx.mock
async def test_publish_already_published(tools):
    respx.get(f"{BASE_API}/posts/p1/").respond(json={
        "posts": [{"id": "p1", "status": "published", "updated_at": "2024-01-01"}],
    })

    result = await tools["ghost_publish_post"](id="p1")
    assert "already published" in result


@respx.mock
async def test_unpublish_post(tools):
    respx.get(f"{BASE_API}/posts/p1/").respond(json={
        "posts": [{"id": "p1", "status": "published", "updated_at": "2024-01-01T00:00:00.000Z"}],
    })
    respx.put(f"{BASE_API}/posts/p1/").respond(json={
        "posts": [{"id": "p1", "status": "draft"}],
    })

    result = await tools["ghost_unpublish_post"](id="p1")
    assert "unpublished" in result
    assert "draft" in result


@respx.mock
async def test_unpublish_already_draft(tools):
    respx.get(f"{BASE_API}/posts/p1/").respond(json={
        "posts": [{"id": "p1", "status": "draft", "updated_at": "2024-01-01"}],
    })

    result = await tools["ghost_unpublish_post"](id="p1")
    assert "already a draft" in result
