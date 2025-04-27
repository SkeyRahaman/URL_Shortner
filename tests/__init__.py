import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app=app)

@pytest.fixture
def access_token():
    credentials = {
        "username": "test_username",
        "password": "password" 
    }
    response = client.post("/auth/token", data=credentials)
    token = response.json().get("access_token")

    assert token is not None, "Access token was not generated!"
    return token
