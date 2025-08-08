from typing import Optional
from datetime import timedelta, datetime, timezone
from jose import jwt, JWTError
from config import Config

class JWTTokenManager:
    SECRET_KEY = Config.SECRET_KEY
    ALGORITHM = Config.ALGORITHM
    EXPIRY_MINUTES = Config.ACCESS_TOKEN_EXPIRE_MINUTES

    @staticmethod
    def create_access_token(data: dict, expire_delta: Optional[timedelta] = None) -> str:
        to_encode = data.copy()
        expire = datetime.now(timezone.utc) + (
            expire_delta if expire_delta else timedelta(minutes=JWTTokenManager.EXPIRY_MINUTES)
        )
        to_encode.update({"exp": expire})
        encoded_jwt = jwt.encode(to_encode, key=JWTTokenManager.SECRET_KEY, algorithm=JWTTokenManager.ALGORITHM)
        return encoded_jwt

    @staticmethod
    def decode_access_token(token: str) -> dict:
        try:
            payload = jwt.decode(token, key=JWTTokenManager.SECRET_KEY, algorithms=[JWTTokenManager.ALGORITHM])
            return payload
        except JWTError as e:
            raise ValueError("Invalid or expired token") from e
