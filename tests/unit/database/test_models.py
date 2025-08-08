import pytest
from app.database.models import DBUser, DBUrl

@pytest.mark.usefixtures("setup_database")
class TestDBModels:
    def test_user_model_basic_attributes(self, db_session):
        user = DBUser(user_name="testuser", email="test@example.com", password="hashedpass")
        db_session.add(user)
        db_session.commit()
        db_session.refresh(user)

        assert user.id is not None
        assert user.user_name == "testuser"
        assert user.email == "test@example.com"
        assert user.password == "hashedpass"

    def test_url_model_basic_attributes_and_relationship(self, db_session):
        user = DBUser(user_name="urlowner", email="url@owner.com", password="hashedpass")
        db_session.add(user)
        db_session.commit()
        db_session.refresh(user)

        url = DBUrl(
            long_url="https://example.com",
            short_url="exmpl",
            description="Example URL",
            user_id=user.id
        )
        db_session.add(url)
        db_session.commit()
        db_session.refresh(url)

        assert url.id is not None
        assert url.long_url == "https://example.com"
        assert url.short_url == "exmpl"
        assert url.description == "Example URL"
        assert url.user_id == user.id

        # Relationship checks
        assert url.user == user
        assert url in user.urls

    def test_user_urls_relationship_addition(self, db_session):
        user = DBUser(user_name="reluser", email="rel@user.com", password="hashed")
        url1 = DBUrl(long_url="https://a.com", short_url="a", description="", user=user)
        url2 = DBUrl(long_url="https://b.com", short_url="b", description="", user=user)

        db_session.add(user)
        db_session.add(url1)
        db_session.add(url2)
        db_session.commit()

        db_session.refresh(user)
        db_session.refresh(url1)
        db_session.refresh(url2)

        assert len(user.urls) == 2
        assert url1 in user.urls
        assert url2 in user.urls
