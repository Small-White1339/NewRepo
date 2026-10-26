"""将真实公开资料导入当前 HR 工作区，保留来源并防止重复导入。"""

import json
from datetime import datetime, timedelta, timezone
from pathlib import Path
from uuid import uuid4

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_hr, get_db
from app.api.v1.resumes import _populate_resume_relations
from app.config import settings
from app.models.job import Job, JobLevel, JobStatus
from app.models.resume import Resume, ResumeStatus
from app.models.user import User
from app.services.public_sources import fetch_public_jobs, fetch_public_resumes

router = APIRouter()


async def existing_imports(db, model, user):
    rows = (
        (
            await db.execute(
                select(model).where(model.user_id == user.id, model.source_url.is_not(None))
            )
        )
        .scalars()
        .all()
    )
    recent = [row.imported_at for row in rows if row.imported_at]
    if recent and max(stamp.replace(tzinfo=timezone.utc) for stamp in recent) > datetime.now(
        timezone.utc
    ) - timedelta(hours=1):
        raise HTTPException(status_code=429, detail="公开数据已在一小时内同步过，请稍后再试。")
    return {row.source_url: row for row in rows}


@router.post("/jobs")
async def import_jobs(db: AsyncSession = Depends(get_db), user: User = Depends(get_current_hr)):
    existing = await existing_imports(db, Job, user)
    records, errors = await fetch_public_jobs()
    if not records:
        raise HTTPException(status_code=502, detail="真实岗位来源暂时不可用，请稍后重试。")
    created, updated = 0, 0
    for record in records:
        job = existing.get(record["source_url"])
        if job is None:
            job = Job(user_id=user.id, level=JobLevel.UNSPECIFIED, status=JobStatus.ACTIVE)
            db.add(job)
            existing[record["source_url"]] = job
            created += 1
        else:
            updated += 1
        job.title, job.company = record["title"], record["company"]
        job.raw_description = f"工作地点：{record['location']}\n\n{record['description']}"
        job.source_name, job.source_url = record["source_name"], record["source_url"]
        job.imported_at = datetime.now(timezone.utc)
    await db.flush()
    return {"created": created, "updated": updated, "skipped": 0, "errors": errors}


@router.post("/resumes")
async def import_resumes(db: AsyncSession = Depends(get_db), user: User = Depends(get_current_hr)):
    existing = await existing_imports(db, Resume, user)
    records, errors = await fetch_public_resumes()
    if not records:
        raise HTTPException(status_code=502, detail="公开简历来源暂时不可用，请稍后重试。")
    created, skipped = 0, 0
    seen_names = set()
    for record in records:
        parsed = record["parsed"]
        if record["source_url"] in existing:
            existing[record["source_url"]].imported_at = datetime.now(timezone.utc)
            skipped += 1
            continue
        if parsed["name"] in seen_names:
            skipped += 1
            continue
        seen_names.add(parsed["name"])
        resume = Resume(
            user_id=user.id,
            title=f"{parsed['name']} · 公开简历"[:255],
            status=ResumeStatus.PARSED,
            parsed_data=parsed,
            source_name=record["source_name"],
            source_url=record["source_url"],
            imported_at=datetime.now(timezone.utc),
        )
        text = json.dumps(parsed, ensure_ascii=False, indent=2)
        resume.raw_text = (
            "本人公开的职业履历参考资料，不代表本人正在求职或向本平台投递。\n"
            f"来源：{record['source_url']}\n\n{text}"
        )
        directory = Path(settings.UPLOAD_DIR).resolve()
        directory.mkdir(parents=True, exist_ok=True)
        path = directory / f"{uuid4().hex}.txt"
        path.write_text(resume.raw_text, encoding="utf-8")
        resume.file_path = str(path)
        db.add(resume)
        await db.flush()
        await _populate_resume_relations(resume, parsed, db, new=True)
        created += 1
    await db.flush()
    return {"created": created, "updated": 0, "skipped": skipped, "errors": errors}
