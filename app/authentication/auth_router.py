from fastapi import APIRouter, Depends, status
from fastapi.security import OAuth2PasswordRequestForm
from fastapi.exceptions import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi.concurrency import run_in_threadpool

from app.database.dependencies import  get_db
from app.database import db_user
from app.authentication.password_hash import PasswordHasher
from app.authentication.authentication import JWTTokenManager
from app.utils.logger import log

router = APIRouter(
    prefix="/auth",
    tags=["AUTHENTICATION"]
)

@router.post(
    "/token",
    name="token",
    operation_id="login_for_token",
    summary="Authenticate and get access token",
    response_description="JWT access token for authenticating subsequent requests"
)
async def get_token(
        request: OAuth2PasswordRequestForm = Depends(OAuth2PasswordRequestForm), 
        db:AsyncSession = Depends(get_db)
    ):
    """
    Authenticate a user and return a JWT access token. No prior authentication required.

    This is the FIRST tool to call before using any authenticated endpoint.
    Submit username and password to receive a Bearer token. Include this token
    in the Authorization header of subsequent requests as: "Bearer <token>".

    - **username**: The user's registered username
    - **password**: The user's plain-text password
    - **Returns**: {"access_token": "<jwt>", "token_type": "bearer", "user_name": "<username>"}
    - **Error**: 401 Unauthorized if username or password is incorrect
    - **Auth**: Not required (public endpoint)

    **Typical workflow**:
    1. Call this tool with username + password → get access_token
    2. Use the access_token in Authorization header for all protected tools
    """
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
    log.info(f"User {user.user_name} authenticated successfully.")
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user_name": user.user_name
    }
