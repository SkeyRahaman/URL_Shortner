import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from fastapi.exceptions import HTTPException
from fastapi import status

from app.database import db_user as db_user_functions  # adjust import to your actual file
from app.authentication.password_hash import PasswordHasher


@pytest.mark.asyncio
class TestDBUserFunctions:

    async def test_check_email_address_found(self, mock_db, mock_db_user):
        mock_scalar_result = MagicMock()
        mock_scalar_result.first.return_value = mock_db_user

        mock_result = MagicMock()
        mock_result.scalars.return_value = mock_scalar_result

        mock_db.execute = AsyncMock(return_value=mock_result)

        result = await db_user_functions.check_email_address(mock_db, mock_db_user.email)
        assert result is True
        mock_db.execute.assert_awaited_once()

    async def test_check_email_address_not_found(self, mock_db):
        mock_scalar_result = MagicMock()
        mock_scalar_result.first.return_value = None

        mock_result = MagicMock()
        mock_result.scalars.return_value = mock_scalar_result

        mock_db.execute = AsyncMock(return_value=mock_result)

        result = await db_user_functions.check_email_address(mock_db, "noone@example.com")
        assert result is False

    async def test_check_username_exist_found(self, mock_db, mock_db_user):
        mock_scalar_result = MagicMock()
        mock_scalar_result.first.return_value = mock_db_user

        mock_result = MagicMock()
        mock_result.scalars.return_value = mock_scalar_result

        mock_db.execute = AsyncMock(return_value=mock_result)

        result = await db_user_functions.check_username_exist(mock_db, mock_db_user.user_name)
        assert result is True

    async def test_check_username_exist_not_found(self, mock_db):
        mock_scalar_result = MagicMock()
        mock_scalar_result.first.return_value = None

        mock_result = MagicMock()
        mock_result.scalars.return_value = mock_scalar_result

        mock_db.execute = AsyncMock(return_value=mock_result)

        result = await db_user_functions.check_username_exist(mock_db, "nouser")
        assert result is False

    @patch("app.authentication.password_hash.PasswordHasher.get_password_hash", return_value="hashedpass")
    async def test_create_user_success(self, mock_hash, mock_db, fake_user_details):
        mock_db.add = MagicMock()
        mock_db.commit = AsyncMock()
        mock_db.refresh = AsyncMock()
        result = await db_user_functions.create_user(mock_db, fake_user_details)
        mock_hash.assert_called_once_with(fake_user_details.password)
        mock_db.add.assert_called_once()
        mock_db.commit.assert_awaited_once()
        mock_db.refresh.assert_awaited_once()
        assert hasattr(result, "user_name")
        assert result.user_name == fake_user_details.user_name

    @patch("app.authentication.password_hash.PasswordHasher.get_password_hash")
    async def test_update_user_success(self, mock_hash, mock_db_user, mock_db):
        mock_scalar_result = MagicMock()
        mock_scalar_result.first.return_value = mock_db_user

        mock_result = MagicMock()
        mock_result.scalars.return_value = mock_scalar_result
        mock_db.execute = AsyncMock(return_value=mock_result)
        mock_db.commit = AsyncMock()
        mock_db.refresh = AsyncMock()

        new_email = "newemail@example.com"
        new_password = "newpass"
        mock_hash.return_value = "hashednewpass"

        updated_user = await db_user_functions.update_user(mock_db, mock_db_user, new_email, new_password)

        assert updated_user.email == new_email
        assert updated_user.password == "hashednewpass"
        mock_db.commit.assert_awaited()
        mock_db.refresh.assert_awaited()
        mock_hash.assert_called_once_with(new_password)

    async def test_update_user_not_found(self, mock_db, mock_db_user):
        mock_scalar_result = MagicMock()
        mock_scalar_result.first.return_value = None

        mock_result = MagicMock()
        mock_result.scalars.return_value = mock_scalar_result
        mock_db.execute = AsyncMock(return_value=mock_result)

        user = await db_user_functions.update_user(mock_db, mock_db_user, "email@example.com", "somepass")
        assert user is None

    async def test_delete_user_success(self, mock_db, mock_db_user):
        mock_scalar_result = MagicMock()
        mock_scalar_result.first.return_value = mock_db_user

        mock_result = MagicMock()
        mock_result.scalars.return_value = mock_scalar_result
        mock_db.execute = AsyncMock(return_value=mock_result)

        mock_db.delete = AsyncMock()
        mock_db.commit = AsyncMock()

        response = await db_user_functions.delete_user(mock_db_user, mock_db)
        mock_db.delete.assert_awaited_with(mock_db_user)
        mock_db.commit.assert_awaited()
        assert response is True

    async def test_delete_user_not_found(self, mock_db, mock_db_user):
        mock_scalar_result = MagicMock()
        mock_scalar_result.first.return_value = None

        mock_result = MagicMock()
        mock_result.scalars.return_value = mock_scalar_result
        mock_db.execute = AsyncMock(return_value=mock_result)

        response = await db_user_functions.delete_user(mock_db_user, mock_db)
        assert response is False

    async def test_get_user_found(self, mock_db, mock_db_user):
        mock_scalar_result = MagicMock()
        mock_scalar_result.first.return_value = mock_db_user

        mock_result = MagicMock()
        mock_result.scalars.return_value = mock_scalar_result
        mock_db.execute = AsyncMock(return_value=mock_result)

        user = await db_user_functions.get_user(mock_db_user.user_name, mock_db)
        assert user == mock_db_user

    async def test_get_user_not_found(self, mock_db):
        mock_scalar_result = MagicMock()
        mock_scalar_result.first.return_value = None

        mock_result = MagicMock()
        mock_result.scalars.return_value = mock_scalar_result
        mock_db.execute = AsyncMock(return_value=mock_result)

        user = await db_user_functions.get_user("invaliduser", mock_db)

        assert user is None
