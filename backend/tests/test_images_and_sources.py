"""覆盖照片解析、自动 AI 分析以及真实数据来源导入规则。"""

import json
from datetime import datetime, timedelta, timezone
from io import BytesIO
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import AsyncMock

from PIL import Image, ImageDraw, ImageFont
from sqlalchemy import select
from test_api import sign_in

from app.config import settings
from app.models.job import Job
from app.services.public_sources import normalize_resume
from app.services.resume_parser import parse_resume_file


def png_bytes(text="Python FastAPI PostgreSQL"):
    image = Image.new("RGB", (1200, 160), "white")
    ImageDraw.Draw(image).text((30, 40), text, font=ImageFont.load_default(size=46), fill="black")
    buffer = BytesIO()
    image.save(buffer, format="PNG")
    return buffer.getvalue()


async def test_photo_upload_runs_ocr_and_auto_ai(client, monkeypatch):
    headers = await sign_in(client)
    monkeypatch.setattr(
        "app.services.resume_parser._get_ocr_engine",
        lambda: lambda pixels: SimpleNamespace(txts=("Python FastAPI PostgreSQL",)),
    )
    monkeypatch.setattr(settings, "DEEPSEEK_API_KEY", "test-key")
    analyze = AsyncMock(
        return_value={"summary": "Python backend skills", "skills": [{"name": "Python"}]}
    )
    monkeypatch.setattr("app.agents.resume_agent.ResumeAnalysisAgent.run", analyze)
    response = await client.post(
        "/api/v1/resumes/upload",
        headers=headers,
        files={"file": ("photo.png", png_bytes(), "image/png")},
    )
    assert response.status_code == 201, response.text
    assert response.json()["status"] == "PARSED"
    analyze.assert_awaited_once_with(resume_text="Python FastAPI PostgreSQL")
    detail = (await client.get(f"/api/v1/resumes/{response.json()['id']}", headers=headers)).json()
    assert detail["raw_text"] == "Python FastAPI PostgreSQL"
    assert detail["skills"][0]["name"] == "Python"
    preview = await client.get(f"/api/v1/resumes/{detail['id']}/file", headers=headers)
    assert preview.headers["content-type"].startswith("image/png")
    assert preview.content == png_bytes()


async def test_invalid_and_blank_photo_do_not_create_resume(client, monkeypatch):
    headers = await sign_in(client)
    monkeypatch.setattr(
        "app.services.resume_parser._get_ocr_engine",
        lambda: lambda pixels: SimpleNamespace(txts=None),
    )
    for data in [b"not an image", png_bytes("")]:
        response = await client.post(
            "/api/v1/resumes/upload", headers=headers, files={"file": ("bad.jpg", data)}
        )
        assert response.status_code == 422, response.text
    assert (await client.get("/api/v1/resumes/", headers=headers)).json() == []
    assert list(Path(settings.UPLOAD_DIR).iterdir()) == []


def test_real_ocr_engine_recognizes_text(tmp_path):
    image_path = tmp_path / "ocr.png"
    image_path.write_bytes(png_bytes())
    text = parse_resume_file(str(image_path))
    assert "python" in text.lower()
    assert "postgresql" in text.lower()


def test_public_resume_preserves_facts_and_removes_contacts():
    parsed = normalize_resume(
        {
            "basics": {
                "name": "Test Person",
                "email": "private@example.com",
                "phone": "+86 13800000000",
                "location": {"address": "Private street"},
                "summary": "Engineer. Contact private@example.com",
            },
            "skills": [{"name": "Python", "keywords": ["SQL"]}],
            "work": [
                {"name": "Real source company", "position": "Engineer", "startDate": "2021-01"}
            ],
        }
    )
    encoded = json.dumps(parsed)
    assert "private@example.com" not in encoded and "13800000000" not in encoded
    assert "Private street" not in encoded
    assert parsed["work_experiences"][0]["start_date"] == "2021-01"
    assert "experience_years" not in parsed


async def test_job_import_attribution_dedup_and_cooldown(client, monkeypatch, session_factory):
    headers = await sign_in(client)
    records = [
        {
            "title": "Engineer",
            "company": "Source company",
            "description": "Python",
            "location": "London",
            "source_name": "Official source",
            "source_url": "https://jobs.lever.co/example/123",
        }
    ]
    monkeypatch.setattr(
        "app.api.v1.imports.fetch_public_jobs", AsyncMock(return_value=(records, []))
    )
    response = await client.post("/api/v1/imports/jobs", headers=headers)
    assert response.status_code == 200, response.text
    assert response.json()["created"] == 1
    assert (await client.post("/api/v1/imports/jobs", headers=headers)).status_code == 429
    rows = (await client.get("/api/v1/jobs/", headers=headers)).json()
    assert rows[0]["source_url"] == records[0]["source_url"]
    assert rows[0]["level"] == "UNSPECIFIED"
    async with session_factory() as session:
        job = (await session.execute(select(Job))).scalar_one()
        job.imported_at = datetime.now(timezone.utc) - timedelta(hours=2)
        await session.commit()
    response = await client.post("/api/v1/imports/jobs", headers=headers)
    assert response.json()["updated"] == 1 and response.json()["created"] == 0


async def test_resume_import_without_llm_and_isolation(client, monkeypatch):
    headers = await sign_in(client)
    parsed = normalize_resume({"basics": {"name": "Test Person"}, "skills": [{"name": "Python"}]})
    records = [
        {
            "parsed": parsed,
            "source_name": "Public self-published resume",
            "source_url": "https://registry.jsonresume.org/test",
        }
    ]
    monkeypatch.setattr(
        "app.api.v1.imports.fetch_public_resumes", AsyncMock(return_value=(records, []))
    )
    response = await client.post("/api/v1/imports/resumes", headers=headers)
    assert response.status_code == 200, response.text
    assert response.json()["created"] == 1
    resumes = (await client.get("/api/v1/resumes/?q=Python", headers=headers)).json()
    assert len(resumes) == 1 and resumes[0]["source_url"]
    detail = (await client.get(f"/api/v1/resumes/{resumes[0]['id']}", headers=headers)).json()
    assert detail["skills"][0]["name"] == "Python"
    stranger = await sign_in(client, name="stranger")
    assert (await client.get("/api/v1/resumes/", headers=stranger)).json() == []


async def test_imports_are_hr_only_and_fail_without_fake_fallback(client, monkeypatch):
    headers = await sign_in(client, role="JOB_SEEKER")
    for resource in ["jobs", "resumes"]:
        assert (
            await client.post(f"/api/v1/imports/{resource}", headers=headers)
        ).status_code == 403
    hr = await sign_in(client, name="hruser")
    monkeypatch.setattr(
        "app.api.v1.imports.fetch_public_jobs", AsyncMock(return_value=([], ["unavailable"]))
    )
    assert (await client.post("/api/v1/imports/jobs", headers=hr)).status_code == 502
    assert (await client.get("/api/v1/jobs/", headers=hr)).json() == []
