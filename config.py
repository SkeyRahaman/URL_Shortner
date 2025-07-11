import os
class Config:
    SQLALCHEMY_DATABASE_URL = os.getenv('DATABASE_URL',"sqlite:///./shortener.db")

    SECRET_KEY = "Some random secret key"
    ALGORITHM = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES = 30

    SHORT_URL_LENGTH = 8
    VERSION = "2.0.0"
    URL_PREFIX = "/api/v2"


    #Test Data
    TEST_USER = {
        "email": "test1@email.com",
        "password": "password1",
        "username": "test_username1"
    }
    AUTH_PAYLOAD = {
        "grant_type": "password",
        "scope": "",
        "client_id": "string",
        "client_secret": "string"
    }