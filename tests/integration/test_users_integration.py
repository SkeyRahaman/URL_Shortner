import pytest
from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import db_user
from app.schemas import UserDetails
from app.database.models import DBUser
from app.authentication.password_hash import PasswordHasher


@pytest.mark.asyncio
class TestUserOperations:

    async def test_check_email_address_exists(self, test_user: DBUser, async_db_session: AsyncSession):
        result = await db_user.check_email_address(async_db_session, test_user.email)
        assert result is True

    async def test_check_email_address_not_exists(self, async_db_session: AsyncSession):
        result = await db_user.check_email_address(async_db_session, "noone@example.com")
        assert result is False

    async def test_create_user_success(self, async_db_session: AsyncSession):
        new_user_data = UserDetails(
            user_name="newuser",
            email="newuser@example.com",
            password="securepassword"
        )
        user = await db_user.create_user(async_db_session, new_user_data)
        assert isinstance(user, DBUser)
        assert user.email == new_user_data.email

    async def test_create_user_email_already_exists(self, test_user: DBUser, async_db_session: AsyncSession):
        duplicate_user_data = UserDetails(
            user_name="anothername",
            email=test_user.email,
            password="anotherpass"
        )
        with pytest.raises(HTTPException) as exc_info:
            await db_user.create_user(async_db_session, duplicate_user_data)

        assert exc_info.value.status_code == status.HTTP_409_CONFLICT
        assert "Email already registered." in exc_info.value.detail

    async def test_update_user_email_password(self, test_user: DBUser, async_db_session: AsyncSession):
        new_email = "updated@example.com"
        new_password = "updatedpassword"

        updated_user = await db_user.update_user(user=test_user, email=new_email, password=new_password, db=async_db_session)
        assert updated_user.email == new_email
        assert PasswordHasher.verify_password(plain_password=new_password, hashed_password=updated_user.password)

    async def test_update_user_not_found(self, async_db_session: AsyncSession):
        fake_user = DBUser(id=9999, user_name="ghost", email="ghost@example.com", password="irrelevant")
        with pytest.raises(HTTPException) as exc_info:
            await db_user.update_user(user=fake_user, email="x@y.com", password="xyz", db=async_db_session)

        assert exc_info.value.status_code == status.HTTP_404_NOT_FOUND

    async def test_get_user_success(self, test_user: DBUser, async_db_session: AsyncSession):
        user = await db_user.get_user(user_name=test_user.user_name, db=async_db_session)
        assert user.email == test_user.email

    async def test_get_user_not_found(self, async_db_session: AsyncSession):
        with pytest.raises(HTTPException) as exc_info:
            await db_user.get_user(user_name="nonexistent", db=async_db_session)

        assert exc_info.value.status_code == status.HTTP_404_NOT_FOUND

    async def test_delete_user_success(self, test_user: DBUser, async_db_session: AsyncSession):
        result = await db_user.delete_user(test_user, async_db_session)
        assert result["Message"] == "User Deleted."

    async def test_delete_user_not_found(self, async_db_session: AsyncSession):
        fake_user = DBUser(id=9999, user_name="ghost", email="ghost@example.com", password="irrelevant")
        with pytest.raises(HTTPException) as exc_info:
            await db_user.delete_user(fake_user, async_db_session)

        assert exc_info.value.status_code == status.HTTP_404_NOT_FOUND
