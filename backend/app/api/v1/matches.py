"""匹配分析端点（完整的 AI Agent 流水线实现）。"""

import asyncio
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from loguru import logger
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_hr, get_current_user, get_db
from app.config import settings
from app.models.job import Job
from app.models.match import MatchReport, MatchStatus
from app.models.resume import Resume
from app.models.user import User
from app.schemas.match import (
    MatchAnalyzeRequest,
    MatchReportListItem,
    MatchReportResponse,
)

router = APIRouter()


@router.post(
    "/analyze", response_model=list[MatchReportResponse], status_code=status.HTTP_201_CREATED
)
async def analyze_match(
    body: MatchAnalyzeRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_hr),
):
    """使用多 Agent 流水线批量分析多个简历与职位的匹配。"""
    if not settings.DEEPSEEK_API_KEY:
        raise HTTPException(status_code=503, detail="尚未配置 DeepSeek API Key。")
    # 1. 验证职位所有权和描述（只需一次）
    result = await db.execute(
        select(Job).where(
            Job.id == body.job_id,
            Job.user_id == current_user.id,
        )
    )
    job = result.scalar_one_or_none()
    if job is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Job not found",
        )
    if not job.raw_description:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Job has no description text. Please provide a description.",
        )

    # 2. 验证简历所有权和文本内容（过滤无效简历，不中止整个批次）
    valid_resumes: list[Resume] = []
    skipped: list[dict] = []
    for resume_id in dict.fromkeys(body.resume_ids):
        result = await db.execute(
            select(Resume).where(
                Resume.id == resume_id,
                Resume.user_id == current_user.id,
            )
        )
        resume = result.scalar_one_or_none()
        if resume is None:
            skipped.append({"resume_id": str(resume_id), "reason": "Resume not found"})
            logger.warning(f"Skipping resume {resume_id}: not found")
            continue
        if not resume.raw_text:
            skipped.append({"resume_id": str(resume_id), "reason": "Resume has no parseable text"})
            logger.warning(f"Skipping resume {resume_id}: no parseable text")
            continue
        valid_resumes.append(resume)

    if not valid_resumes:
        detail = "No valid resumes to analyze"
        if skipped:
            detail += f" ({len(skipped)} skipped)"
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=detail,
        )

    # 3. 为所有有效简历创建 PENDING 报告
    reports: list[MatchReport] = []
    for resume in valid_resumes:
        report = MatchReport(
            resume_id=resume.id,
            job_id=body.job_id,
            status=MatchStatus.PENDING,
        )
        db.add(report)
        reports.append(report)
    await db.flush()

    # 刷新以获取 ID / created_at
    for report in reports:
        await db.refresh(report)

    # 4. 并行运行多 Agent 流水线（每个简历独立执行）
    semaphore = asyncio.Semaphore(settings.MATCH_CONCURRENCY)

    async def _run_pipeline(report: MatchReport, resume: Resume):
        try:
            from app.agents.orchestrator import orchestrator

            logger.info(f"Starting agent pipeline for match {report.id} (resume={resume.id})")
            async with semaphore:
                result_data = await orchestrator.analyze(
                    resume_text=resume.raw_text,
                    job_description=job.raw_description,
                )

            report.overall_score = result_data.overall_score
            report.result_data = result_data.to_dict()
            report.status = MatchStatus.COMPLETED

            logger.info(
                f"Match {report.id} completed: overall_score={result_data.overall_score}, "
                f"recommendation={result_data.report.get('hiring_recommendation')}"
            )
        except Exception as e:
            logger.error(f"Agent pipeline failed for match {report.id}: {e}")
            report.status = MatchStatus.FAILED
            report.result_data = {"error": str(e)}

    await asyncio.gather(
        *[_run_pipeline(report, resume) for report, resume in zip(reports, valid_resumes)]
    )

    # 5. 持久化所有更新并返回
    await db.flush()
    for report in reports:
        await db.refresh(report)

    return [MatchReportResponse.model_validate(r) for r in reports]


@router.get("/", response_model=list[MatchReportListItem])
async def list_matches(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """列出当前用户的所有匹配报告。"""
    # 通过用户的简历获取匹配报告
    result = await db.execute(
        select(MatchReport)
        .join(Resume)
        .where(Resume.user_id == current_user.id)
        .order_by(MatchReport.created_at.desc())
    )
    reports = result.scalars().all()
    return reports


@router.get("/{report_id}", response_model=MatchReportResponse)
async def get_match_report(
    report_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """获取匹配报告详情。"""
    result = await db.execute(
        select(MatchReport)
        .join(Resume)
        .where(
            MatchReport.id == report_id,
            Resume.user_id == current_user.id,
        )
    )
    report = result.scalar_one_or_none()
    if report is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Match report not found",
        )
    return report
