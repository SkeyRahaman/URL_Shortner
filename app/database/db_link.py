import string
import random
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import update
from .models import Link
from config import Config
from datetime import datetime, timezone
from app.utils.logger import log

def generate_slug(original_url: str) -> str:
    """Generate a random slug. (In production, could hash or base62 encode)."""
    chars = string.ascii_letters + string.digits
    return ''.join(random.choice(chars) for _ in range(Config.SLUG_LENGTH))

async def create_link(original_url: str, description: str | None, created_by: int, db: AsyncSession, 
                      custom_slug: str | None = None, expires_at: datetime | None = None) -> Link:
    """Create a new link. Supports optional custom alias and expiration."""
    slug = custom_slug if custom_slug else generate_slug(original_url)
    is_custom = custom_slug is not None
    
    new_link = Link(
        slug=slug,
        original_url=original_url,
        description=description,
        created_by=created_by,
        is_custom_alias=is_custom,
        expires_at=expires_at
    )
    db.add(new_link)
    await db.commit()
    await db.refresh(new_link)
    log.debug("db_link_created", slug=slug, created_by=created_by)
    return new_link

async def get_link_by_slug(slug: str, db: AsyncSession, include_deleted: bool = False) -> Link | None:
    """Fetch active, non-expired link by slug."""
    query = select(Link).filter(Link.slug == slug)
    if not include_deleted:
        query = query.filter(Link.is_deleted == False)
    result = await db.execute(query)
    link = result.scalars().first()
    log.debug("db_get_link_by_slug", slug=slug, found=link is not None, include_deleted=include_deleted)
    return link

async def get_links_by_user(created_by: int, skip: int, limit: int, db: AsyncSession) -> list[Link]:
    """Paginated list of user's links."""
    result = await db.execute(
        select(Link).filter(Link.created_by == created_by, Link.is_deleted == False).offset(skip).limit(limit)
    )
    links = list(result.scalars().all())
    log.debug("db_get_links_by_user", created_by=created_by, count=len(links))
    return links

async def update_link(slug: str, created_by: int, db: AsyncSession, 
                      new_original_url: str | None = None, new_description: str | None = None, 
                      new_is_active: bool | None = None, new_expires_at: datetime | None = None) -> Link | None:
    """Partial update — only provided fields are changed."""
    result = await db.execute(select(Link).filter(Link.slug == slug, Link.created_by == created_by, Link.is_deleted == False))
    link = result.scalars().first()
    if not link:
        log.debug("db_update_link_not_found", slug=slug, created_by=created_by)
        return None
        
    if new_original_url is not None:
        link.original_url = new_original_url
    if new_description is not None:
        link.description = new_description
    if new_is_active is not None:
        link.is_active = new_is_active
    if new_expires_at is not None:
        link.expires_at = new_expires_at
        
    await db.commit()
    await db.refresh(link)
    log.debug("db_update_link_success", slug=slug, created_by=created_by)
    return link

async def delete_link(slug: str, created_by: int, db: AsyncSession) -> bool:
    """Soft delete a link."""
    result = await db.execute(select(Link).filter(Link.slug == slug, Link.created_by == created_by, Link.is_deleted == False))
    link = result.scalars().first()
    if not link:
        log.debug("db_delete_link_not_found", slug=slug, created_by=created_by)
        return False
    link.is_deleted = True
    await db.commit()
    log.debug("db_delete_link_success", slug=slug, created_by=created_by)
    return True

async def increment_click_count(slug: str, db: AsyncSession) -> None:
    """Atomically increment total_clicks."""
    await db.execute(
        update(Link).where(Link.slug == slug, Link.is_deleted == False).values(total_clicks=Link.total_clicks + 1)
    )
    await db.commit()
    log.debug("db_increment_click_count", slug=slug)
