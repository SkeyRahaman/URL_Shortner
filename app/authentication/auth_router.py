from fastapi import APIRouter, Depends, status
from fastapi.security import OAuth2PasswordRequestForm
from fastapi.exceptions import HTTPException
from sqlalchemy.orm import Session
from app.database import  get_db
from app.database.models import DBUser
from app.database.hash import PasswordHasher
from app.authentication.authentication import create_access_token


router = APIRouter(
    prefix="/auth",
    tags=["AUTHENTICATION"]
)

@router.post("/token", name="token")
def get_token(request: OAuth2PasswordRequestForm = Depends(OAuth2PasswordRequestForm), db:Session = Depends(get_db)):
    user = db.query(DBUser).filter(DBUser.user_name == request.username).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, 
            detail="Invalid Credentials.",
        )
    if not PasswordHasher.verify_password(plain_password=request.password, hashed_password=user.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid Credentials.",
        )
    access_token = create_access_token(data={"sub": user.user_name})
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user_name": user.user_name
    }