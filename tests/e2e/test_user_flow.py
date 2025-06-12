import pytest
from fastapi.testclient import TestClient
from app.main import app

user_payload = {
    "email": "e2e_user@example.com",
    "password": "e2e_password",
    "user_name": "e2e_user"
}

updated_user_payload = {
    "email": "updated_e2e_user_new@example.com",
    "password": "newpass123"
}

url_payload = {
    "url": "https://example.com/e2e-test",
    "description": "E2E test link"
}

updated_url_payload = {
    "long_url": "https://example.com/e2e-updated",
    "description": "Updated E2E test"
}

token = None
headers = {}
short_url = None


@pytest.mark.order(1)
def test_create_user(client: TestClient):
    url = app.url_path_for("create_user")
    res = client.post(url, json=user_payload)
    assert res.status_code == 201
    assert res.json()["email"] == user_payload["email"]


@pytest.mark.order(2)
def test_get_token(client: TestClient):
    global token, headers
    url = app.url_path_for("token")
    res = client.post(url, data={
        "username": user_payload["user_name"],
        "password": user_payload["password"]
    })
    assert res.status_code == 200
    token = res.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}


@pytest.mark.order(3)
def test_get_current_user(client: TestClient):
    url = app.url_path_for("get_current_user")
    res = client.get(url, headers=headers)
    assert res.status_code == 200
    assert res.json()["user_name"] == user_payload["user_name"]


@pytest.mark.order(4)
def test_update_user(client: TestClient):
    url = app.url_path_for("update_current_user")
    res = client.put(url, headers=headers, params=updated_user_payload)
    assert res.status_code == 200
    assert res.json()["email"] == updated_user_payload["email"]


@pytest.mark.order(5)
def test_create_short_url(client: TestClient):
    global short_url
    url = app.url_path_for("create_short_url")
    res = client.post(url, headers=headers, params=url_payload)
    assert res.status_code == 201
    short_url = res.json()["short_url"]
    assert short_url


@pytest.mark.order(6)
def test_get_short_url_details(client: TestClient):
    url = app.url_path_for("get_short_url_details", short_url=short_url)
    res = client.get(url, headers=headers)
    assert res.status_code == 200
    assert res.json()["long_url"] == url_payload["url"]


@pytest.mark.order(7)
def test_redirect_short_url(client: TestClient):
    url = app.url_path_for("redirect_short_url", short_url=short_url)
    res = client.get(url, follow_redirects=False)
    assert res.status_code == 302
    assert res.headers["location"] == url_payload["url"]


@pytest.mark.order(8)
def test_list_urls(client: TestClient):
    url = app.url_path_for("list_user_urls")
    res = client.get(url, headers=headers)
    assert res.status_code == 200
    assert isinstance(res.json(), list)
    assert any(u["short_url"] == short_url for u in res.json())


@pytest.mark.order(9)
def test_update_short_url(client: TestClient):
    url = app.url_path_for("update_short_url", short_url=short_url)
    updated_url_payload["short_url"] = short_url
    res = client.put(url, headers=headers, json=updated_url_payload)
    assert res.status_code == 200
    assert res.json()["long_url"] == updated_url_payload["long_url"]


@pytest.mark.order(10)
def test_delete_short_url(client: TestClient):
    url = app.url_path_for("delete_short_url", short_url=short_url)
    res = client.delete(url, headers=headers)
    assert res.status_code == 200
    assert "deleted" in res.json()["Message"].lower()


@pytest.mark.order(11)
def test_delete_user(client: TestClient):
    url = app.url_path_for("delete_current_user")
    res = client.delete(url, headers=headers)
    assert res.status_code == 200
    print(res.json())
    assert "deleted" in res.json()["Message"].lower()
