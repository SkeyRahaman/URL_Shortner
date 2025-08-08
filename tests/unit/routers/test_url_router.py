import pytest
from unittest.mock import AsyncMock, patch
from fastapi import status
from fastapi.responses import RedirectResponse

from app.routers import urls  
from app.database import db_url

@pytest.mark.asyncio
class TestUrlsRouter:

    async def test_create_short_url_success(self, mock_db, mock_db_user, mock_url_display):
        with patch.object(db_url, "add_url", AsyncMock(return_value=mock_url_display)) as mock_add_url:
            result = await urls.create_short_url(
                url=mock_url_display.long_url,
                description=mock_url_display.description,
                db=mock_db,
                user=mock_db_user
            )
            mock_add_url.assert_awaited_once_with(
                long_url=mock_url_display.long_url,
                description=mock_url_display.description,
                user_id=mock_db_user.id,
                db=mock_db
            )
            assert result == mock_url_display

    async def test_redirect_short_url_success(self, mock_db, mock_url_display):
        with patch.object(db_url, "get_url", AsyncMock(return_value=mock_url_display)) as mock_get_url:
            response = await urls.redirect_short_url(short_url=mock_url_display.short_url, db=mock_db)
            mock_get_url.assert_awaited_once_with(short_url=mock_url_display.short_url, db=mock_db)
            assert isinstance(response, RedirectResponse)
            assert response.status_code == status.HTTP_302_FOUND
            assert response.headers["location"] == mock_url_display.long_url

    async def test_get_short_url_details_success(self, mock_db, mock_url_display):
        with patch.object(db_url, "get_url", AsyncMock(return_value=mock_url_display)) as mock_get_url:
            result = await urls.get_short_url_details(short_url=mock_url_display.short_url, db=mock_db)
            mock_get_url.assert_awaited_once_with(short_url=mock_url_display.short_url, db=mock_db)
            assert result == mock_url_display

    async def test_list_urls_success(self, mock_db, mock_db_user, mock_url_display):
        url_list = [mock_url_display]
        with patch.object(db_url, "get_user_urls", AsyncMock(return_value=url_list)) as mock_get_user_urls:
            result = await urls.list_urls(
                skip=0,
                limit=10,
                db=mock_db,
                user=mock_db_user
            )
            mock_get_user_urls.assert_awaited_once_with(user_id=mock_db_user.id, skip=0, limit=10, db=mock_db)
            assert result == url_list

    async def test_update_url_success(self, mock_db, mock_db_user, mock_url_data_update, mock_url_display):
        with patch.object(db_url, "update_url", AsyncMock(return_value=mock_url_display)) as mock_update_url:
            result = await urls.update_url(
                url_data=mock_url_data_update,
                db=mock_db,
                user=mock_db_user
            )
            mock_update_url.assert_awaited_once_with(
                short_url=mock_url_data_update.short_url,
                new_long_url=mock_url_data_update.long_url,
                new_description=mock_url_data_update.description,
                user_id=mock_db_user.id,
                db=mock_db
            )
            assert result == mock_url_display

    async def test_delete_url_success(self, mock_db, mock_db_user):
        with patch.object(db_url, "delete_url", AsyncMock(return_value={"Message": "URL Deleted."})) as mock_delete_url:
            response = await urls.delete_url(
                short_url="abc123",
                db=mock_db,
                user=mock_db_user
            )
            mock_delete_url.assert_awaited_once_with(short_url="abc123", user_id=mock_db_user.id, db=mock_db)
            assert response == {"Message": "URL Deleted."}
