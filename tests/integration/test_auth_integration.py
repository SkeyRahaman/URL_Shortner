import pytest
from jose import jwt
from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.authentication.dependencies import get_current_user
from config import Config


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
