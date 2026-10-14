"""Pydantic schemas for API request/response validation."""

from app.schemas.job import (
    JobCreateRequest,
    JobListItem,
    JobRequirementSchema,
    JobResponse,
    JobUpdateRequest,
)
from app.schemas.match import (
    MatchAnalyzeRequest,
    MatchReportListItem,
    MatchReportResponse,
    MatchResultData,
)
from app.schemas.resume import (
    CertificateSchema,
    EducationSchema,
    ProjectSchema,
    ResumeListItem,
    ResumeResponse,
    ResumeUploadResponse,
    SkillSchema,
    WorkExperienceSchema,
)
from app.schemas.user import (
    TokenPayload,
    TokenResponse,
    UserLoginRequest,
    UserRegisterRequest,
    UserResponse,
    UserUpdateRequest,
)

__all__ = [
    "CertificateSchema",
    "EducationSchema",
    "JobCreateRequest",
    "JobListItem",
    "JobRequirementSchema",
    "JobResponse",
    "JobUpdateRequest",
    "MatchAnalyzeRequest",
    "MatchReportListItem",
    "MatchReportResponse",
    "MatchResultData",
    "ProjectSchema",
    "ResumeListItem",
    "ResumeResponse",
    "ResumeUploadResponse",
    "SkillSchema",
    "TokenPayload",
    "TokenResponse",
    "UserLoginRequest",
    "UserRegisterRequest",
    "UserResponse",
    "UserUpdateRequest",
    "WorkExperienceSchema",
]
