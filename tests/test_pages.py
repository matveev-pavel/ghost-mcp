"""Tests for Ghost page tools."""

import respx

from tests.conftest import BASE_API


@respx.mock
async def test_list_pages(tools):
    respx.get(f"{BASE_API}/pages/").respond(json={
        "pages": [
            {
                "id": "pg1",
                "title": "About",
                "slug": "about",
                "status": "published",
            }
        ],
        "meta": {"pagination": {"total": 1}},
    })

    result = await tools["ghost_list_pages"]()
    assert "Found pages: 1" in result
    assert "About" in result
    assert "pg1" in result


@respx.mock
async def test_list_pages_with_status_filter(tools):
    respx.get(f"{BASE_API}/pages/").respond(json={
        "pages": [],
        "meta": {"pagination": {"total": 0}},
    })

    result = await tools["ghost_list_pages"](status="draft")
    assert "Found pages: 0" in result

    request = respx.calls[0].request
    assert "status%3Adraft" in str(request.url)


@respx.mock
async def test_get_page_by_id(tools):
    respx.get(f"{BASE_API}/pages/pg1/").respond(json={
        "pages": [{
            "id": "pg1",
            "title": "About Us",
            "slug": "about-us",
            "status": "published",
            "url": "http://test.ghost.io/about-us/",
            "html": "<p>We are great</p>",
        }],
    })

    result = await tools["ghost_get_page"](id="pg1")
    assert "About Us" in result
    assert "published" in result
    assert "<p>We are great</p>" in result


@respx.mock
async def test_get_page_by_slug(tools):
    respx.get(f"{BASE_API}/pages/slug/contact/").respond(json={
        "pages": [{
            "id": "pg2",
            "title": "Contact",
            "slug": "contact",
            "status": "draft",
            "url": "/contact/",
        }],
    })

    result = await tools["ghost_get_page"](slug="contact")
    assert "Contact" in result
    assert "draft" in result


async def test_get_page_no_params(tools):
    result = await tools["ghost_get_page"]()
    assert "Error" in result


@respx.mock
async def test_create_page(tools):
    respx.post(f"{BASE_API}/pages/").respond(json={
        "pages": [{"id": "pg3", "slug": "new-page", "status": "draft"}],
    })

    result = await tools["ghost_create_page"](
        title="New Page",
        markdown_content="# Welcome\n\nHello",
        tags=["info"],
        slug="new-page",
    )
    assert "Page created" in result
    assert "pg3" in result

    request = respx.calls[0].request
    assert "source=html" in str(request.url)


@respx.mock
async def test_create_page_published(tools):
    respx.post(f"{BASE_API}/pages/").respond(json={
        "pages": [{"id": "pg4", "slug": "pub", "status": "published"}],
    })

    result = await tools["ghost_create_page"](
        title="Published Page",
        markdown_content="Content",
        status="published",
    )
    assert "Page created" in result
    assert "published" in result


@respx.mock
async def test_update_page(tools):
    respx.get(f"{BASE_API}/pages/pg1/").respond(json={
        "pages": [{"id": "pg1", "updated_at": "2024-01-01T00:00:00.000Z"}],
    })
    respx.put(f"{BASE_API}/pages/pg1/").respond(json={
        "pages": [{"id": "pg1", "title": "Updated Page"}],
    })

    result = await tools["ghost_update_page"](
        id="pg1",
        title="Updated Page",
        markdown_content="New **content**",
    )
    assert "Page updated" in result
    assert "Updated Page" in result

    put_request = respx.calls[1].request
    assert "source=html" in str(put_request.url)


@respx.mock
async def test_update_page_title_only(tools):
    respx.get(f"{BASE_API}/pages/pg1/").respond(json={
        "pages": [{"id": "pg1", "updated_at": "2024-01-01T00:00:00.000Z"}],
    })
    respx.put(f"{BASE_API}/pages/pg1/").respond(json={
        "pages": [{"id": "pg1", "title": "Just Title"}],
    })

    result = await tools["ghost_update_page"](id="pg1", title="Just Title")
    assert "Page updated" in result

    put_request = respx.calls[1].request
    assert "source=html" not in str(put_request.url)


@respx.mock
async def test_delete_page(tools):
    respx.delete(f"{BASE_API}/pages/pg1/").respond(status_code=204)

    result = await tools["ghost_delete_page"](id="pg1")
    assert "pg1" in result
    assert "deleted" in result
