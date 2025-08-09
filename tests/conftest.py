import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from unittest.mock import MagicMock
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession

from app.schemas import UserDetails, UrlDisplay, UrlDataUpdate
from app.database.models import Base, DBUser, DBUrl
from app.database.db_url import generate_short_code
from app.authentication.authentication import JWTTokenManager
from app.authentication.password_hash import PasswordHasher
from app.main import app
from app.database.dependencies import get_db
from config import Config

TEST_DATABASE_URL = "sqlite:///./test_db.db"

# Create engine and sessionmaker for tests
engine = create_engine(TEST_DATABASE_URL, echo=False)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

TEST_ASYNC_DATABASE_URL = "sqlite+aiosqlite:///test_async_db.db"

async_engine = create_async_engine(TEST_ASYNC_DATABASE_URL, echo=False)
AsyncTestingSessionLocal = sessionmaker(
    bind=async_engine, class_=AsyncSession, expire_on_commit=False
)

@pytest.fixture
def mock_db():
    """
    Provides a mocked AsyncSession instance for DB dependency injection.
    """
    return MagicMock(spec=AsyncSession)

@pytest.fixture
def test_token():
    """
    Provides a dummy token string for OAuth2 token dependency.
    """
    return "valid.token.here"

@pytest.fixture
def test_username():
    """
    Provides a test username used in decoded JWT payload.
    """
    return "testuser"

@pytest.fixture
def valid_form_data():
    """
    Provides an OAuth2PasswordRequestForm-like object.
    """
    form = MagicMock(spec=OAuth2PasswordRequestForm)
    form.username = "testuser"
    form.password = "testpass"
    return form

@pytest.fixture
def invalid_form_data():
    """
    Provides an OAuth2PasswordRequestForm-like object with invalid credentials.
    """
    form = MagicMock(spec=OAuth2PasswordRequestForm)
    form.username = "invaliduser"
    form.password = "wrongpass"
    return form

@pytest.fixture(scope="module", autouse=True)
def setup_database():
    # Create tables before any test runs
    Base.metadata.create_all(bind=engine)
    yield
    # Drop tables after all tests in module are done
    Base.metadata.drop_all(bind=engine)

@pytest.fixture()
def db_session():
    """
    Creates a new database session for a test.
    Rolls back and closes session after test to isolate tests.
    """
    session = TestingSessionLocal()
    try:
        yield session
        session.rollback()
    finally:
        session.close()

@pytest.fixture
def fake_user_details():
    """Sample UserDetails input for create_user."""
    return UserDetails(user_name="testuser", email="test@example.com", password="securepass")

@pytest.fixture
def mock_db_user():
    """Mocked DBUser-like object."""
    mock_user = MagicMock()
    mock_user.id = 123
    mock_user.user_name = "testuser"
    mock_user.email = "test@example.com"
    mock_user.password = "hashedpassword"
    return mock_user

@pytest.fixture
def sample_dburl():
    """
    A mock DBUrl object for reuse in tests.
    """
    mock_url = MagicMock()
    mock_url.id = 1
    mock_url.long_url = "https://example.com"
    mock_url.short_url = "abc123"
    mock_url.description = "Example description"
    mock_url.user_id = 42
    return mock_url

@pytest.fixture
def mock_url_display():
    """Mock UrlDisplay instance for return values."""
    url = MagicMock(spec=UrlDisplay)
    url.short_url = "abc123"
    url.long_url = "https://example.com"
    url.description = "Test URL"
    url.user_id = 1
    return url

@pytest.fixture
def mock_url_data_update():
    """Mock UrlDataUpdate instance for updating URL data."""
    data = MagicMock(spec=UrlDataUpdate)
    data.short_url = "abc123"
    data.long_url = "https://new-url.com"
    data.description = "Updated description"
    return data

#integration test
@pytest_asyncio.fixture(scope="module", autouse=True)
async def setup_async_database():
    async with async_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with async_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    await async_engine.dispose()

@pytest_asyncio.fixture()
async def async_db_session():
    async with AsyncTestingSessionLocal() as session:
        yield session
        await session.rollback()

@pytest_asyncio.fixture
async def test_user(async_db_session: AsyncSession):
    user = DBUser(
        user_name=Config.TEST_USER['username'],
        email=Config.TEST_USER['email'],
        password=PasswordHasher.get_password_hash(Config.TEST_USER['password']),
    )
    async_db_session.add(user)  # no await here because add is sync
    await async_db_session.commit()
    await async_db_session.refresh(user)
    yield user
    await async_db_session.delete(user)
    await async_db_session.commit()

@pytest_asyncio.fixture
async def auth_token(test_user):
    return JWTTokenManager.create_access_token(data={"sub": test_user.user_name})

@pytest_asyncio.fixture
async def async_client():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac

@pytest_asyncio.fixture
async def override_get_db(async_db_session):
    # Provide the same db session as in test_user fixture
    async def _override_get_db():
        yield async_db_session
    app.dependency_overrides[get_db] = _override_get_db
    yield
    app.dependency_overrides.pop(get_db, None)

@pytest_asyncio.fixture
async def test_url(async_db_session: AsyncSession, test_user: DBUser):
    url = DBUrl(
        long_url = Config.TEST_URL['url'],
        short_url = generate_short_code(Config.TEST_URL['url']),
        description = Config.TEST_URL['description'],
        user_id = test_user.id
    )
    async_db_session.add(url)
    await async_db_session.commit()
    await async_db_session.refresh(url)
    yield url
    await async_db_session.delete(url)
    await async_db_session.commit()
