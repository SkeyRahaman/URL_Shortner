import pytest
from datetime import timedelta, datetime, timezone
from app.authentication.authentication import JWTTokenManager  # Adjust this import as needed


class TestJWTTokenManager:
    def setup_method(self):
        # This runs before each test method
        self.jwt_manager = JWTTokenManager

    def test_create_access_token_default_expiry(self):
        data = {"sub": "testuser"}
        token = self.jwt_manager.create_access_token(data)
        assert isinstance(token, str)

        payload = self.jwt_manager.decode_access_token(token)
        assert payload["sub"] == "testuser"
        assert "exp" in payload

        exp_timestamp = payload["exp"]
        now_ts = datetime.now(timezone.utc).timestamp()

        expected_exp = datetime.now(timezone.utc) + timedelta(minutes=self.jwt_manager.EXPIRY_MINUTES)
        expected_exp_ts = expected_exp.timestamp()

        # Allow 10 seconds tolerance for timing differences
        assert (expected_exp_ts - 10) <= exp_timestamp <= (expected_exp_ts + 10)
        assert exp_timestamp > now_ts

    def test_create_access_token_custom_expiry(self):
        data = {"sub": "customuser"}
        custom_expiry = timedelta(minutes=60)

        token = self.jwt_manager.create_access_token(data, expire_delta=custom_expiry)
        assert isinstance(token, str)

        payload = self.jwt_manager.decode_access_token(token)
        assert payload["sub"] == "customuser"
        assert "exp" in payload

        exp_timestamp = payload["exp"]
        expected_exp = datetime.now(timezone.utc) + custom_expiry
        expected_exp_ts = expected_exp.timestamp()

        assert (expected_exp_ts - 10) <= exp_timestamp <= (expected_exp_ts + 10)

    def test_decode_invalid_token_raises(self):
        invalid_token = "invalid.token.value"
        with pytest.raises(ValueError):
            self.jwt_manager.decode_access_token(invalid_token)
