import pytest
from app.core.secrets import get_secret, get_secret_int
import os
from pathlib import Path
import app.core.secrets

@pytest.fixture
def temp_secrets_dir(tmp_path):
    orig_dir = app.core.secrets.SECRETS_DIR
    app.core.secrets.SECRETS_DIR = tmp_path
    yield tmp_path
    app.core.secrets.SECRETS_DIR = orig_dir

def test_get_secret_from_file(temp_secrets_dir):
    (temp_secrets_dir / "NON_PROD_TEST_KEY").write_text("file_value\n")
    assert get_secret("TEST_KEY", "default") == "file_value"

def test_get_secret_fallback_to_env(temp_secrets_dir, monkeypatch):
    monkeypatch.setenv("TEST_KEY", "env_value")
    assert get_secret("TEST_KEY", "default") == "env_value"

def test_get_secret_fallback_to_default(temp_secrets_dir):
    assert get_secret("TEST_KEY_NOT_EXIST", "default_val") == "default_val"

def test_get_secret_int(temp_secrets_dir):
    (temp_secrets_dir / "NON_PROD_TEST_INT").write_text(" 42 \n")
    assert get_secret_int("TEST_INT", 0) == 42
