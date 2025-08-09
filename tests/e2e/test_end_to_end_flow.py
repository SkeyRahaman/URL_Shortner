import pytest
import pytest_asyncio
from httpx import AsyncClient
from app.main import app

USER_PAYLOAD = {
    "email": "e2e_user@example.com",
    "password": "e2e_password",
    "user_name": "e2e_user"
}
UPDATED_USER_PAYLOAD = {
    "email": "updated_e2e_user_new@example.com",
    "password": "newpass123"
}
URL_PAYLOAD = {
    "url": "https://example.com/e2e-test",
    "description": "E2E test link"
}
UPDATED_URL_PAYLOAD = {
    "long_url": "https://example.com/e2e-updated",
    "description": "Updated E2E test"
}
@pytest.mark.asyncio
class TestEndToEndFlow:

    async def test_full_user_url_flow(self, async_client: AsyncClient, override_get_db):
        # 1. Create user
        res = await async_client.post(app.url_path_for("create_user"), json=USER_PAYLOAD)
        assert res.status_code in (201, 409)

        # 2. Login to get auth token
        login_data = {
            "username": USER_PAYLOAD["user_name"],  
            "password": USER_PAYLOAD["password"]
        }
        res = await async_client.post(app.url_path_for("token"), data=login_data)
        assert res.status_code == 200
        token = res.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}

        # 3. Get current user
        res = await async_client.get(app.url_path_for("get_current_user"), headers=headers)
        assert res.status_code == 200
        assert res.json()["user_name"] == USER_PAYLOAD["user_name"]

        # 4. Update current user email
        res = await async_client.put(app.url_path_for("update_current_user"), headers=headers, params=UPDATED_USER_PAYLOAD)
        assert res.status_code == 200
        assert res.json()["email"] == UPDATED_USER_PAYLOAD["email"]

        # 5. Create short URL
        res = await async_client.post(app.url_path_for("create_short_url"), params=URL_PAYLOAD, headers=headers)
        assert res.status_code == 201
        short_url = res.json()["short_url"]
        assert short_url

        # 6. Get short URL details
        url = app.url_path_for("get_short_url_details", short_url=short_url)
        res = await async_client.get(url, headers=headers)
        assert res.status_code == 200
        assert res.json()["long_url"] == URL_PAYLOAD["url"]

        # 7. Redirect short URL (expect 302 redirect)
        url = app.url_path_for("redirect_short_url", short_url=short_url)
        res = await async_client.get(url, follow_redirects=False)
        assert res.status_code == 302
        assert "location" in res.headers
        assert res.headers["location"] == URL_PAYLOAD["url"]

        # 8. List user URLs
        res = await async_client.get(app.url_path_for("list_user_urls"), headers=headers)
        assert res.status_code == 200
        urls = res.json()
        assert isinstance(urls, list)
        assert any(u["short_url"] == short_url for u in urls)

        # 9. Update short URL details
        updated_url_data = UPDATED_URL_PAYLOAD.copy()
        updated_url_data["short_url"] = short_url
        url = app.url_path_for("update_short_url", short_url=short_url)
        res = await async_client.put(url, json=updated_url_data, headers=headers)
        assert res.status_code == 200
        assert res.json()["long_url"] == UPDATED_URL_PAYLOAD["long_url"]
        assert res.json()["description"] == UPDATED_URL_PAYLOAD["description"]

        # 10. Delete short URL
        url = app.url_path_for("delete_short_url", short_url=short_url)
        res = await async_client.delete(url, headers=headers)
        assert res.status_code == 200
        assert "deleted" in res.json()["Message"].lower()

        # 11. Delete user
        url = app.url_path_for("delete_current_user")
        res = await async_client.delete(url, headers=headers)
        assert res.status_code == 200
        assert "deleted" in res.json()["Message"].lower()

        # 12. Attempt to delete user again (should fail with 404 or 401)
        res = await async_client.delete(url, headers=headers)
        assert res.status_code in (401, 404)
