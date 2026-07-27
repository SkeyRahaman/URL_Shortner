import pytest
from fastapi import HTTPException
from app.dependencies.header_auth import get_user_id

@pytest.mark.asyncio
async def test_get_user_id_valid():
    user_id = await get_user_id(123)
    assert user_id == 123

@pytest.mark.asyncio
async def test_get_user_id_invalid():
    with pytest.raises(HTTPException) as exc:
        await get_user_id(0)
    assert exc.value.status_code == 400
