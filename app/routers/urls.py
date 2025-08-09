from fastapi import APIRouter, Depends, status, Query
from fastapi.responses import RedirectResponse, HTMLResponse
from fastapi.exceptions import HTTPException
from sqlalchemy.orm import Session

from app.authentication.dependencies import get_current_user
from app.schemas import UrlDisplay, UrlDataUpdate
from app.database import db_url
from app.database.dependencies import get_db
from app.database.models import DBUser

router = APIRouter(
    prefix="/urls",
    tags=["URLs"],
)

@router.post(
    "/create_short_url",
    response_model=UrlDisplay,
    status_code=status.HTTP_201_CREATED,
    name="create_short_url",
    summary="Create a short URL",
    response_description="The created short URL details"
)
async def create_short_url(
    url: str,
    description: str,
    db: Session = Depends(get_db),
    user: DBUser = Depends(get_current_user)
):
    """
    Create a shortened URL from a long URL.
    
    - **url**: The original long URL to shorten
    - **description**: Description for the URL
    - Returns: Created short URL details
    """
    return await db_url.add_url(long_url=url, description=description, user_id=user.id, db=db)

@router.get(
    "/{short_url}",
    name="redirect_short_url",
    summary="Redirect to original URL",
    response_description="Redirect response to original URL"
)
async def redirect_short_url(
    short_url: str,
    db: Session = Depends(get_db)
):
    """
    Redirects to the original long URL associated with the short URL.
    
    - **short_url**: The shortened URL identifier
    - Returns: 302 Redirect to original URL
    """
    long_url = await db_url.get_url(short_url=short_url, db=db)
    long_url = long_url.long_url
    return RedirectResponse(url=long_url, status_code=status.HTTP_302_FOUND)

@router.get(
    "/{short_url}/details",
    response_model=UrlDisplay,
    name="get_short_url_details",
    summary="Get short URL details",
    response_description="Detailed information about the short URL"
)
async def get_short_url_details(
    short_url: str,
    db: Session = Depends(get_db)
):
    """
    Retrieve metadata about a shortened URL.
    
    - **short_url**: The shortened URL identifier
    - Returns: URL details including original URL and creation info
    """
    return await db_url.get_url(short_url=short_url, db=db)

@router.get(
    "",
    response_model=list[UrlDisplay],
    name="list_user_urls",
    summary="List user's URLs",
    response_description="Paginated list of user's short URLs"
)
async def list_urls(
    skip: int = Query(0, ge=0, description="Pagination offset"),
    limit: int = Query(10, ge=1, le=100, description="Items per page (1-100)"),
    db: Session = Depends(get_db),
    user: DBUser = Depends(get_current_user)
):
    """
    Get a paginated list of the authenticated user's short URLs.
    
    - **skip**: Number of items to skip (for pagination)
    - **limit**: Number of items to return per page
    - Returns: List of URL objects with metadata
    """
    return await db_url.get_user_urls(user_id=user.id, skip=skip, limit=limit, db=db)

@router.put(
    "/{short_url}",
    response_model=UrlDisplay,
    name="update_short_url",
    summary="Update short URL details",
    response_description="Updated URL details"
)
async def update_url(
    url_data: UrlDataUpdate,
    db: Session = Depends(get_db),
    user: DBUser = Depends(get_current_user)
):
    """
    Update the destination or metadata of a short URL.
    
    - **short_url**: The URL identifier to update
    - **url_data**: New URL details (long URL and/or description)
    - Returns: Updated URL details
    """
    return await db_url.update_url(
        short_url=url_data.short_url,
        new_long_url=url_data.long_url,
        new_description=url_data.description,
        user_id=user.id,
        db=db
    )

@router.delete(
    "/{short_url}",
    status_code=status.HTTP_200_OK,
    name="delete_short_url",
    summary="Delete a short URL",
    response_description="Confirmation of deletion"
)
async def delete_url(
    short_url: str,
    db: Session = Depends(get_db),
    user: DBUser = Depends(get_current_user)
):
    """
    Permanently delete a short URL.
    
    - **short_url**: The URL identifier to delete
    - Returns: Success message
    """
    response = await db_url.delete_url(short_url=short_url, user_id=user.id, db=db)
    if response:
        return {"Message" : "URL Deleted."}
    else:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="URL not found.")