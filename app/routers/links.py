from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import RedirectResponse
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List

from app.database import SessionLocal
from app.database import db_link
from app.schemas import LinkCreate, LinkUpdate, LinkResponse
from app.dependencies.header_auth import get_user_id
from app.utils.logger import log

router = APIRouter(prefix="/links", tags=["Links"])

async def get_db():
    async with SessionLocal() as session:
        yield session

@router.post("", response_model=LinkResponse, status_code=status.HTTP_201_CREATED)
async def create_link(link: LinkCreate, user_id: int = Depends(get_user_id), db: AsyncSession = Depends(get_db)):
    log.info("create_link_requested", user_id=user_id, custom_slug=link.custom_slug)
    if link.custom_slug:
        existing = await db_link.get_link_by_slug(link.custom_slug, db, include_deleted=True)
        if existing:
            log.warning("custom_slug_conflict", user_id=user_id, custom_slug=link.custom_slug)
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Custom slug already exists or was previously used")
    
    new_link = await db_link.create_link(
        original_url=link.original_url,
        description=link.description,
        created_by=user_id,
        db=db,
        custom_slug=link.custom_slug,
        expires_at=link.expires_at
    )
    log.info("link_created_successfully", user_id=user_id, slug=new_link.slug)
    return new_link

@router.get("", response_model=List[LinkResponse])
async def list_links(skip: int = 0, limit: int = 10, user_id: int = Depends(get_user_id), db: AsyncSession = Depends(get_db)):
    log.info("list_links_requested", user_id=user_id, skip=skip, limit=limit)
    links = await db_link.get_links_by_user(user_id, skip, limit, db)
    return links

@router.get("/{slug}")
async def redirect_link(slug: str, db: AsyncSession = Depends(get_db)):
    from datetime import datetime, timezone
    
    log.info("redirect_requested", slug=slug)
    link = await db_link.get_link_by_slug(slug, db)
    if not link:
        log.warning("redirect_failed_not_found", slug=slug)
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Link not found")
        
    if not link.is_active:
        log.warning("redirect_failed_inactive", slug=slug)
        raise HTTPException(status_code=status.HTTP_410_GONE, detail="Link is inactive")
        
    if link.expires_at and link.expires_at < datetime.now(timezone.utc):
        log.warning("redirect_failed_expired", slug=slug)
        raise HTTPException(status_code=status.HTTP_410_GONE, detail="Link has expired")
        
    await db_link.increment_click_count(slug, db)
    log.info("redirect_success", slug=slug, original_url=link.original_url)
    return RedirectResponse(url=link.original_url, status_code=status.HTTP_302_FOUND)

@router.get("/{slug}/details", response_model=LinkResponse)
async def get_link_details(slug: str, db: AsyncSession = Depends(get_db)):
    log.info("get_link_details_requested", slug=slug)
    link = await db_link.get_link_by_slug(slug, db)
    if not link:
        log.warning("link_details_not_found", slug=slug)
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Link not found")
    return link

@router.put("/{slug}", response_model=LinkResponse)
async def update_link(slug: str, link_update: LinkUpdate, user_id: int = Depends(get_user_id), db: AsyncSession = Depends(get_db)):
    log.info("update_link_requested", slug=slug, user_id=user_id)
    updated_link = await db_link.update_link(
        slug=slug,
        created_by=user_id,
        db=db,
        new_original_url=link_update.original_url,
        new_description=link_update.description,
        new_is_active=link_update.is_active,
        new_expires_at=link_update.expires_at
    )
    if not updated_link:
        log.warning("update_link_failed_not_found", slug=slug, user_id=user_id)
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Link not found or you are not authorized to update it")
    log.info("update_link_success", slug=slug, user_id=user_id)
    return updated_link

@router.patch("/{slug}/deactivate", response_model=LinkResponse)
async def deactivate_link(slug: str, user_id: int = Depends(get_user_id), db: AsyncSession = Depends(get_db)):
    log.info("deactivate_link_requested", slug=slug, user_id=user_id)
    updated_link = await db_link.update_link(slug=slug, created_by=user_id, db=db, new_is_active=False)
    if not updated_link:
        log.warning("deactivate_link_failed", slug=slug, user_id=user_id)
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Link not found or you are not authorized to update it")
    log.info("deactivate_link_success", slug=slug, user_id=user_id)
    return updated_link

@router.delete("/{slug}", status_code=status.HTTP_200_OK)
async def delete_link(slug: str, user_id: int = Depends(get_user_id), db: AsyncSession = Depends(get_db)):
    log.info("delete_link_requested", slug=slug, user_id=user_id)
    success = await db_link.delete_link(slug=slug, created_by=user_id, db=db)
    if not success:
        log.warning("delete_link_failed", slug=slug, user_id=user_id)
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Link not found or you are not authorized to delete it")
    log.info("delete_link_success", slug=slug, user_id=user_id)
    return {"detail": "Link deleted successfully"}
