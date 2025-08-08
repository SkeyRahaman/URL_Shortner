import os
from urllib.parse import quote_plus

class Config:
    # Get environment variables with defaults
    DB_PROTOCOL = os.getenv('DATABASE_PR0TOCOL', 'sqlite')  # Changed to SQLite
    DB_USER = os.getenv('DATABASE_USER', '')                 # Not needed for SQLite
    DB_PASSWORD = os.getenv('DATABASE_PASSW0RD', '')        # Not needed for SQLite
    DB_HOST = os.getenv('DATABASE_HOSTNAME', '')             # Not needed for SQLite
    DB_PORT = os.getenv('DATABASE_PORT', '')                 # Not needed for SQLite
    DB_NAME = os.getenv('DATABASE_NAME', 'url_shortner.db')  # SQLite uses a file

    # SQLite has a different URL format
    if DB_PROTOCOL.lower() == 'sqlite':
        # SQLite connection string (uses a file path)
        DATABASE_URL = f"sqlite+aiosqlite:///{DB_NAME}"
    elif DB_PROTOCOL.lower() == 'manual':
        DATABASE_URL = os.getenv('DATABASE_URL_MANUAL', f"sqlite:///{DB_NAME}") 
    else:
        # For other databases (MySQL, PostgreSQL, etc.)
        encoded_password = quote_plus(DB_PASSWORD)
        DATABASE_URL = f"{DB_PROTOCOL}://{DB_USER}:{encoded_password}@{DB_HOST}:{DB_PORT}/{DB_NAME}"


    SECRET_KEY = "Some random secret key"
    ALGORITHM = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES = 30

    SHORT_URL_LENGTH = 8
    VERSION = "2.0.0"
    URL_PREFIX = os.getenv('URL_PREFIX', '')


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
