import pytest
from sqlalchemy.orm import Session
from fastapi import HTTPException, status

from app.database import db_user
from app.schemas import UserDetails
from app.database.models import DBUser
from app.database.hash import PasswordHasher


def test_check_email_address_exists(test_user, db_session):
    result = db_user.check_email_address(db_session, test_user.email)
    assert result is True


def test_check_email_address_not_exists(db_session):
    result = db_user.check_email_address(db_session, "noone@example.com")
    assert result is False


def test_create_user_success(db_session):
    new_user_data = UserDetails(
        user_name="newuser",
        email="newuser@example.com",
        password="securepassword"
    )
    user = db_user.create_user(db_session, new_user_data)
    assert isinstance(user, DBUser)
    assert user.email == new_user_data.email


def test_create_user_email_already_exists(test_user, db_session):
    duplicate_user_data = UserDetails(
        user_name="anothername",
        email=test_user.email,
        password="anotherpass"
    )
    with pytest.raises(HTTPException) as exc_info:
        db_user.create_user(db_session, duplicate_user_data)

    assert exc_info.value.status_code == status.HTTP_409_CONFLICT
    assert "Email already registered." in exc_info.value.detail


def test_update_user_email_password(test_user, db_session):
    new_email = "updated@example.com"
    new_password = "updatedpassword"

    updated_user = db_user.update_user(test_user, email=new_email, password=new_password, db=db_session)
    assert updated_user.email == new_email
    assert PasswordHasher.verify_password(plain_password=updated_user.password, hashed_password=new_password)


def test_update_user_not_found(db_session):
    fake_user = DBUser(id=9999, user_name="ghost", email="ghost@example.com", password="irrelevant")
    with pytest.raises(HTTPException) as exc_info:
        data = db_user.update_user(fake_user, email="x@y.com", password="xyz", db=db_session)
        print(data)
    
    assert exc_info.value.status_code == status.HTTP_404_NOT_FOUND


def test_get_user_success(test_user, db_session):
    user = db_user.get_user(user_name=test_user.user_name, db=db_session)
    assert user.email == test_user.email


def test_get_user_not_found(db_session):
    with pytest.raises(HTTPException) as exc_info:
        db_user.get_user(user_name="nonexistent", db=db_session)

    assert exc_info.value.status_code == status.HTTP_404_NOT_FOUND


def test_delete_user_success(test_user, db_session):
    result = db_user.delete_user(test_user, db_session)
    assert result["Message"] == "User Deleted."


def test_delete_user_not_found(db_session):
    fake_user = DBUser(id=9999, user_name="ghost", email="ghost@example.com", password="irrelevant")
    with pytest.raises(HTTPException) as exc_info:
        db_user.delete_user(fake_user, db_session)

    assert exc_info.value.status_code == status.HTTP_404_NOT_FOUND
