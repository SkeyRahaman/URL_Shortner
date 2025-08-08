from fastapi import APIRouter, Depends, status
from fastapi.security import OAuth2PasswordRequestForm
from fastapi.exceptions import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.database.dependencies import  get_db
from app.database import db_user
from app.authentication.password_hash import PasswordHasher
from app.authentication.authentication import JWTTokenManager
from fastapi.concurrency import run_in_threadpool

router = APIRouter(
    prefix="/auth",
    tags=["AUTHENTICATION"]
)

@router.post("/token", name="token")
async def get_token(
        request: OAuth2PasswordRequestForm = Depends(OAuth2PasswordRequestForm), 
        db:AsyncSession = Depends(get_db)
    ):
    user = await db_user.get_user(user_name=request.username, db=db)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, 
            detail="Invalid Credentials.",
        )
    if not await run_in_threadpool(PasswordHasher.verify_password, request.password, user.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid Credentials.",
        )
    access_token = JWTTokenManager.create_access_token(
        data={
                "sub": user.user_name
            }
        )
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user_name": user.user_name
    }
