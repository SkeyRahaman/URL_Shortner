from fastapi import APIRouter, Depends, status
from fastapi.exceptions import HTTPException
from fastapi.responses import HTMLResponse

from app.schemas import UserDetails, UserDisplay
from app.database import db_user
from app.database.dependencies import get_db
from app.database.models import DBUser
from app.authentication.dependencies import get_current_user

from sqlalchemy.ext.asyncio import AsyncSession

router = APIRouter(
    prefix="/users",
    tags=["Users"]
)

@router.post(
    "",
    response_model=UserDisplay,
    status_code=status.HTTP_201_CREATED,
    name="create_user",
    operation_id="create_user",
    summary="Create a new user account",
    response_description="The created user details"
)
async def create_new_user(data: UserDetails, db: AsyncSession = Depends(get_db)):
    """
    Register a new user account. No authentication required.

    Creates a user with a unique username, email, and password. The password
    is hashed before storage. Fails with 409 if the email or username is
    already taken.

    - **data.user_name**: Unique username for the account
    - **data.email**: Email address (must not already be registered)
    - **data.password**: Plain-text password (will be hashed server-side)
    - **Returns**: User object with id, user_name, and email (password excluded)
    - **Error**: 409 Conflict if email or username already exists
    - **Auth**: Not required (public endpoint)
    """
    if await db_user.check_email_address(db=db, email=data.email) or await db_user.check_username_exist(db=db,username=data.user_name):
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Email already registered.")
    return await db_user.create_user(db, data)

@router.get(
    "/me",
    response_model=UserDisplay,
    status_code=status.HTTP_200_OK,
    name="get_current_user",
    operation_id="get_current_user",
    summary="Get current authenticated user details",
    response_description="The authenticated user's details"
)
async def get_current_user_router(user: DBUser = Depends(get_current_user)):
    """
    Retrieve the profile of the currently authenticated user. Requires authentication.

    Returns the user's id, username, and email. Use this to verify who is
    logged in or to display profile information.

    - **Returns**: User object with id, user_name, and email
    - **Auth**: Requires Bearer token in Authorization header
    """
    return user

@router.put(
    "/me",
    response_model=UserDisplay,
    name="update_current_user",
    operation_id="update_current_user",
    summary="Update current user's details",
    response_description="Updated user details"
)
async def update_user(
    email: str = None,
    password: str = None,
    db: AsyncSession = Depends(get_db),
    user: DBUser = Depends(get_current_user)
):
    """
    Update the authenticated user's email or password. Requires authentication.

    At least one of email or password must be provided. The password will be
    re-hashed before storage. Only the currently authenticated user's own
    profile is updated.

    - **email**: New email address (optional, omit to keep current)
    - **password**: New plain-text password (optional, will be hashed)
    - **Returns**: Updated user object with id, user_name, and email
    - **Auth**: Requires Bearer token in Authorization header
    """
    return await db_user.update_user(user=user, email=email, password=password, db=db)

@router.delete(
    "/me",
    name="delete_current_user",
    operation_id="delete_current_user",
    summary="Delete current user account",
    response_description="Confirmation of deletion"
)
async def delete_user(
    user: DBUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Permanently delete the authenticated user's account. Requires authentication.

    This action is irreversible. All URLs owned by this user will become
    orphaned (the URLs remain but have no owner). The Bearer token becomes
    invalid after deletion.

    - **Returns**: {"Message": "User Deleted."} on success
    - **Error**: 404 if the user account was not found
    - **Auth**: Requires Bearer token in Authorization header
    """
    response = await db_user.delete_user(user=user, db=db)
    if response:
        return {"Message" : "User Deleted."}
    else:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User Not found.")