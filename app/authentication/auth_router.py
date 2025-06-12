from fastapi import APIRouter, Depends, status
from fastapi.security import OAuth2PasswordRequestForm
from fastapi.exceptions import HTTPException
from sqlalchemy.orm import Session
from app.database import  get_db
from app.database.models import DBUser
from app.database.hash import Hash
from app.authentication.authentication import create_access_token
from config import Config


router = APIRouter(
    prefix="/auth",
    tags=["AUTHENTICATION"]
)

@router.post("/token")
def get_token(request: OAuth2PasswordRequestForm = Depends(OAuth2PasswordRequestForm), db:Session = Depends(get_db)):
    user = db.query(DBUser).filter(DBUser.user_name == request.username).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, 
            detail="Invalid Credentials.",
        )
    if not Hash.verify(user.password, request.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid Credentials.",
        )
    access_token = create_access_token(data={"sub": user.user_name})
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "expires_in": int(Config.ACCESS_TOKEN_EXPIRE_MINUTES) * 60,  # Convert minutes to seconds
        "user_name": user.user_name
    }