"""Pydantic schemas for Job CRUD operations."""

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field

from app.models.job import JobLevel, JobStatus

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
    level: JobLevel = JobLevel.INTERMEDIATE


class JobUpdateRequest(BaseModel):
    """Job update request body."""

    title: str | None = Field(None, min_length=1, max_length=255)
    company: str | None = Field(None, min_length=1, max_length=255)
    raw_description: str | None = None
    level: JobLevel | None = None
    status: JobStatus | None = None


# ---------- Response Schemas ----------


class JobResponse(BaseModel):
    """Full job detail response."""

    id: UUID
    user_id: UUID
    title: str
    source_name: str | None = None
    source_url: str | None = None
    imported_at: datetime | None = None
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
    source_name: str | None = None
    source_url: str | None = None
    imported_at: datetime | None = None
    company: str
    level: str
    status: str
    created_at: datetime

    model_config = {"from_attributes": True}
