from fastapi import Depends, status
from fastapi.security import OAuth2PasswordBearer
from fastapi.exceptions import HTTPException
from config import Config
from typing import Optional
from datetime import timedelta, datetime, timezone
from jose import jwt
from sqlalchemy.orm import Session
from database import get_db, db_user

oauth2_scheme =  OAuth2PasswordBearer(tokenUrl = "auth/token")

def create_access_token(data : dict, expire_delta : Optional[timedelta] = None):
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + (expire_delta if expire_delta else timedelta(minutes=Config.ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp" : expire})
    return jwt.encode(to_encode, key=Config.SECTER_KEY, algorithm=Config.ALOGRITHM)

def get_curren_user(token : str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials.",  
        headers={"WWW-Authenticate": "Bearer"}, 
    )
    try:
        payload = jwt.decode(token, Config.SECTER_KEY, algorithms=[Config.ALOGRITHM])
        user_name = payload.get("sub")
        if user_name is None:
            raise credentials_exception
    except jwt.JWTError:
        raise credentials_exception
    user = db_user.get_user(user_name=user_name, db=db)
    if not user or user is None:
        raise credentials_exception
    return user