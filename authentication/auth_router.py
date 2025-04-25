from fastapi import APIRouter, Depends, status
from fastapi.security import OAuth2PasswordRequestForm
from fastapi.exceptions import HTTPException
from sqlalchemy.orm import Session
from database import  get_db
from database.models import DBUser
from database.hash import Hash
from authentication.authentication import create_access_token


router = APIRouter(
    prefix="/auth",
    tags=["AUTHENTICATION"]
)

@router.post("/token")
def get_token(request: OAuth2PasswordRequestForm = Depends(OAuth2PasswordRequestForm), db:Session = Depends(get_db)):
    user = db.query(DBUser).filter(DBUser.user_name == request.username).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, 
            detail="Invalid Credentials.",
        )
    if not Hash.verify(user.password, request.password):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Invalid Credentials.",
        )
    access_token = create_access_token(data={"sub": user.user_name})
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user_name": user.user_name
    }