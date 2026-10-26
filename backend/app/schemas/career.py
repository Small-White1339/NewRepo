"""求职者岗位、收藏、匹配请求与响应。"""

from datetime import datetime, timezone
from typing import Literal
from uuid import UUID

from pydantic import BaseModel, Field, field_validator

from app.models.job import JobLevel, JobStatus
from app.schemas.match import MatchReportResponse

CareerStage = Literal["SAVED", "APPLIED", "INTERVIEW", "OFFER", "ARCHIVED"]


def utc_datetime(value: datetime | None) -> datetime | None:
    """SQLite 返回无时区的 UTC 时间，补齐时区供浏览器正确换算。"""
    if value is not None and value.tzinfo is None:
        return value.replace(tzinfo=timezone.utc)
    return value


class CareerJob(BaseModel):
    id: UUID
    title: str
    company: str
    raw_description: str | None = None
    level: JobLevel
    status: JobStatus
    source_name: str | None = None
    source_url: str | None = None
    imported_at: datetime | None = None
    created_at: datetime

    model_config = {"from_attributes": True}
    _timestamps = field_validator("created_at", "imported_at")(utc_datetime)


class SaveJobRequest(BaseModel):
    stage: CareerStage = "SAVED"
    notes: str = Field(default="", max_length=4000)


class SavedJobResponse(BaseModel):
    job: CareerJob
    stage: CareerStage
    notes: str
    updated_at: datetime
    _timestamps = field_validator("updated_at")(utc_datetime)


class CareerAnalyzeRequest(BaseModel):
    resume_id: UUID
    job_id: UUID


class CareerReportResponse(MatchReportResponse):
    job_title: str
    company: str
    resume_title: str
    _timestamps = field_validator("created_at")(utc_datetime)
