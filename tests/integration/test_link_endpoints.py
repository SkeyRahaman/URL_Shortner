import pytest

@pytest.mark.asyncio
async def test_create_link(async_client):
    response = await async_client.post(
        "/links",
        json={"original_url": "https://test.com"},
        headers={"X-User-Id": "1"}
    )
    assert response.status_code == 201
    data = response.json()
    assert data["original_url"] == "https://test.com"
    assert data["created_by"] == 1

@pytest.mark.asyncio
async def test_create_link_no_auth(async_client):
    response = await async_client.post(
        "/links",
        json={"original_url": "https://test.com"}
    )
    assert response.status_code == 422

@pytest.mark.asyncio
async def test_list_links(async_client, test_link):
    response = await async_client.get("/links", headers={"X-User-Id": "1"})
    assert response.status_code == 200
    data = response.json()
    assert len(data) >= 1

@pytest.mark.asyncio
async def test_get_link_details(async_client, test_link):
    response = await async_client.get(f"/links/{test_link.slug}/details")
    assert response.status_code == 200
    assert response.json()["slug"] == test_link.slug

@pytest.mark.asyncio
async def test_redirect_link(async_client, test_link):
    response = await async_client.get(f"/links/{test_link.slug}", follow_redirects=False)
    assert response.status_code == 302
    assert response.headers["location"] == test_link.original_url

@pytest.mark.asyncio
async def test_update_link(async_client, test_link):
    response = await async_client.put(
        f"/links/{test_link.slug}",
        json={"description": "Updated"},
        headers={"X-User-Id": "1"}
    )
    assert response.status_code == 200
    assert response.json()["description"] == "Updated"

@pytest.mark.asyncio
async def test_deactivate_link(async_client, test_link):
    response = await async_client.patch(
        f"/links/{test_link.slug}/deactivate",
        headers={"X-User-Id": "1"}
    )
    assert response.status_code == 200
    assert response.json()["is_active"] is False

    # Check redirect fails
    redirect = await async_client.get(f"/links/{test_link.slug}")
    assert redirect.status_code == 410

@pytest.mark.asyncio
async def test_delete_link(async_client, test_link):
    response = await async_client.delete(
        f"/links/{test_link.slug}",
        headers={"X-User-Id": "1"}
    )
    assert response.status_code == 200
