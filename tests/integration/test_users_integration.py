import pytest
from httpx import AsyncClient
from app.database.models import DBUser
from app.main import app

@pytest.mark.asyncio
@pytest.mark.usefixtures("setup_async_database", "override_get_db")
class TestUsersIntegration:
    USERS_URL = app.url_path_for("create_user")

    async def test_create_new_user(self, async_client: AsyncClient):
        payload = {
            "user_name": "newuser",
            "email": "newuser@example.com",
            "password": "secret123"
        }

        resp = await async_client.post(f"{TestUsersIntegration.USERS_URL}", json=payload)
        assert resp.status_code == 201
        data = resp.json()
        assert data["user_name"] == payload["user_name"]
        assert data["email"] == payload["email"]

    async def test_get_current_user(self, async_client: AsyncClient, auth_token: str, test_user: DBUser):
        headers = {"Authorization": f"Bearer {auth_token}"}

        resp = await async_client.get(f"{TestUsersIntegration.USERS_URL}/me", headers=headers)
        assert resp.status_code == 200
        data = resp.json()
        assert data["user_name"] == test_user.user_name
        assert data["email"] == test_user.email

    async def test_update_current_user(self, async_client: AsyncClient, auth_token: str, test_user: DBUser):
        headers = {"Authorization": f"Bearer {auth_token}"}
        params = {"email": "updated@example.com"}

        resp = await async_client.put(f"{TestUsersIntegration.USERS_URL}/me", params=params, headers=headers)
        assert resp.status_code == 200
        assert resp.json()["user_name"] == test_user.user_name
        assert resp.json()["email"] == "updated@example.com"

    async def test_delete_current_user(self, async_client: AsyncClient, auth_token: str):
        headers = {"Authorization": f"Bearer {auth_token}"}

        resp = await async_client.delete(f"{TestUsersIntegration.USERS_URL}/me", headers=headers)
        assert resp.status_code == 200
        assert resp.json()["Message"] == "User Deleted."

    async def test_delete_current_user_not_found(self, async_client: AsyncClient, auth_token: str):
        headers = {"Authorization": f"Bearer {auth_token}"}
        # Delete again immediately after deletion
        resp = await async_client.delete(f"{TestUsersIntegration.USERS_URL}/me", headers=headers)
        resp = await async_client.delete(f"{TestUsersIntegration.USERS_URL}/me", headers=headers)
        assert resp.status_code == 401
