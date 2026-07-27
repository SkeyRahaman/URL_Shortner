import pytest
from app.database import db_link
from datetime import datetime, timezone, timedelta

@pytest.mark.asyncio
async def test_create_link(db_session):
    link = await db_link.create_link("https://example.com", "desc", 1, db_session)
    assert link.slug is not None
    assert link.original_url == "https://example.com"
    assert link.is_custom_alias is False

@pytest.mark.asyncio
async def test_get_link_by_slug(db_session, test_link):
    link = await db_link.get_link_by_slug(test_link.slug, db_session)
    assert link is not None
    assert link.id == test_link.id

@pytest.mark.asyncio
async def test_update_link(db_session, test_link):
    link = await db_link.update_link(test_link.slug, 1, db_session, new_description="new desc")
    assert link.description == "new desc"

@pytest.mark.asyncio
async def test_delete_link(db_session, test_link):
    success = await db_link.delete_link(test_link.slug, 1, db_session)
    assert success is True
    link = await db_link.get_link_by_slug(test_link.slug, db_session)
    assert link is None

@pytest.mark.asyncio
async def test_increment_click_count(db_session, test_link):
    await db_link.increment_click_count(test_link.slug, db_session)
    link = await db_link.get_link_by_slug(test_link.slug, db_session)
    assert link.total_clicks == 1
