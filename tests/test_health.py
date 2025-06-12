from fastapi import status
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_health_check():
    """Test if the health endpoint returns 200 and expected JSON."""
    url = app.url_path_for("health_check") 
    response = client.get(url)
    
    # Assert status code
    assert response.status_code == status.HTTP_200_OK
    
    # Assert response body
    data = response.json()
    assert "version" in data
    assert "status" in data
    assert data["status"] == "HEALTHY"