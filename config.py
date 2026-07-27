from app.core.secrets import get_secret, get_secret_int
from urllib.parse import quote_plus

class Config:
    DB_PROTOCOL = get_secret('DATABASE_PROTOCOL', 'postgresql+psycopg')
    DB_USER = get_secret('DATABASE_USER', 'postgres')
    DB_PASSWORD = get_secret('DATABASE_PASSWORD', 'postgres')
    DB_HOST = get_secret('DATABASE_HOSTNAME', 'localhost')
    DB_PORT = get_secret('DATABASE_PORT', '5432')
    DB_NAME = get_secret('DATABASE_NAME', 'url_service')

    encoded_password = quote_plus(DB_PASSWORD)
    DATABASE_URL = f"{DB_PROTOCOL}://{DB_USER}:{encoded_password}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

    SLUG_LENGTH = get_secret_int('SLUG_LENGTH', 8)
    VERSION = "3.0.0"
    URL_PREFIX = get_secret('URL_PREFIX', '')

    # Logging Configuration
    LOG_LEVEL = get_secret('LOG_LEVEL', 'INFO')
    LOG_FILENAME = get_secret('LOG_FILENAME', 'app.json')
    LOG_FOLDERNAME = get_secret('LOG_FOLDERNAME', 'logs')
    LOG_MAX_BYTES = get_secret_int('LOG_MAX_BYTES', 5_000_000)
    LOG_BACKUP_COUNT = get_secret_int('LOG_BACKUP_COUNT', 1)

    # Test Data
    TEST_URL = {
        "url": "https://www.youtube.com/",
        "description": "YouTube video platform.",
    }
