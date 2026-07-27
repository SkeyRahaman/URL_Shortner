from app.database.models import Link
from datetime import datetime, timezone

def test_link_model_instantiation():
    link = Link(slug="abc", original_url="https://google.com", created_by=1)
    assert link.slug == "abc"
    assert link.original_url == "https://google.com"
    assert link.created_by == 1
