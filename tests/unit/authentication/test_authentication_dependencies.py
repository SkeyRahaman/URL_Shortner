import pytest
from unittest.mock import AsyncMock, patch
from fastapi import HTTPException, status
from jose import jwt
from unittest.mock import MagicMock
from app.authentication.authentication import JWTTokenManager
from app.database import db_user
from app.authentication.dependencies import get_current_user

@pytest.mark.asyncio
class TestGetCurrentUser:
    async def test_get_current_user_success(self, mock_db, test_token, test_username):
        test_user_obj = MagicMock()

        with patch.object(JWTTokenManager, "decode_access_token", return_value={"sub": test_username}) as mock_decode, \
             patch.object(db_user, "get_user", new_callable=AsyncMock) as mock_get_user:

            mock_get_user.return_value = test_user_obj

            user = await get_current_user(token=test_token, db=mock_db)

            assert user == test_user_obj
            mock_decode.assert_called_once_with(test_token)
            mock_get_user.assert_awaited_once_with(user_name=test_username, db=mock_db)

    async def test_get_current_user_no_sub_in_token(self, mock_db, test_token):
        with patch.object(JWTTokenManager, "decode_access_token", return_value={}) as mock_decode:
            with pytest.raises(HTTPException) as exc_info:
                await get_current_user(token=test_token, db=mock_db)

            assert exc_info.value.status_code == status.HTTP_401_UNAUTHORIZED
            mock_decode.assert_called_once_with(test_token)

    async def test_get_current_user_decode_failure(self, mock_db, test_token):
        with patch.object(JWTTokenManager, "decode_access_token", side_effect=jwt.JWTError()) as mock_decode:
            with pytest.raises(HTTPException) as exc_info:
                await get_current_user(token=test_token, db=mock_db)

            assert exc_info.value.status_code == status.HTTP_401_UNAUTHORIZED
            mock_decode.assert_called_once_with(test_token)

    async def test_get_current_user_user_not_found(self, mock_db, test_token, test_username):
        with patch.object(JWTTokenManager, "decode_access_token", return_value={"sub": test_username}) as mock_decode, \
             patch.object(db_user, "get_user", new_callable=AsyncMock) as mock_get_user:

            mock_get_user.return_value = None

            with pytest.raises(HTTPException) as exc_info:
                await get_current_user(token=test_token, db=mock_db)

            assert exc_info.value.status_code == status.HTTP_401_UNAUTHORIZED
            mock_decode.assert_called_once_with(test_token)
            mock_get_user.assert_awaited_once_with(user_name=test_username, db=mock_db)
