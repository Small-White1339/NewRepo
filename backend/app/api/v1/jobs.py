"""职位管理端点（完整实现）。"""

from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from loguru import logger
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.api.deps import get_current_user, get_db
from app.models.job import Job, JobLevel, JobRequirement, JobStatus, RequirementCategory
from app.models.user import User
from app.schemas.job import (
    JobCreateRequest,
    JobListItem,
    JobResponse,
    JobUpdateRequest,
)

router = APIRouter()


@router.post("/", response_model=JobResponse, status_code=status.HTTP_201_CREATED)
async def create_job(
    body: JobCreateRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """创建新的职位发布，包含原始描述。"""
    job = Job(
        user_id=current_user.id,
        title=body.title,
        company=body.company,
        raw_description=body.raw_description,
        level=JobLevel(body.level),
        status=JobStatus.ACTIVE,
    )
    db.add(job)
    await db.flush()

    # 用 selectinload 重新查询，确保 relationships 预加载
    result = await db.execute(
        select(Job).options(selectinload(Job.requirements)).where(Job.id == job.id)
    )
    return result.scalar_one()


@router.get("/", response_model=list[JobListItem])
async def list_jobs(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    q: str = Query("", description="按标题/公司关键字搜索"),
    status_filter: str | None = Query(None, alias="status", description="按状态过滤"),
    level_filter: str | None = Query(None, alias="level", description="按职级过滤"),
):
    """列出当前用户的职位，支持搜索和过滤。"""
    stmt = select(Job).where(Job.user_id == current_user.id)
    if q:
        stmt = stmt.where(Job.title.ilike(f"%{q}%") | Job.company.ilike(f"%{q}%"))
    if status_filter:
        stmt = stmt.where(Job.status == JobStatus(status_filter))
    if level_filter:
        stmt = stmt.where(Job.level == JobLevel(level_filter))
    stmt = stmt.order_by(Job.created_at.desc())
    result = await db.execute(stmt)
    jobs = result.scalars().all()
    return jobs


@router.get("/{job_id}", response_model=JobResponse)
async def get_job(
    job_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """获取完整的职位详情及要求。"""
    result = await db.execute(
        select(Job)
        .options(selectinload(Job.requirements))
        .where(Job.id == job_id, Job.user_id == current_user.id)
    )
    job = result.scalar_one_or_none()
    if job is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Job not found",
        )
    return job


@router.put("/{job_id}", response_model=JobResponse)
async def update_job(
    job_id: UUID,
    body: JobUpdateRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """更新职位发布详情。"""
    result = await db.execute(
        select(Job)
        .options(selectinload(Job.requirements))
        .where(Job.id == job_id, Job.user_id == current_user.id)
    )
    job = result.scalar_one_or_none()
    if job is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Job not found",
        )

    update_data = body.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(job, field, value)

    await db.flush()
    # 用 selectinload 重新查询，确保 relations 预加载
    result = await db.execute(
        select(Job).options(selectinload(Job.requirements)).where(Job.id == job_id)
    )
    return result.scalar_one()


@router.post("/{job_id}/analyze", response_model=JobResponse)
async def analyze_job(
    job_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """使用 JobAnalysisAgent 分析职位描述并存储结构化数据。"""
    result = await db.execute(
        select(Job)
        .options(selectinload(Job.requirements))
        .where(Job.id == job_id, Job.user_id == current_user.id)
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
            detail="Job has no description text to analyze",
        )

    try:
        from app.agents.job_agent import JobAnalysisAgent

        agent = JobAnalysisAgent()
        structured_data = await agent.run(job_description=job.raw_description)
        job.structured_data = structured_data

        # 将结构化要求转换为 JobRequirement 记录
        # 先清除旧要求（重新分析时）
        job.requirements.clear()

        for skill in structured_data.get("required_skills", []):
            req = JobRequirement(
                job_id=job_id,
                category=RequirementCategory.SKILL,
                name=skill.get("name", ""),
                importance=skill.get("importance", 5),
                is_mandatory=skill.get("is_mandatory", True),
            )
            db.add(req)

        for req_text in structured_data.get("mandatory_requirements", []):
            req = JobRequirement(
                job_id=job_id,
                category=RequirementCategory.SKILL,
                name=req_text,
                importance=10,
                is_mandatory=True,
            )
            db.add(req)

        for req_text in structured_data.get("nice_to_have", []):
            req = JobRequirement(
                job_id=job_id,
                category=RequirementCategory.SKILL,
                name=req_text,
                importance=3,
                is_mandatory=False,
            )
            db.add(req)

        edu = structured_data.get("education_requirement", "")
        if edu and edu != "not specified":
            req = JobRequirement(
                job_id=job_id,
                category=RequirementCategory.EDUCATION,
                name=f"学历要求：{edu}",
                importance=7,
                is_mandatory=True,
            )
            db.add(req)

        exp = structured_data.get("experience_requirement", "")
        if exp and exp != "not specified":
            req = JobRequirement(
                job_id=job_id,
                category=RequirementCategory.EXPERIENCE,
                name=f"经验要求：{exp}",
                importance=7,
                is_mandatory=True,
            )
            db.add(req)

        await db.flush()
        logger.info(f"Job {job_id} analyzed successfully: {len(structured_data.get('required_skills', []))} skills, "
                    f"{len(structured_data.get('mandatory_requirements', []))} mandatory, "
                    f"{len(structured_data.get('nice_to_have', []))} nice-to-have")
    except Exception as e:
        logger.error(f"Failed to analyze job {job_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Job analysis failed: {e}",
        )

    # 重新加载包含要求的职位
    result = await db.execute(
        select(Job)
        .options(selectinload(Job.requirements))
        .where(Job.id == job_id)
    )
    return result.scalar_one()


@router.delete("/{job_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_job(
    job_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """删除职位及关联要求。"""
    result = await db.execute(
        select(Job).where(Job.id == job_id, Job.user_id == current_user.id)
    )
    job = result.scalar_one_or_none()
    if job is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Job not found")

    await db.delete(job)
    await db.commit()
    logger.info("Job deleted: id={}, user_id={}", job_id, current_user.id)
