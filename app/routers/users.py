from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.schemas import UserDetails, UserDisplay
from app.database import get_db, db_user
from app.database.models import DBUser
from app.authentication.authentication import get_current_user

router = APIRouter(
    prefix="/users",
    tags=["Users"]
)

@router.post(
    "",
    response_model=UserDisplay,
    status_code=status.HTTP_201_CREATED,
    name="create_user",
    summary="Create a new user account",
    response_description="The created user details"
)
def create_new_user(data: UserDetails, db: Session = Depends(get_db)):
    """
    Creates a new user with the provided details.
    
    - **data**: UserDetails schema containing email and password
    - Returns: Newly created user information
    """
    return db_user.create_user(db, data)

@router.get(
    "/me",
    response_model=UserDisplay,
    status_code=status.HTTP_200_OK,
    name="get_current_user",
    summary="Get current authenticated user details",
    response_description="The authenticated user's details"
)
def get_current_user(user: DBUser = Depends(get_current_user)):
    """
    Returns the details of the currently authenticated user.
    
    - Requires valid authentication token
    - Returns: Current user's information
    """
    return user

@router.put(
    "/me",
    response_model=UserDisplay,
    name="update_current_user",
    summary="Update current user's details",
    response_description="Updated user details"
)
def update_user(
    email: str = None,
    password: str = None,
    db: Session = Depends(get_db),
    user: DBUser = Depends(get_current_user)
):
    """
    Updates the current user's information.
    
    - At least one of email or password must be provided
    - Returns: Updated user information
    """
    return db_user.update_user(user=user, email=email, password=password, db=db)

@router.delete(
    "/me",
    name="delete_current_user",
    summary="Delete current user account",
    response_description="Confirmation of deletion"
)
def delete_user(
    user: DBUser = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Permanently deletes the current user's account.
    
    - This action cannot be undone
    - Returns: Success/error message
    """
    return db_user.delete_user(user=user, db=db)