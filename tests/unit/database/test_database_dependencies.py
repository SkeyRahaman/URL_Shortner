import pytest
from app.database.dependencies import get_db

@pytest.mark.asyncio
async def test_get_db_yields_session():
    # get_db is an async generator. We need to get the yielded value.

    gen = get_db()  # This returns an async generator
    
    # Get the first yielded value - the session
    session = await gen.__anext__()
    
    from sqlalchemy.ext.asyncio import AsyncSession
    # Check that the yielded object is an instance of AsyncSession
    assert isinstance(session, AsyncSession)
    
    # Close the generator (which triggers cleanup code after yield)
    with pytest.raises(StopAsyncIteration):
        await gen.__anext__()
