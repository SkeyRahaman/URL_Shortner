from fastapi import Depends, status
from fastapi.security import OAuth2PasswordBearer
from fastapi.exceptions import HTTPException
from jose import JWTError
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import db_user
from app.authentication.authentication import JWTTokenManager
from app.database.dependencies import get_db

oauth2_scheme =  OAuth2PasswordBearer(tokenUrl = "auth/token")

async def get_current_user(
    token: str = Depends(oauth2_scheme), 
    db: AsyncSession = Depends(get_db)
):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials.",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = JWTTokenManager.decode_access_token(token)
        user_name = payload.get("sub")
        if user_name is None:
            raise credentials_exception
    except (JWTError, ValueError):
        raise credentials_exception
    
    user = await db_user.get_user(user_name=user_name, db=db)
    if not user:
        raise credentials_exception
    return user
