import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from fastapi.exceptions import HTTPException
from fastapi import status

from app.database import db_url  # Adjust this import to your actual file path
from app.database.models import DBUrl
from config import Config

@pytest.mark.asyncio
class TestDBUrlFunctions:

    async def test_generate_short_code(self):
        url = "https://example.com"
        short_code = db_url.generate_short_code(url)
        # Should be a string of expected length
        assert isinstance(short_code, str)
        assert len(short_code) == Config.SHORT_URL_LENGTH

    async def test_add_url_success(self, mock_db, sample_dburl):
        long_url = "https://example.com"
        user_id = 42
        description = "Test URL"

        # We patch DBUrl constructor to create sample_dburl with provided args to verify properties
        with patch("app.database.db_url.DBUrl", return_value=sample_dburl) as mock_dburl_class:
            mock_db.add = MagicMock()
            mock_db.commit = AsyncMock()
            mock_db.refresh = AsyncMock()

            result = await db_url.add_url(long_url, mock_db, user_id, description)

            mock_dburl_class.assert_called_once_with(
                long_url=long_url,
                short_url=db_url.generate_short_code(long_url),
                description=description,
                user_id=user_id
            )
            mock_db.add.assert_called_once_with(sample_dburl)
            mock_db.commit.assert_awaited_once()
            mock_db.refresh.assert_awaited_once_with(sample_dburl)
            assert result == sample_dburl

    async def test_get_url_found(self, mock_db, sample_dburl):
        # Mock DB execute().scalars().first() returning sample_dburl
        mock_scalar_result = MagicMock()
        mock_scalar_result.first.return_value = sample_dburl

        mock_result = MagicMock()
        mock_result.scalars.return_value = mock_scalar_result

        mock_db.execute = AsyncMock(return_value=mock_result)

        result = await db_url.get_url(sample_dburl.short_url, mock_db)
        assert result == sample_dburl
        mock_db.execute.assert_awaited_once()

    async def test_get_url_not_found(self, mock_db):
        mock_scalar_result = MagicMock()
        mock_scalar_result.first.return_value = None

        mock_result = MagicMock()
        mock_result.scalars.return_value = mock_scalar_result

        mock_db.execute = AsyncMock(return_value=mock_result)

        response = await db_url.get_url("nonexistent_short_url", mock_db)

        assert response is None

    async def test_get_user_urls(self, mock_db, sample_dburl):
        mock_scalar_result = MagicMock()
        mock_scalar_result.all.return_value = [sample_dburl]

        mock_result = MagicMock()
        mock_result.scalars.return_value = mock_scalar_result

        mock_db.execute = AsyncMock(return_value=mock_result)

        user_id = sample_dburl.user_id
        skip, limit = 0, 10

        result = await db_url.get_user_urls(user_id, skip, limit, mock_db)
        assert result == [sample_dburl]
        mock_db.execute.assert_awaited_once()

    async def test_update_url_success(self, mock_db, sample_dburl):
        # Patch scalars().first() to return a DBUrl
        mock_scalar_result = MagicMock()
        mock_scalar_result.first.return_value = sample_dburl

        mock_result = MagicMock()
        mock_result.scalars.return_value = mock_scalar_result

        mock_db.execute = AsyncMock(return_value=mock_result)
        mock_db.commit = AsyncMock()
        mock_db.refresh = AsyncMock()

        new_long_url = "https://new-url.com"
        new_description = "Updated Description"
        user_id = sample_dburl.user_id
        short_url = sample_dburl.short_url

        updated_url = await db_url.update_url(short_url, new_long_url, new_description, user_id, mock_db)

        assert updated_url.long_url == new_long_url
        assert updated_url.description == new_description
        mock_db.commit.assert_awaited_once()
        mock_db.refresh.assert_awaited_once_with(sample_dburl)

    async def test_update_url_not_found(self, mock_db):
        mock_scalar_result = MagicMock()
        mock_scalar_result.first.return_value = None

        mock_result = MagicMock()
        mock_result.scalars.return_value = mock_scalar_result

        mock_db.execute = AsyncMock(return_value=mock_result)

        response = await db_url.update_url("nonexistent", "url", "desc", 1, mock_db)

        assert response is None

    async def test_delete_url_success(self, mock_db, sample_dburl):
        mock_scalar_result = MagicMock()
        mock_scalar_result.first.return_value = sample_dburl

        mock_result = MagicMock()
        mock_result.scalars.return_value = mock_scalar_result

        mock_db.execute = AsyncMock(return_value=mock_result)
        mock_db.delete = AsyncMock()
        mock_db.commit = AsyncMock()

        response = await db_url.delete_url(sample_dburl.short_url, sample_dburl.user_id, mock_db)

        mock_db.delete.assert_awaited_once_with(sample_dburl)
        mock_db.commit.assert_awaited_once()
        assert response is True

    async def test_delete_url_not_found(self, mock_db):
        mock_scalar_result = MagicMock()
        mock_scalar_result.first.return_value = None

        mock_result = MagicMock()
        mock_result.scalars.return_value = mock_scalar_result

        mock_db.execute = AsyncMock(return_value=mock_result)

        response = await db_url.delete_url("nonexistent_short_url", 1, mock_db)

        assert response is False
