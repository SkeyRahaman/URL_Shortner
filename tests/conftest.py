# conftest.py
import os
print(os.curdir)
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from jose import jwt

from app.database import get_db
from app.database.hash import PasswordHasher
from app.main import app
from app.database.models import Base, DBUser
from config import Config as settings

# Database setup
TEST_DB_URL = "sqlite:///./test.db"
engine = create_engine(TEST_DB_URL)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Fixtures
@pytest.fixture(scope="module")
def db_session():
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    yield db
    db.close()
    Base.metadata.drop_all(bind=engine)

@pytest.fixture(scope="module")
def client(db_session):
    def override_get_db():
        yield db_session
    app.dependency_overrides[get_db] = override_get_db
    return TestClient(app)

@pytest.fixture
def test_user(db_session):
    user = DBUser(
        user_name = settings.TEST_USER['username'],
        email = settings.TEST_USER['email'],
        password = PasswordHasher.get_password_hash(settings.TEST_USER['password'],)
    )
    db_session.add(user)
    db_session.commit()
    return user

@pytest.fixture
def auth_token(test_user):
    return jwt.encode({"sub": test_user.user_name}, settings.SECRET_KEY, algorithm=settings.ALGORITHM)

@pytest.fixture
def auth_headers(auth_token):
    return {"Authorization": f"Bearer {auth_token}"}