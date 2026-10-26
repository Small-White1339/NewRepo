"""Pydantic schemas for Resume CRUD operations."""

from datetime import date, datetime
from uuid import UUID

from pydantic import BaseModel

# ---------- Sub-model Schemas ----------


class EducationSchema(BaseModel):
    """Education entry."""

    id: int | None = None
    school: str
    degree: str | None = None
    field: str | None = None
    start_date: date | None = None
    end_date: date | None = None
    description: str | None = None

    model_config = {"from_attributes": True}


class SkillSchema(BaseModel):
    """Skill entry."""

    id: int | None = None
    name: str
    level: str | None = None
    category: str | None = None

    model_config = {"from_attributes": True}


class ProjectSchema(BaseModel):
    """Project entry."""

    id: int | None = None
    name: str
    role: str | None = None
    description: str | None = None
    tech_stack: list[str] | None = None
    start_date: date | None = None
    end_date: date | None = None
    url: str | None = None

    model_config = {"from_attributes": True}


class WorkExperienceSchema(BaseModel):
    """Work experience entry."""

    id: int | None = None
    company: str
    title: str
    description: str | None = None
    start_date: date | None = None
    end_date: date | None = None
    is_current: bool = False

    model_config = {"from_attributes": True}


class CertificateSchema(BaseModel):
    """Certificate entry."""

    id: int | None = None
    name: str
    issuer: str | None = None
    issued_date: date | None = None
    url: str | None = None

    model_config = {"from_attributes": True}


# ---------- Request Schemas ----------


class ResumeUploadResponse(BaseModel):
    """Response after uploading a resume."""

    id: UUID
    title: str
    status: str
    message: str = "Resume uploaded successfully. Parsing in progress."

    model_config = {"from_attributes": True}


class ResumeUpdateRequest(BaseModel):
    """Request to update resume metadata."""

    title: str | None = None


# ---------- Response Schemas ----------


class ResumeResponse(BaseModel):
    """Full resume detail response."""

    id: UUID
    user_id: UUID
    title: str
    source_name: str | None = None
    source_url: str | None = None
    imported_at: datetime | None = None
    file_path: str
    raw_text: str | None = None
    parsed_data: dict | None = None
    status: str
    created_at: datetime
    updated_at: datetime
    educations: list[EducationSchema] = []
    skills: list[SkillSchema] = []
    projects: list[ProjectSchema] = []
    work_experiences: list[WorkExperienceSchema] = []
    certificates: list[CertificateSchema] = []

    model_config = {"from_attributes": True}


class ResumeListItem(BaseModel):
    """Resume list item (summary)."""

    id: UUID
    title: str
    source_name: str | None = None
    source_url: str | None = None
    imported_at: datetime | None = None
    status: str
    created_at: datetime

    model_config = {"from_attributes": True}
