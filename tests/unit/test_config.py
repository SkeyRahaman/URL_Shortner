from config import Config

def test_config_defaults():
    assert Config.DB_PROTOCOL == "postgresql+psycopg"
    assert Config.SLUG_LENGTH == 8
    assert "postgresql+psycopg://" in Config.DATABASE_URL
