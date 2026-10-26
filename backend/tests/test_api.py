"""覆盖用户、权限、文件管理、重复分析及匹配流水线。"""

from io import BytesIO
from pathlib import Path
from unittest.mock import AsyncMock

from docx import Document
from sqlalchemy import select

from app.agents.base import AgentError
from app.agents.orchestrator import OrchestratorResult
from app.config import settings
from app.models.user import User


async def sign_in(client, name="tester", role="HR"):
    response = await client.post(
        "/api/v1/auth/register",
        json={
            "username": name,
            "email": f"{name}@example.com",
            "password": "test-password",
            "role": role,
        },
    )
    assert response.status_code == 201, response.text
    response = await client.post(
        "/api/v1/auth/login",
        json={
            "username": name,
            "password": "test-password",
        },
    )
    assert response.status_code == 200, response.text
    return {"Authorization": f"Bearer {response.json()['access_token']}"}


async def upload(client, headers, filename="resume.txt", content=b"Python engineer"):
    response = await client.post(
        "/api/v1/resumes/upload", headers=headers, files={"file": (filename, content)}
    )
    assert response.status_code == 201, response.text
    return response.json()["id"]


async def create_job(client, headers):
    response = await client.post(
        "/api/v1/jobs/",
        headers=headers,
        json={
            "title": "Python 工程师",
            "company": "测试公司",
            "raw_description": "熟悉 Python",
            "level": "INTERMEDIATE",
        },
    )
    assert response.status_code == 201, response.text
    return response.json()["id"]


async def test_same_filename_is_independent_and_owner_is_checked(client):
    headers = await sign_in(client)
    first = await upload(client, headers, "../resume.txt", b"first")
    second = await upload(client, headers, "../resume.txt", b"second")
    for resume_id, expected in [(first, b"first"), (second, b"second")]:
        response = await client.get(f"/api/v1/resumes/{resume_id}/file", headers=headers)
        assert response.content == expected
    stranger = await sign_in(client, "stranger")
    assert (await client.get(f"/api/v1/resumes/{first}/file", headers=stranger)).status_code == 404
    assert (await client.delete(f"/api/v1/resumes/{first}", headers=headers)).status_code == 204
    assert (
        await client.get(f"/api/v1/resumes/{second}/file", headers=headers)
    ).content == b"second"


async def test_upload_limit_and_invalid_filter(client, monkeypatch):
    headers = await sign_in(client)
    monkeypatch.setattr(settings, "MAX_UPLOAD_SIZE", 4)
    response = await client.post(
        "/api/v1/resumes/upload", headers=headers, files={"file": ("big.txt", b"12345")}
    )
    assert response.status_code == 413
    assert not Path(settings.UPLOAD_DIR).exists()
    assert (await client.get("/api/v1/resumes/?status=INVALID", headers=headers)).status_code == 422
    assert (await client.get("/api/v1/jobs/?level=INVALID", headers=headers)).status_code == 422


async def test_docx_preview_escapes_html_and_download_has_filename(client):
    headers = await sign_in(client)
    document = Document()
    document.add_paragraph('<script>alert("xss")</script>')
    buffer = BytesIO()
    document.save(buffer)
    resume_id = await upload(client, headers, "<img>.docx", buffer.getvalue())
    response = await client.get(f"/api/v1/resumes/{resume_id}/file", headers=headers)
    assert "<script>" not in response.text
    assert "<img>" not in response.text
    assert "&lt;script&gt;" in response.text
    response = await client.get(f"/api/v1/resumes/{resume_id}/file?download=true", headers=headers)
    assert response.headers["content-disposition"].startswith("attachment;")
    assert "filename" in response.headers["content-disposition"]


async def test_resume_reanalysis_replaces_relations_and_update_serializes(client, monkeypatch):
    headers = await sign_in(client)
    resume_id = await upload(client, headers)
    run = AsyncMock(side_effect=[{"skills": [{"name": "Python"}]}, {"skills": [{"name": "SQL"}]}])
    monkeypatch.setattr("app.agents.resume_agent.ResumeAnalysisAgent.run", run)
    for expected in ["Python", "SQL"]:
        response = await client.post(f"/api/v1/resumes/{resume_id}/analyze", headers=headers)
        assert response.status_code == 200, response.text
        assert [skill["name"] for skill in response.json()["skills"]] == [expected]
    response = await client.put(
        f"/api/v1/resumes/{resume_id}", headers=headers, json={"title": "renamed"}
    )
    assert response.status_code == 200, response.text
    assert [skill["name"] for skill in response.json()["skills"]] == ["SQL"]


async def test_job_reanalysis_refreshes_requirements(client, monkeypatch):
    headers = await sign_in(client)
    job_id = await create_job(client, headers)
    monkeypatch.setattr(
        "app.agents.job_agent.JobAnalysisAgent.run",
        AsyncMock(
            side_effect=[
                {"required_skills": [{"name": "Python"}]},
                {"required_skills": [{"name": "SQL"}]},
            ]
        ),
    )
    for expected in ["Python", "SQL"]:
        response = await client.post(f"/api/v1/jobs/{job_id}/analyze", headers=headers)
        assert response.status_code == 200, response.text
        assert [item["name"] for item in response.json()["requirements"]] == [expected]


async def test_job_seeker_cannot_write_recruitment_data(client):
    headers = await sign_in(client, role="JOB_SEEKER")
    response = await client.post(
        "/api/v1/jobs/",
        headers=headers,
        json={
            "title": "Engineer",
            "company": "Test",
            "level": "INTERMEDIATE",
        },
    )
    assert response.status_code == 403
    resume_id = await upload(client, headers)
    response = await client.post(
        "/api/v1/matches/analyze",
        headers=headers,
        json={"resume_ids": [resume_id], "job_id": resume_id},
    )
    assert response.status_code == 403


async def test_no_key_returns_503_and_preserves_previous_analysis(client):
    headers = await sign_in(client)
    resume_id = await upload(client, headers)
    job_id = await create_job(client, headers)
    for path in [f"/api/v1/resumes/{resume_id}/analyze", f"/api/v1/jobs/{job_id}/analyze"]:
        response = await client.post(path, headers=headers)
        assert response.status_code == 503, response.text
        assert "API Key" in response.json()["detail"]
    response = await client.post(
        "/api/v1/matches/analyze",
        headers=headers,
        json={"resume_ids": [resume_id], "job_id": job_id},
    )
    assert response.status_code == 503
    assert (await client.get("/api/v1/matches/", headers=headers)).json() == []


async def test_match_success_deduplicates_and_failure_is_persisted(client, monkeypatch):
    headers = await sign_in(client)
    resume_id = await upload(client, headers)
    job_id = await create_job(client, headers)
    monkeypatch.setattr(settings, "DEEPSEEK_API_KEY", "test-key")
    pipeline = AsyncMock(
        side_effect=[
            OrchestratorResult({}, {}, {"overall_score": 85}, {"hiring_recommendation": "hire"}),
            AgentError("AI 服务调用失败"),
        ]
    )
    monkeypatch.setattr("app.agents.orchestrator.orchestrator.analyze", pipeline)
    for expected in ["COMPLETED", "FAILED"]:
        response = await client.post(
            "/api/v1/matches/analyze",
            headers=headers,
            json={"resume_ids": [resume_id, resume_id], "job_id": job_id},
        )
        assert response.status_code == 201, response.text
        assert len(response.json()) == 1
        report = response.json()[0]
        assert report["status"] == expected
        persisted = await client.get(f"/api/v1/matches/{report['id']}", headers=headers)
        assert persisted.json()["status"] == expected
        if expected == "FAILED":
            assert persisted.json()["overall_score"] is None
    assert pipeline.await_count == 2


async def test_seed_admin_uses_session_factory_and_is_idempotent(session_factory, monkeypatch):
    from app.main import _seed_admin_user

    monkeypatch.setattr("app.database.async_session_factory", session_factory)
    await _seed_admin_user()
    await _seed_admin_user()
    async with session_factory() as session:
        admins = (
            (await session.execute(select(User).where(User.username == "admin"))).scalars().all()
        )
        assert len(admins) == 1
