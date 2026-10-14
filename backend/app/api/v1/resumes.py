"""简历上传和管理端点。"""

import os
import re
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, UploadFile, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from loguru import logger

from app.api.deps import get_current_user, get_current_user_from_query, get_db
from app.config import settings
from app.models.resume import (
    Certificate,
    Education,
    Project,
    Resume,
    ResumeStatus,
    Skill,
    WorkExperience,
)
from app.models.user import User
from app.schemas.resume import (
    ResumeListItem,
    ResumeResponse,
    ResumeUpdateRequest,
    ResumeUploadResponse,
)
from app.services.resume_parser import parse_resume_file

router = APIRouter()

ALLOWED_EXTENSIONS = {".pdf", ".docx", ".txt", ".md", ".markdown"}


def _populate_resume_relations(resume: Resume, parsed_data: dict, db: AsyncSession, new: bool = False):
    """从 AI 解析结果填充关联表，直接操作外键避免懒加载。"""
    if not new:
        # 重新分析时手动删除旧数据（不使用 .clear() 避免懒加载）
        for rel in [resume.skills, resume.educations, resume.work_experiences, resume.projects, resume.certificates]:
            for item in list(rel):
                db.delete(item)

    for s in parsed_data.get("skills", []):
        if s.get("name"):
            db.add(Skill(resume_id=resume.id, name=s["name"], level=s.get("level"), category=s.get("category")))

    for e in parsed_data.get("educations", []):
        if e.get("school"):
            db.add(Education(
                resume_id=resume.id, school=e["school"], degree=e.get("degree"), field=e.get("field"),
                start_date=_parse_date(e.get("start_date")), end_date=_parse_date(e.get("end_date")),
                description=e.get("description"),
            ))

    for w in parsed_data.get("work_experiences", []):
        if w.get("company") and w.get("title"):
            db.add(WorkExperience(
                resume_id=resume.id, company=w["company"], title=w["title"], description=w.get("description"),
                start_date=_parse_date(w.get("start_date")), end_date=_parse_date(w.get("end_date")),
                is_current=w.get("is_current", False),
            ))

    for p in parsed_data.get("projects", []):
        if p.get("name"):
            db.add(Project(
                resume_id=resume.id, name=p["name"], role=p.get("role"), description=p.get("description"),
                tech_stack=p.get("tech_stack", []),
                start_date=_parse_date(p.get("start_date")), end_date=_parse_date(p.get("end_date")),
            ))


def _parse_date(s: str | None):
    if not s:
        return None
    try:
        from datetime import date
        m = re.match(r"(\d{4})-(\d{2})", s)
        if m:
            return date(int(m.group(1)), int(m.group(2)), 1)
        m = re.match(r"(\d{4})", s)
        if m:
            return date(int(m.group(1)), 1, 1)
    except:  # noqa: E722
        pass
    return None


@router.post("/upload", response_model=ResumeUploadResponse, status_code=status.HTTP_201_CREATED)
async def upload_resume(
    file: UploadFile,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """上传简历文件（PDF/DOCX/TXT）进行解析。"""
    logger.info(
        "Resume upload by user_id={}: filename={}, size={}, type={}",
        current_user.id, file.filename, file.size, file.content_type,
    )

    # 校验文件扩展名
    ext = os.path.splitext(file.filename or "")[1].lower()
    if ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Unsupported file type '{ext}'. Allowed: {', '.join(ALLOWED_EXTENSIONS)}",
        )

    # 校验文件大小
    contents = await file.read()
    if len(contents) > settings.MAX_UPLOAD_SIZE:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail=f"File too large. Maximum size is {settings.MAX_UPLOAD_SIZE // (1024*1024)} MB",
        )

    # 将文件保存到磁盘
    upload_dir = settings.UPLOAD_DIR
    os.makedirs(upload_dir, exist_ok=True)
    file_path = os.path.join(upload_dir, f"{current_user.id}_{file.filename}")
    with open(file_path, "wb") as f:
        f.write(contents)

    # 解析文件
    try:
        raw_text = parse_resume_file(file_path, ext)
        status_ = ResumeStatus.PARSED
    except Exception as e:
        logger.error("Resume parse failed for user_id={}, filename={}: {}", current_user.id, file.filename, e)
        raw_text = None
        status_ = ResumeStatus.FAILED

    # AI 智能解析（异步，失败不影响上传）
    parsed_data = None
    if raw_text and status_ == ResumeStatus.PARSED:
        api_key = settings.DEEPSEEK_API_KEY
        if not api_key:
            logger.warning("LLM API key not set — AI resume analysis skipped.")
        else:
            try:
                from app.agents.resume_agent import ResumeAnalysisAgent

                agent = ResumeAnalysisAgent()
                parsed_data = await agent.run(resume_text=raw_text)
                logger.info("AI resume analysis completed for user_id={}: {} skills, {}y exp",
                            current_user.id, len(parsed_data.get("skills", [])), parsed_data.get("experience_years", 0))
            except Exception as e:
                logger.warning("AI resume analysis failed for user_id={}: {}", current_user.id, e)

    # 创建简历记录
    resume = Resume(
        user_id=current_user.id,
        title=file.filename or "untitled",
        file_path=file_path,
        raw_text=raw_text,
        parsed_data=parsed_data,
        status=status_,
    )
    db.add(resume)
    await db.flush()

    # 填充关联表（新简历，无需清空）
    if parsed_data:
        _populate_resume_relations(resume, parsed_data, db, new=True)
        await db.flush()

    await db.refresh(resume)

    logger.info(
        "Resume uploaded by user_id={}: id={}, filename={}, status={}",
        current_user.id, resume.id, resume.title, status_.value,
    )

    return ResumeUploadResponse(
        id=resume.id,
        title=resume.title,
        status=resume.status.value,
        message="Resume uploaded and parsed successfully." if status_ == ResumeStatus.PARSED
        else "Resume uploaded but parsing failed.",
    )


@router.get("/", response_model=list[ResumeListItem])
async def list_resumes(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    q: str = Query("", description="按标题关键字搜索"),
    status_filter: str | None = Query(None, alias="status", description="按状态过滤"),
):
    """列出当前用户的简历，支持搜索和状态过滤。"""
    stmt = select(Resume).where(Resume.user_id == current_user.id)
    if q:
        stmt = stmt.where(Resume.title.ilike(f"%{q}%"))
    if status_filter:
        stmt = stmt.where(Resume.status == ResumeStatus(status_filter))
    stmt = stmt.order_by(Resume.created_at.desc())
    result = await db.execute(stmt)
    resumes = result.scalars().all()
    logger.debug("Resumes listed for user_id={}: count={}", current_user.id, len(resumes))
    return resumes


@router.get("/{resume_id}", response_model=ResumeResponse)
async def get_resume(
    resume_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """获取完整的简历详情及解析数据。"""
    result = await db.execute(
        select(Resume)
        .options(
            selectinload(Resume.educations),
            selectinload(Resume.skills),
            selectinload(Resume.projects),
            selectinload(Resume.work_experiences),
            selectinload(Resume.certificates),
        )
        .where(Resume.id == resume_id, Resume.user_id == current_user.id)
    )
    resume = result.scalar_one_or_none()
    if resume is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Resume not found",
        )
    logger.debug("Resume detail queried: resume_id={}, user_id={}", resume_id, current_user.id)
    return resume


@router.get("/{resume_id}/file")
async def get_resume_file(
    resume_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user_from_query),
    download: bool = Query(False, description="强制下载而非预览"),
):
    """获取原始简历文件进行预览（支持 PDF/TXT/MD/DOCX）。"""
    from fastapi.responses import FileResponse, HTMLResponse

    result = await db.execute(
        select(Resume).where(Resume.id == resume_id, Resume.user_id == current_user.id)
    )
    resume = result.scalar_one_or_none()
    if resume is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Resume not found")
    if not resume.file_path or not os.path.exists(resume.file_path):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Resume file not found")

    ext = os.path.splitext(resume.file_path)[1].lower()
    media_types = {
        ".pdf": "application/pdf",
        ".docx": "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        ".txt": "text/plain; charset=utf-8",
        ".md": "text/markdown; charset=utf-8",
        ".markdown": "text/markdown; charset=utf-8",
    }
    media_type = media_types.get(ext, "application/octet-stream")

    disposition = "attachment" if download else "inline"

    # DOCX 浏览器无法直接预览，转为 HTML 展示
    if ext == ".docx" and not download:
        try:
            from app.services.resume_parser import _parse_docx
            text = _parse_docx(resume.file_path)
            html = f"""<!DOCTYPE html><html lang="zh-CN"><head><meta charset="utf-8">
<title>{resume.title}</title>
<style>body{{font-family:sans-serif;max-width:800px;margin:40px auto;padding:0 20px;line-height:1.8;white-space:pre-wrap;word-break:break-word}}
h1{{border-bottom:2px solid #2563eb;padding-bottom:8px;color:#1e293b}}</style>
</head><body><h1>{resume.title}</h1><div>{'<br>'.join(text.split(chr(10)))}</div></body></html>"""
            return HTMLResponse(content=html, status_code=200)
        except Exception as e:
            logger.warning("DOCX text preview failed: {}", e)
            # 降级为直接下载
    return FileResponse(resume.file_path, filename=resume.title, media_type=media_type, headers={"Content-Disposition": disposition})

    return FileResponse(resume.file_path, filename=resume.title, media_type=media_type, headers={"Content-Disposition": "inline"})


@router.put("/{resume_id}", response_model=ResumeResponse)
async def update_resume(
    resume_id: UUID,
    body: ResumeUpdateRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """更新简历信息（标题）。"""
    result = await db.execute(
        select(Resume)
        .options(
            selectinload(Resume.educations),
            selectinload(Resume.skills),
            selectinload(Resume.projects),
            selectinload(Resume.work_experiences),
            selectinload(Resume.certificates),
        )
        .where(Resume.id == resume_id, Resume.user_id == current_user.id)
    )
    resume = result.scalar_one_or_none()
    if resume is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Resume not found")

    update_data = body.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(resume, field, value)

    await db.flush()
    await db.refresh(resume)
    logger.info("Resume updated: id={}, user_id={}", resume_id, current_user.id)
    return resume


@router.delete("/{resume_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_resume(
    resume_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """删除简历及其关联数据。"""
    result = await db.execute(
        select(Resume).where(Resume.id == resume_id, Resume.user_id == current_user.id)
    )
    resume = result.scalar_one_or_none()
    if resume is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Resume not found")

    # 删除物理文件
    if resume.file_path and os.path.exists(resume.file_path):
        os.remove(resume.file_path)

    await db.delete(resume)
    await db.commit()
    logger.info("Resume deleted: id={}, user_id={}", resume_id, current_user.id)


@router.post("/{resume_id}/analyze", response_model=ResumeResponse)
async def analyze_resume(
    resume_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """使用 ResumeAnalysisAgent 对简历进行 AI 智能解析并填充结构化数据。"""
    result = await db.execute(
        select(Resume)
        .options(
            selectinload(Resume.educations),
            selectinload(Resume.skills),
            selectinload(Resume.projects),
            selectinload(Resume.work_experiences),
            selectinload(Resume.certificates),
        )
        .where(Resume.id == resume_id, Resume.user_id == current_user.id)
    )
    resume = result.scalar_one_or_none()
    if resume is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Resume not found")
    if not resume.raw_text:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Resume has no parseable text")

    try:
        from app.agents.resume_agent import ResumeAnalysisAgent

        agent = ResumeAnalysisAgent()
        parsed_data = await agent.run(resume_text=resume.raw_text)
        resume.parsed_data = parsed_data
        _populate_resume_relations(resume, parsed_data, db)
        await db.flush()
        await db.refresh(resume)
        logger.info("Resume AI analysis completed: id={}, user_id={}", resume_id, current_user.id)
    except Exception as e:
        logger.error("Resume AI analysis failed: id={}, error={}", resume_id, e)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"AI analysis failed: {e}")

    return resume
