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
    operation_id="create_short_url",
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
    Create a shortened URL from a long URL. Requires authentication.

    Takes a full URL (e.g. "https://example.com/very/long/path") and generates
    a unique short code. The short code can then be used with the redirect
    endpoint to navigate to the original URL.

    - **url**: The original long URL to shorten (must be a valid URL)
    - **description**: A human-readable description of what this URL points to (max 200 chars)
    - **Returns**: The created URL object with id, short_url, long_url, and description
    - **Auth**: Requires Bearer token in Authorization header
    """
    return await db_url.add_url(long_url=url, description=description, user_id=user.id, db=db)

@router.get(
    "/{short_url}",
    name="redirect_short_url",
    operation_id="redirect_short_url",
    summary="Redirect to original URL",
    response_description="Redirect response to original URL"
)
async def redirect_short_url(
    short_url: str,
    db: Session = Depends(get_db)
):
    """
    Redirect to the original long URL using its short code. No authentication required.

    Given a short URL code (e.g. "abc12345"), looks up the original URL and
    returns a 302 redirect. This is the core functionality of the URL shortener.

    - **short_url**: The 8-character short URL code (e.g. "abc12345")
    - **Returns**: HTTP 302 redirect to the original long URL
    - **Auth**: Not required (public endpoint)
    """
    long_url = await db_url.get_url(short_url=short_url, db=db)
    long_url = long_url.long_url
    return RedirectResponse(url=long_url, status_code=status.HTTP_302_FOUND)

@router.get(
    "/{short_url}/details",
    response_model=UrlDisplay,
    name="get_short_url_details",
    operation_id="get_short_url_details",
    summary="Get short URL details",
    response_description="Detailed information about the short URL"
)
async def get_short_url_details(
    short_url: str,
    db: Session = Depends(get_db)
):
    """
    Get metadata about a shortened URL without redirecting. No authentication required.

    Returns the full details of a URL entry: the original long URL, the short
    code, the description, and the record ID. Use this to inspect a short URL
    before visiting it.

    - **short_url**: The 8-character short URL code (e.g. "abc12345")
    - **Returns**: URL object with id, short_url, long_url, and description
    - **Auth**: Not required (public endpoint)
    """
    return await db_url.get_url(short_url=short_url, db=db)

@router.get(
    "",
    response_model=list[UrlDisplay],
    name="list_user_urls",
    operation_id="list_user_urls",
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
    List all shortened URLs created by the currently authenticated user. Requires authentication.

    Returns a paginated list of URL objects. Each object includes the short code,
    original long URL, description, and record ID.

    - **skip**: Number of records to skip (default: 0). Use for pagination.
    - **limit**: Maximum number of records to return (default: 10, max: 100)
    - **Returns**: Array of URL objects belonging to the authenticated user
    - **Auth**: Requires Bearer token in Authorization header
    """
    return await db_url.get_user_urls(user_id=user.id, skip=skip, limit=limit, db=db)

@router.put(
    "/{short_url}",
    response_model=UrlDisplay,
    name="update_short_url",
    operation_id="update_short_url",
    summary="Update short URL details",
    response_description="Updated URL details"
)
async def update_url(
    url_data: UrlDataUpdate,
    db: Session = Depends(get_db),
    user: DBUser = Depends(get_current_user)
):
    """
    Update the destination URL or description of an existing short URL. Requires authentication.

    The authenticated user can only update URLs they own. The short code itself
    cannot be changed. Provide the new long_url and/or description to update.

    - **url_data.short_url**: The 8-character short URL code to update
    - **url_data.long_url**: The new destination URL
    - **url_data.description**: The new description (max 200 chars)
    - **Returns**: The updated URL object with id, short_url, long_url, and description
    - **Auth**: Requires Bearer token in Authorization header
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
    operation_id="delete_short_url",
    summary="Delete a short URL",
    response_description="Confirmation of deletion"
)
async def delete_url(
    short_url: str,
    db: Session = Depends(get_db),
    user: DBUser = Depends(get_current_user)
):
    """
    Permanently delete a shortened URL. Requires authentication.

    The authenticated user can only delete URLs they own. This action is
    irreversible — the short code will no longer redirect after deletion.

    - **short_url**: The 8-character short URL code to delete (e.g. "abc12345")
    - **Returns**: {"Message": "URL Deleted."} on success
    - **Error**: 404 if the short URL does not exist or belongs to another user
    - **Auth**: Requires Bearer token in Authorization header
    """
    response = await db_url.delete_url(short_url=short_url, user_id=user.id, db=db)
    if response:
        return {"Message" : "URL Deleted."}
    else:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="URL not found.")