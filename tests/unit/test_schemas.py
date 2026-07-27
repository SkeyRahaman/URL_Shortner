import pytest
from app.schemas import LinkCreate, LinkUpdate

def test_link_create_schema_valid():
    schema = LinkCreate(original_url="https://google.com")
    assert schema.original_url == "https://google.com"

def test_link_create_schema_custom_slug():
    schema = LinkCreate(original_url="https://google.com", custom_slug="my-brand")
    assert schema.custom_slug == "my-brand"

def test_link_update_schema():
    schema = LinkUpdate(is_active=False)
    assert schema.is_active is False
    assert schema.original_url is None
