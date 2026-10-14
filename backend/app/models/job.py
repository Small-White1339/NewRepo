"""职位模型及相关子模型。"""

import enum
from datetime import datetime
from uuid import UUID, uuid4

from sqlalchemy import DateTime, Enum, ForeignKey, Integer, String, Text, func
from sqlalchemy import JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class JobStatus(str, enum.Enum):
    """职位发布状态。"""

    DRAFT = "DRAFT"
    ACTIVE = "ACTIVE"
    CLOSED = "CLOSED"


class JobLevel(str, enum.Enum):
    """职位职级。"""

    JUNIOR = "JUNIOR"
    INTERMEDIATE = "INTERMEDIATE"
    SENIOR = "SENIOR"
    EXPERT = "EXPERT"


class RequirementCategory(str, enum.Enum):
    """职位要求类别。"""

    SKILL = "SKILL"
    EDUCATION = "EDUCATION"
    EXPERIENCE = "EXPERIENCE"
    PROJECT = "PROJECT"


class Job(Base):
    __tablename__ = "jobs"

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    user_id: Mapped[UUID] = mapped_column(ForeignKey("users.id"), nullable=False, index=True)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    company: Mapped[str] = mapped_column(String(255), nullable=False)
    raw_description: Mapped[str | None] = mapped_column(Text, nullable=True)
    structured_data: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    status: Mapped[JobStatus] = mapped_column(
        Enum(JobStatus, name="job_status"), nullable=False, default=JobStatus.DRAFT
    )
    level: Mapped[JobLevel] = mapped_column(
        Enum(JobLevel, name="job_level"), nullable=False, default=JobLevel.INTERMEDIATE
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    # 关联关系
    user = relationship("User", back_populates="jobs")
    requirements = relationship(
        "JobRequirement", back_populates="job", cascade="all, delete-orphan"
    )
    match_reports = relationship(
        "MatchReport", back_populates="job", cascade="all, delete-orphan"
    )

    def __repr__(self):
        return f"<Job {self.title} @ {self.company}>"


class JobRequirement(Base):
    __tablename__ = "job_requirements"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    job_id: Mapped[UUID] = mapped_column(ForeignKey("jobs.id"), nullable=False, index=True)
    category: Mapped[RequirementCategory] = mapped_column(
        Enum(RequirementCategory, name="requirement_category"), nullable=False
    )
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    importance: Mapped[int] = mapped_column(Integer, default=5)
    is_mandatory: Mapped[bool] = mapped_column(default=False)

    # 关联关系
    job = relationship("Job", back_populates="requirements")

    def __repr__(self):
        return f"<JobRequirement {self.category.value}:{self.name}>"
