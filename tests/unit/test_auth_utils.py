import pytest
from jose import jwt
from app.authentication.authentication import create_access_token
from config import Config

def test_create_access_token_returns_valid_token(test_user):
    data = {"sub": test_user.user_name}
    token = create_access_token(data)

    decoded = jwt.decode(token, Config.SECRET_KEY, algorithms=[Config.ALGORITHM])
    assert decoded.get("sub") == test_user.user_name
    assert "exp" in decoded


def test_create_access_token_with_custom_expiry(test_user):
    from datetime import timedelta

    token = create_access_token({"sub": test_user.user_name}, expire_delta=timedelta(minutes=1))
    decoded = jwt.decode(token, Config.SECRET_KEY, algorithms=[Config.ALGORITHM])
    assert "exp" in decoded
