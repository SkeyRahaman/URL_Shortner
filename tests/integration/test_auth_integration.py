from httpx import AsyncClient
import pytest
from jose import jwt
from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.authentication.dependencies import get_current_user
from app.database.models import DBUser
from config import Config
from app.main import app


@pytest.mark.asyncio
class TestGetCurrentUser:

    async def test_get_current_user_success(self, async_db_session: AsyncSession, auth_token: str):
        user = await get_current_user(token=auth_token, db=async_db_session)
        assert user is not None
        assert user.user_name == Config.TEST_USER['username']

    async def test_get_current_user_invalid_token_raises_exception(self, async_db_session: AsyncSession):
        invalid_token = "invalid.token.signature"
        with pytest.raises(HTTPException) as exc_info:
            await get_current_user(token=invalid_token, db=async_db_session)

        assert exc_info.value.status_code == 401
        assert "Could not validate credentials." in exc_info.value.detail

    async def test_get_current_user_with_missing_sub_field(self, async_db_session: AsyncSession):
        token = jwt.encode({}, Config.SECRET_KEY, algorithm=Config.ALGORITHM)
        with pytest.raises(HTTPException) as exc_info:
            await get_current_user(token=token, db=async_db_session)

        assert exc_info.value.status_code == 401
        assert "Could not validate credentials." in exc_info.value.detail

@pytest.mark.asyncio
class TestGetToken:
    TOKEN_URL = app.url_path_for("token")

    async def test_get_token_success(self, test_user: DBUser, async_client: AsyncClient, override_get_db):
        response = await async_client.post(
            self.TOKEN_URL,
            data={"username": test_user.user_name, "password": Config.TEST_USER['password']}
        )
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"
        assert data["user_name"] == test_user.user_name

    async def test_get_token_invalid_username(self, test_user: DBUser, async_client: AsyncClient, override_get_db):
        response = await async_client.post(
            TestGetToken.TOKEN_URL,
            data={"username": "wronguser", "password": Config.TEST_USER['password']}
        )
        assert response.status_code == 401
        assert response.json()["detail"] == "Invalid Credentials."

    async def test_get_token_wrong_password(self, test_user: DBUser, async_client: AsyncClient, override_get_db):
        response = await async_client.post(
            TestGetToken.TOKEN_URL,
            data={"username": test_user.user_name, "password": "wrong password"}
        )
        assert response.status_code == 401
        assert response.json()["detail"] == "Invalid Credentials."

    async def test_get_token_wrong_credentials(self, async_client: AsyncClient, override_get_db):
        response = await async_client.post(
            TestGetToken.TOKEN_URL,
            data={"username": "wrong password", "password": "wrong password"}
        )
        assert response.status_code == 401
        assert response.json()["detail"] == "Invalid Credentials."
