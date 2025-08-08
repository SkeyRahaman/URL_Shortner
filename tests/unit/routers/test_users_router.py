import pytest
from unittest.mock import patch, AsyncMock
from fastapi.exceptions import HTTPException
from starlette import status

from app.routers import users
from app.database import db_user


@pytest.mark.asyncio
class TestUsersRouter:

    async def test_create_new_user_conflict_email_or_username(self, mock_db, fake_user_details):
        # Patch the check_email_address and check_username_exist to simulate email or username existing
        with patch.object(db_user, "check_email_address", AsyncMock(return_value=True)), \
             patch.object(db_user, "check_username_exist", AsyncMock(return_value=False)):
            with pytest.raises(HTTPException) as exc_info:
                await users.create_new_user(data=fake_user_details, db=mock_db)
            assert exc_info.value.status_code == status.HTTP_409_CONFLICT
            assert "Email already registered" in exc_info.value.detail

        with patch.object(db_user, "check_email_address", AsyncMock(return_value=False)), \
             patch.object(db_user, "check_username_exist", AsyncMock(return_value=True)):
            with pytest.raises(HTTPException) as exc_info:
                await users.create_new_user(data=fake_user_details, db=mock_db)
            assert exc_info.value.status_code == status.HTTP_409_CONFLICT

    async def test_create_new_user_success(self, mock_db, fake_user_details, mock_db_user):
        with patch.object(db_user, "check_email_address", AsyncMock(return_value=False)), \
             patch.object(db_user, "check_username_exist", AsyncMock(return_value=False)), \
             patch.object(db_user, "create_user", AsyncMock(return_value=mock_db_user)) as mock_create_user:
            
            result = await users.create_new_user(data=fake_user_details, db=mock_db)
            
            mock_create_user.assert_awaited_once_with(mock_db, fake_user_details)
            assert result == mock_db_user

    async def test_get_current_user_router(self, mock_db_user):
        # Directly test returning the current authenticated user
        result = await users.get_current_user_router(user=mock_db_user)
        assert result == mock_db_user

    async def test_update_user_calls_db_user_update(self, mock_db, mock_db_user):
        email = "newemail@example.com"
        password = "newpassword"

        with patch.object(db_user, "update_user", AsyncMock(return_value=mock_db_user)) as mock_update:
            updated_user = await users.update_user(email=email, password=password, db=mock_db, user=mock_db_user)
            
            mock_update.assert_awaited_once_with(user=mock_db_user, email=email, password=password, db=mock_db)
            assert updated_user == mock_db_user

    async def test_delete_user_calls_db_user_delete(self, mock_db, mock_db_user):
        with patch.object(db_user, "delete_user", AsyncMock(return_value={"Message": "User Deleted."})) as mock_delete:
            resp = await users.delete_user(user=mock_db_user, db=mock_db)
            
            mock_delete.assert_awaited_once_with(user=mock_db_user, db=mock_db)
            assert resp == {"Message": "User Deleted."}
