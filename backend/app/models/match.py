"""职位-简历匹配结果的匹配报告模型。"""

import enum
from datetime import datetime
from uuid import UUID, uuid4

from sqlalchemy import DateTime, Enum, Float, ForeignKey, func
from sqlalchemy import JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class MatchStatus(str, enum.Enum):
    """匹配分析状态。"""

    PENDING = "PENDING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"


class MatchReport(Base):
    __tablename__ = "match_reports"

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    resume_id: Mapped[UUID] = mapped_column(ForeignKey("resumes.id"), nullable=False, index=True)
    job_id: Mapped[UUID] = mapped_column(ForeignKey("jobs.id"), nullable=False, index=True)
    overall_score: Mapped[float | None] = mapped_column(Float, nullable=True)
    result_data: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    status: Mapped[MatchStatus] = mapped_column(
        Enum(MatchStatus, name="match_status"), nullable=False, default=MatchStatus.PENDING
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

    # 关联关系
    resume = relationship("Resume", back_populates="match_reports")
    job = relationship("Job", back_populates="match_reports")

    def __repr__(self):
        return f"<MatchReport resume={self.resume_id} job={self.job_id} score={self.overall_score}>"
