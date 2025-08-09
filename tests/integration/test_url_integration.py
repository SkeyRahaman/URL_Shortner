import pytest
from httpx import AsyncClient
from app.main import app
from config import Config
from app.database.models import DBUrl

@pytest.mark.asyncio
@pytest.mark.usefixtures("setup_async_database", "override_get_db")
class TestUrlsIntegration:
    BASE_URL = app.url_path_for("list_user_urls")

    async def test_create_short_url(self, async_client: AsyncClient, auth_token: str):
        headers = {"Authorization": f"Bearer {auth_token}"}
        payload = {"url": Config.TEST_URL['url'], "description": Config.TEST_URL['description']}
        resp = await async_client.post(f"{TestUrlsIntegration.BASE_URL}/create_short_url", params=payload, headers=headers)
        assert resp.status_code == 201
        data = resp.json()
        assert data["description"] == Config.TEST_URL['description']
        assert "short_url" in data

    async def test_redirect_short_url(self, async_client: AsyncClient, test_url:DBUrl):
        resp = await async_client.get(f"{TestUrlsIntegration.BASE_URL}/{test_url.short_url}", follow_redirects=False)
        assert resp.status_code == 302
        assert resp.headers["location"] == Config.TEST_URL['url']

    async def test_get_short_url_details(self, async_client: AsyncClient, test_url:DBUrl):
        resp = await async_client.get(f"{TestUrlsIntegration.BASE_URL}/{test_url.short_url}/details")
        assert resp.status_code == 200
        data = resp.json()
        assert data["short_url"] == test_url.short_url
        assert data["long_url"] == test_url.long_url

    async def test_list_user_urls(self, async_client: AsyncClient, auth_token: str, test_url: DBUrl):
        headers = {"Authorization": f"Bearer {auth_token}"}
        resp = await async_client.get(TestUrlsIntegration.BASE_URL, headers=headers)
        assert resp.status_code == 200
        urls = resp.json()
        assert isinstance(urls, list)
        assert any(u["description"] == test_url.description for u in urls)

    async def test_update_short_url(self, async_client: AsyncClient, auth_token: str, test_url: DBUrl):
        headers = {"Authorization": f"Bearer {auth_token}"}
        url_data = {
            "short_url": test_url.short_url,
            "long_url": "https://example.com/updated",
            "description": "Updated Desc"
        }
        resp = await async_client.put(f"{TestUrlsIntegration.BASE_URL}/{test_url.short_url}", json=url_data, headers=headers)
        assert resp.status_code == 200
        data = resp.json()
        assert data["long_url"] == "https://example.com/updated"
        assert data["description"] == "Updated Desc"

    async def test_delete_short_url(self, async_client: AsyncClient, auth_token: str, test_url: DBUrl):
        headers = {"Authorization": f"Bearer {auth_token}"}
        resp = await async_client.delete(f"{TestUrlsIntegration.BASE_URL}/{test_url.short_url}", headers=headers)
        assert resp.status_code == 200
        assert resp.json()["Message"] == "URL Deleted."

    async def test_delete_short_url_not_found(self, async_client: AsyncClient, auth_token: str):
        headers = {"Authorization": f"Bearer {auth_token}"}
        resp = await async_client.delete(f"{TestUrlsIntegration.BASE_URL}/nonexistent", headers=headers)
        assert resp.status_code == 404
