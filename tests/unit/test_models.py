from app.database.models import DBUser, DBUrl

def test_create_user(db_session):
    user = DBUser(
        user_name="testuser",
        email="testuser@example.com",
        password="securepassword123"
    )
    db_session.add(user)
    db_session.commit()

    retrieved_user = db_session.query(DBUser).filter_by(email="testuser@example.com").first()
    assert retrieved_user is not None
    assert retrieved_user.user_name == "testuser"

def test_create_url_for_user(db_session):
    user = DBUser(
        user_name="urltester",
        email="urltester@example.com",
        password="123test"
    )
    db_session.add(user)
    db_session.commit()

    url = DBUrl(
        long_url="https://example.com",
        short_url="abc123",
        description="Test URL",
        user_id=user.id
    )
    db_session.add(url)
    db_session.commit()

    retrieved_url = db_session.query(DBUrl).filter_by(short_url="abc123").first()
    assert retrieved_url is not None
    assert retrieved_url.long_url == "https://example.com"
    assert retrieved_url.user_id == user.id

def test_user_url_relationship(db_session):
    user = DBUser(
        user_name="reluser",
        email="reluser@example.com",
        password="pass123"
    )
    db_session.add(user)
    db_session.commit()

    url1 = DBUrl(long_url="https://site1.com", short_url="u1", user_id=user.id)
    url2 = DBUrl(long_url="https://site2.com", short_url="u2", user_id=user.id)

    db_session.add_all([url1, url2])
    db_session.commit()

    db_session.refresh(user)
    assert len(user.urls) == 2
    assert {u.short_url for u in user.urls} == {"u1", "u2"}
