import pytest
from app.database import db_url
from config import Config

def test_generate_short_code_length():
    url = "https://example.com/my-long-url"
    short_code = db_url.generate_short_code(url)
    assert isinstance(short_code, str)
    assert len(short_code) == Config.SHORT_URL_LENGTH

def test_generate_short_code_deterministic():
    url = "https://example.com/my-unique-url"
    code1 = db_url.generate_short_code(url)
    code2 = db_url.generate_short_code(url)
    assert code1 == code2  # Should be deterministic

def test_generate_short_code_uniqueness():
    url1 = "https://example.com/1"
    url2 = "https://example.com/2"
    code1 = db_url.generate_short_code(url1)
    code2 = db_url.generate_short_code(url2)
    assert code1 != code2  # Should generate different codes for different URLs
