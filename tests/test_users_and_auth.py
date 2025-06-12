from tests import client
from tests import access_token
from config import Config


def test_new_user():
    data = {
        "email": "test@email.com",
        "password": "password",
        "user_name": "test_username"
    }
    response = client.post("/user/new_user", json=data)
    assert response.status_code == 201

    #test same deta creation 
    data = {
        "email": "test@email.com",
        "password": "password",
        "user_name": "test_username"
    }
    response = client.post("/user/new_user", json=data)
    assert response.status_code == 409

def test_auth_token_wrong_credentials():
    payload = {
        "grant_type": "password",
        "username": "Wrong",
        "password": "Wrong",
        "scope": "",
        "client_id": "string",
        "client_secret": "string"
    }
    headers = {
        "accept": "application/json",
        "Content-Type": "application/x-www-form-urlencoded"
    }
    response = client.post("/auth/token", data=payload, headers=headers)
    assert response.status_code == 401
    assert response.json() == {"detail": "Invalid Credentials."}

def test_auth_token_right_credentials():
    payload = {
        "grant_type": "password",
        "username": "test_username",
        "password": "password",
        "scope": "",
        "client_id": "string",
        "client_secret": "string"
    }
    headers = {
        "accept": "application/json",
        "Content-Type": "application/x-www-form-urlencoded"
    }
    response = client.post("/auth/token", data=payload, headers=headers)
    assert response.status_code == 200

    response_json = response.json()
    
    assert "access_token" in response_json
    assert "token_type" in response_json
    assert "expires_in" in response_json
    assert response_json["token_type"] == "bearer" 
    assert response_json["user_name"] == "test_username"
    assert response_json["expires_in"] == Config.ACCESS_TOKEN_EXPIRE_MINUTES * 60  # Convert minutes to seconds



def test_update_user(access_token):
    email = "admin2"
    headers = {"Authorization": f"Bearer {access_token}"}
    response = client.put(f"/user/update_user?email={email}", headers=headers)
    response_json = response.json()


    assert response.status_code == 200
    assert "email" in response_json
    assert response_json["email"] == email  # Ensure the email was updated correctly



def test_delete_user(access_token):
    headers = {"Authorization": f"Bearer {access_token}"}
    response = client.post("/user/DELETE_USER", headers=headers)

    assert response.status_code == 200

    response_json = response.json()
    assert "Message" in response_json
    assert response_json["Message"] == "User Deleted."




    