"""求职者浏览在招岗位、保存进度、分析自己的简历。"""

from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query
from loguru import logger
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.api.deps import get_current_job_seeker, get_db
from app.config import settings
from app.models.career import SavedJob
from app.models.job import Job, JobLevel, JobStatus
from app.models.match import MatchReport, MatchStatus
from app.models.resume import Resume
from app.models.user import User
from app.schemas.career import (
    CareerAnalyzeRequest,
    CareerJob,
    CareerReportResponse,
    SavedJobResponse,
    SaveJobRequest,
)

router = APIRouter(dependencies=[Depends(get_current_job_seeker)])


async def active_job(db: AsyncSession, job_id: UUID) -> Job:
    job = await db.scalar(select(Job).where(Job.id == job_id, Job.status == JobStatus.ACTIVE))
    if job is None:
        raise HTTPException(status_code=404, detail="岗位不存在或已停止招聘。")
    return job


def saved_response(saved: SavedJob) -> SavedJobResponse:
    return SavedJobResponse(
        job=CareerJob.model_validate(saved.job),
        stage=saved.stage,
        notes=saved.notes,
        updated_at=saved.updated_at,
    )


def report_response(report: MatchReport, job: Job, resume: Resume) -> CareerReportResponse:
    return CareerReportResponse(
        id=report.id,
        resume_id=report.resume_id,
        job_id=report.job_id,
        overall_score=report.overall_score,
        result_data=report.result_data,
        status=report.status.value,
        created_at=report.created_at,
        job_title=job.title,
        company=job.company,
        resume_title=resume.title,
    )


@router.get("/jobs", response_model=list[CareerJob])
async def browse_jobs(
    q: str = Query("", max_length=200),
    level: JobLevel | None = None,
    db: AsyncSession = Depends(get_db),
):
    """只公开在招岗位，按来源链接合并多个 HR 导入的相同岗位。"""
    stmt = select(Job).where(Job.status == JobStatus.ACTIVE)
    if q.strip():
        pattern = f"%{q.strip()}%"
        stmt = stmt.where(
            Job.title.ilike(pattern)
            | Job.company.ilike(pattern)
            | Job.raw_description.ilike(pattern)
        )
    if level:
        stmt = stmt.where(Job.level == level)
    jobs = (await db.scalars(stmt.order_by(Job.created_at.desc(), Job.id))).all()
    seen = set()
    unique = []
    for job in jobs:
        identity = job.source_url or str(job.id)
        if identity not in seen:
            seen.add(identity)
            unique.append(job)
    return unique


@router.get("/jobs/{job_id}", response_model=CareerJob)
async def get_career_job(
    job_id: UUID,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_job_seeker),
):
    job = await db.scalar(select(Job).where(Job.id == job_id))
    saved = await db.scalar(
        select(SavedJob.id).where(SavedJob.job_id == job_id, SavedJob.user_id == user.id)
    )
    if (
        job is None
        or job.status == JobStatus.DRAFT
        or (job.status != JobStatus.ACTIVE and not saved)
    ):
        raise HTTPException(status_code=404, detail="岗位不存在或已停止招聘。")
    return job


@router.get("/saved", response_model=list[SavedJobResponse])
async def list_saved(
    db: AsyncSession = Depends(get_db), user: User = Depends(get_current_job_seeker)
):
    rows = await db.scalars(
        select(SavedJob)
        .join(Job)
        .options(selectinload(SavedJob.job))
        .where(SavedJob.user_id == user.id, Job.status != JobStatus.DRAFT)
        .order_by(SavedJob.updated_at.desc())
    )
    return [saved_response(row) for row in rows]


@router.put("/saved/{job_id}", response_model=SavedJobResponse)
async def save_job(
    job_id: UUID,
    body: SaveJobRequest,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_job_seeker),
):
    saved = await db.scalar(
        select(SavedJob)
        .options(selectinload(SavedJob.job))
        .where(SavedJob.user_id == user.id, SavedJob.job_id == job_id)
    )
    if saved is None:
        job = await active_job(db, job_id)
        saved = SavedJob(user_id=user.id, job_id=job.id, stage=body.stage, notes=body.notes)
        db.add(saved)
    else:
        if saved.job.status == JobStatus.DRAFT:
            raise HTTPException(status_code=404, detail="该岗位已撤回。")
        saved.stage, saved.notes = body.stage, body.notes
    await db.flush()
    await db.refresh(saved, attribute_names=["job", "updated_at"])
    return saved_response(saved)


@router.delete("/saved/{job_id}", status_code=204)
async def remove_saved(
    job_id: UUID,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_job_seeker),
):
    saved = await db.scalar(
        select(SavedJob).where(SavedJob.job_id == job_id, SavedJob.user_id == user.id)
    )
    if saved:
        await db.delete(saved)


@router.post("/analyze", response_model=CareerReportResponse, status_code=201)
async def analyze_career_match(
    body: CareerAnalyzeRequest,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_job_seeker),
):
    job = await active_job(db, body.job_id)
    resume = await db.scalar(
        select(Resume).where(Resume.id == body.resume_id, Resume.user_id == user.id)
    )
    if resume is None:
        raise HTTPException(status_code=404, detail="请使用自己上传的简历。")
    if not resume.raw_text or not job.raw_description:
        raise HTTPException(status_code=422, detail="简历或岗位缺少可分析的正文。")
    if not settings.DEEPSEEK_API_KEY:
        raise HTTPException(status_code=503, detail="尚未配置 AI 服务，请联系管理员。")
    report = MatchReport(resume_id=resume.id, job_id=job.id, status=MatchStatus.PENDING)
    db.add(report)
    await db.flush()
    # 先保存待分析记录，避免耗时的 AI 请求持续占用 SQLite 写锁。
    await db.commit()
    try:
        from app.agents.orchestrator import orchestrator

        result = await orchestrator.analyze(
            resume_text=resume.raw_text,
            job_description=job.raw_description,
            for_job_seeker=True,
        )
        report.overall_score = result.overall_score
        report.result_data = result.to_dict()
        report.status = MatchStatus.COMPLETED
    except Exception:
        logger.warning("求职匹配分析失败，报告 ID：{}", report.id)
        report.status = MatchStatus.FAILED
        report.result_data = {"error": "AI 分析暂时失败，请稍后重试。"}
    await db.flush()
    await db.refresh(report)
    return report_response(report, job, resume)


@router.get("/reports", response_model=list[CareerReportResponse])
async def list_career_reports(
    db: AsyncSession = Depends(get_db), user: User = Depends(get_current_job_seeker)
):
    rows = await db.execute(
        select(MatchReport, Job, Resume)
        .join(Job, Job.id == MatchReport.job_id)
        .join(Resume, Resume.id == MatchReport.resume_id)
        .where(Resume.user_id == user.id)
        .order_by(MatchReport.created_at.desc())
    )
    return [report_response(report, job, resume) for report, job, resume in rows]
