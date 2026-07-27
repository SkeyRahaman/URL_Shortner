import os
from pathlib import Path

SECRETS_DIR = Path(os.getenv("SECRETS_DIR", "/secrets"))
APP_ENV = os.getenv("APP_ENV", "NON_PROD").upper()

def get_secret(key: str, default: str = "") -> str:
    """
    Resolve a configuration value using the fallback chain:
      1. File: /secrets/{APP_ENV}_{KEY}
      2. Env var: os.getenv(KEY)
      3. Hardcoded default
    
    Args:
        key: Variable name in UPPER_CASE (e.g., 'DATABASE_PASSWORD')
        default: Fallback value if neither file nor env var exists
    
    Returns:
        The resolved value as a string.
    """
    # 1. Try secrets folder
    secret_file = SECRETS_DIR / f"{APP_ENV}_{key}"
    if secret_file.is_file():
        return secret_file.read_text().strip()
    
    # 2. Try environment variable
    env_val = os.getenv(key)
    if env_val is not None:
        return env_val
    
    # 3. Return default
    return default


def get_secret_int(key: str, default: int = 0) -> int:
    """Same as get_secret but returns an integer."""
    return int(get_secret(key, str(default)))
