from fastapi import status
from tests import client

def test_get_url_object_random():
    response = client.get(f"/health")
    assert response.status_code == status.HTTP_200_OK
    assert response.json().get("message") == "HEALTHY"