import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from fastapi import HTTPException, status
from app.authentication.auth_router import get_token
from app.database import db_user
from app.authentication.password_hash import PasswordHasher
from app.authentication.authentication import JWTTokenManager

@pytest.mark.asyncio
class TestAuthTokenEndpoint:
    async def test_get_token_success(self, mock_db, valid_form_data):
        # Mock user object returned by db_user.get_user
        mock_user = MagicMock()
        mock_user.user_name = valid_form_data.username
        mock_user.password = "hashed_password"

        with patch.object(db_user, "get_user", new_callable=AsyncMock) as mock_get_user, \
             patch.object(PasswordHasher, "verify_password", return_value=True) as mock_verify_password, \
             patch.object(JWTTokenManager, "create_access_token", return_value="fake.jwt.token") as mock_create_token:

            mock_get_user.return_value = mock_user

            response = await get_token(request=valid_form_data, db=mock_db)

            # Validate output
            assert response["access_token"] == "fake.jwt.token"
            assert response["token_type"] == "bearer"
            assert response["user_name"] == valid_form_data.username

            # Ensure all mocks called as expected
            mock_get_user.assert_awaited_once_with(user_name=valid_form_data.username, db=mock_db)
            mock_verify_password.assert_called_once_with(valid_form_data.password, mock_user.password)
            mock_create_token.assert_called_once_with(data={"sub": valid_form_data.username})

    async def test_get_token_user_not_found(self, mock_db, invalid_form_data):
        with patch.object(db_user, "get_user", new_callable=AsyncMock) as mock_get_user:
            mock_get_user.return_value = None
            with pytest.raises(HTTPException) as exc_info:
                await get_token(request=invalid_form_data, db=mock_db)

            assert exc_info.value.status_code == status.HTTP_401_UNAUTHORIZED
            mock_get_user.assert_awaited_once_with(user_name=invalid_form_data.username, db=mock_db)

    async def test_get_token_invalid_password(self, mock_db, valid_form_data):
        mock_user = MagicMock()
        mock_user.user_name = valid_form_data.username
        mock_user.password = "hashed_password"

        with patch.object(db_user, "get_user", new_callable=AsyncMock) as mock_get_user, \
             patch.object(PasswordHasher, "verify_password", return_value=False) as mock_verify_password:

            mock_get_user.return_value = mock_user

            with pytest.raises(HTTPException) as exc_info:
                await get_token(request=valid_form_data, db=mock_db)

            assert exc_info.value.status_code == status.HTTP_401_UNAUTHORIZED
            mock_get_user.assert_awaited_once_with(user_name=valid_form_data.username, db=mock_db)
            mock_verify_password.assert_called_once_with(valid_form_data.password, mock_user.password)
