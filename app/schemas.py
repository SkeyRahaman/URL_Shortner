from pydantic import BaseModel, Field, ConfigDict, HttpUrl
from datetime import datetime

class LinkCreate(BaseModel):
    """Request body for creating a link."""
    original_url: str
    description: str | None = Field(None, max_length=400)
    custom_slug: str | None = Field(None, max_length=50, pattern=r'^[a-zA-Z0-9_-]+$')
    expires_at: datetime | None = None

class LinkUpdate(BaseModel):
    """Request body for updating a link. All fields optional (partial update)."""
    original_url: str | None = None
    description: str | None = Field(None, max_length=400)
    is_active: bool | None = None
    expires_at: datetime | None = None

class LinkResponse(BaseModel):
    """Response model for a link."""
    id: int
    slug: str
    original_url: str
    description: str | None
    is_custom_alias: bool
    is_active: bool
    is_deleted: bool
    total_clicks: int
    expires_at: datetime | None
    created_by: int
    created_at: datetime
    updated_at: datetime
    model_config = ConfigDict(from_attributes=True)