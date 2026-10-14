"""Pydantic schemas for Job CRUD operations."""

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field

# ---------- Sub-model Schemas ----------

class JobRequirementSchema(BaseModel):
    """Job requirement entry."""
    id: int | None = None
    category: str
    name: str
    description: str | None = None
    importance: int = 5
    is_mandatory: bool = False

    model_config = {"from_attributes": True}


# ---------- Request Schemas ----------

class JobCreateRequest(BaseModel):
    """Job creation request body."""
    title: str = Field(..., min_length=1, max_length=255)
    company: str = Field(..., min_length=1, max_length=255)
    raw_description: str = Field(..., description="Job description text")
    level: str = "INTERMEDIATE"


class JobUpdateRequest(BaseModel):
    """Job update request body."""
    title: str | None = None
    company: str | None = None
    raw_description: str | None = None
    level: str | None = None
    status: str | None = None


# ---------- Response Schemas ----------

class JobResponse(BaseModel):
    """Full job detail response."""
    id: UUID
    user_id: UUID
    title: str
    company: str
    level: str
    raw_description: str | None = None
    structured_data: dict | None = None
    status: str
    created_at: datetime
    updated_at: datetime
    requirements: list[JobRequirementSchema] = []

    model_config = {"from_attributes": True}


class JobListItem(BaseModel):
    """Job list item (summary)."""
    id: UUID
    title: str
    company: str
    level: str
    status: str
    created_at: datetime

    model_config = {"from_attributes": True}
