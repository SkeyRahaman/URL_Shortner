import pytest
from fastapi import status
from tests import client, access_token
from tests.test_users_and_auth import test_new_user


def get_response_after_creating_new_url(access_token):
    headers = {
        "Authorization": f"Bearer {access_token}",
        "accept": "application/json"
    }
    data = {
        "url": "https://www.linkedin.com/in/shakib-mondal/",
        "description": "linked"
    }
    response = client.post("/url/create_short_url", headers=headers, params=data)
    return response


@pytest.fixture
def short_url(access_token):
    response = get_response_after_creating_new_url(access_token)
    return response.json().get("short_url")

def test_new_url(access_token):
    response = get_response_after_creating_new_url(access_token)
    assert response.status_code == 201

def test_get_url_object(short_url):
    response = client.get(f"/url/get_url_object/{short_url}")
    assert response.status_code == status.HTTP_200_OK
    assert response.json().get("long_url") == "https://www.linkedin.com/in/shakib-mondal/"

def test_get_url_object_random():
    response = client.get(f"/url/get_url_object/xxxxxxxxxx")
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json().get("detail") == "URL not found."

def test_get_url_link_random():
    response = client.get(f"/url/xxxxxxxxxx")
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json().get("detail") == "URL not found."

def test_get_url_link(short_url):
    response = client.get(f"/url/{short_url}", follow_redirects=False)
    assert response.status_code == 302
    assert response.headers["location"] == "https://www.linkedin.com/in/shakib-mondal/"




from tests.test_users_and_auth import test_delete_user
