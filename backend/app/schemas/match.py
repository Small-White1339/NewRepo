"""Pydantic schemas for MatchReport operations."""

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field

# ---------- Request Schemas ----------

class MatchAnalyzeRequest(BaseModel):
    """Request to analyze match between resumes and a job."""
    resume_ids: list[UUID] = Field(
        ..., min_length=1, max_length=20,
        description="Resume IDs to analyze (min 1, max 20)",
    )
    job_id: UUID = Field(..., description="Job ID to match against")


# ---------- Response Schemas ----------

class MatchResultData(BaseModel):
    """Full pipeline result stored as JSONB in match reports.
    Matches the OrchestratorResult.to_dict() output format.
    """
    resume_analysis: dict | None = None
    job_analysis: dict | None = None
    match_result: dict | None = None
    report: dict | None = None


class MatchReportResponse(BaseModel):
    """Match report detail response."""
    id: UUID
    resume_id: UUID
    job_id: UUID
    overall_score: float | None = None
    result_data: dict | None = None
    status: str
    created_at: datetime

    model_config = {"from_attributes": True}


class MatchReportListItem(BaseModel):
    """Match report list item (summary)."""
    id: UUID
    resume_id: UUID
    job_id: UUID
    overall_score: float | None = None
    status: str
    created_at: datetime

    model_config = {"from_attributes": True}


class MatchAnalyzeBatchResponse(BaseModel):
    """Batch analyze response wrapping multiple match reports."""
    results: list[MatchReportResponse]
    total: int
    succeeded: int
    failed: int
