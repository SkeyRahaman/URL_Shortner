import pytest
from jose import jwt
from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.authentication.authentication import get_current_user
from config import Config

def test_get_current_user_success(db_session: Session, auth_token):
    """Check if user is returned correctly from a valid token."""
    user = get_current_user(token=auth_token, db=db_session)
    assert user is not None
    assert user.user_name == Config.TEST_USER['username']


def test_get_current_user_invalid_token_raises_exception(db_session):
    """Should raise 401 for invalid token."""
    invalid_token = "invalid.token.signature"
    
    with pytest.raises(HTTPException) as exc_info:
        get_current_user(token=invalid_token, db=db_session)

    assert exc_info.value.status_code == 401
    assert "Could not validate credentials." in exc_info.value.detail


def test_get_current_user_with_missing_sub_field(db_session):
    """Should raise 401 when sub is missing in payload."""
    token = jwt.encode({}, Config.SECRET_KEY, algorithm=Config.ALGORITHM)

    with pytest.raises(HTTPException) as exc_info:
        get_current_user(token=token, db=db_session)

    assert exc_info.value.status_code == 401
