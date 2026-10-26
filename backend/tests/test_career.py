"""验证求职端公开岗位、私有收藏、匹配建议及跨账号权限。"""

from unittest.mock import AsyncMock
from uuid import UUID

from sqlalchemy import select
from test_api import create_job, sign_in, upload

from app.agents.base import AgentError
from app.agents.orchestrator import Orchestrator, OrchestratorResult
from app.config import settings
from app.models.job import Job
from app.models.match import MatchReport


async def test_catalog_only_active_search_and_source_dedup(client, session_factory):
    hr = await sign_in(client, name="hruser")
    seeker = await sign_in(client, name="seeker", role="JOB_SEEKER")
    first = await create_job(client, hr)
    duplicate = await create_job(client, hr)
    draft = await create_job(client, hr)
    closed = await create_job(client, hr)
    for job_id, status in [(draft, "DRAFT"), (closed, "CLOSED")]:
        response = await client.put(f"/api/v1/jobs/{job_id}", headers=hr, json={"status": status})
        assert response.status_code == 200
    async with session_factory() as session:
        for job in (await session.scalars(select(Job))).all():
            if str(job.id) in [first, duplicate]:
                job.source_url = "https://jobs.lever.co/test/real-id"
        await session.commit()
    response = await client.get("/api/v1/career/jobs?q=Python&level=INTERMEDIATE", headers=seeker)
    assert response.status_code == 200, response.text
    rows = response.json()
    assert len(rows) == 1
    assert rows[0]["source_url"] and "user_id" not in rows[0]
    assert rows[0]["created_at"].endswith("Z")
    assert (await client.get("/api/v1/career/jobs?q=nonexistent", headers=seeker)).json() == []
    for job_id in [draft, closed]:
        assert (
            await client.get(f"/api/v1/career/jobs/{job_id}", headers=seeker)
        ).status_code == 404
    assert (await client.get(f"/api/v1/jobs/{first}", headers=seeker)).status_code == 404
    assert (await client.get("/api/v1/career/jobs?level=bad", headers=seeker)).status_code == 422


async def test_saved_progress_is_private_persistent_and_closed_job_readable(client):
    hr = await sign_in(client, name="hruser")
    seeker = await sign_in(client, name="seeker", role="JOB_SEEKER")
    other = await sign_in(client, name="other", role="JOB_SEEKER")
    job_id = await create_job(client, hr)
    path = f"/api/v1/career/saved/{job_id}"
    for stage in ["SAVED", "INTERVIEW"]:
        response = await client.put(
            path, headers=seeker, json={"stage": stage, "notes": "周三准备面试"}
        )
        assert response.status_code == 200, response.text
        assert response.json()["stage"] == stage
    rows = (await client.get("/api/v1/career/saved", headers=seeker)).json()
    assert len(rows) == 1 and rows[0]["notes"] == "周三准备面试"
    assert (await client.get("/api/v1/career/saved", headers=other)).json() == []
    assert (await client.delete(path, headers=other)).status_code == 204
    assert len((await client.get("/api/v1/career/saved", headers=seeker)).json()) == 1
    await client.put(f"/api/v1/jobs/{job_id}", headers=hr, json={"status": "CLOSED"})
    assert (await client.get(f"/api/v1/career/jobs/{job_id}", headers=seeker)).status_code == 200
    assert (await client.get(f"/api/v1/career/jobs/{job_id}", headers=other)).status_code == 404
    assert (await client.put(path, headers=seeker, json={"stage": "ARCHIVED"})).status_code == 200
    assert (await client.delete(path, headers=seeker)).status_code == 204
    assert (await client.get("/api/v1/career/saved", headers=seeker)).json() == []


async def test_progress_input_validated_and_roles_enforced(client):
    hr = await sign_in(client, name="hruser")
    seeker = await sign_in(client, name="seeker", role="JOB_SEEKER")
    job_id = await create_job(client, hr)
    path = f"/api/v1/career/saved/{job_id}"
    for body in [{"stage": "FAKE"}, {"notes": "a" * 4001}, {"stage": None}]:
        assert (await client.put(path, headers=seeker, json=body)).status_code == 422
    for endpoint in ["jobs", "saved", "reports"]:
        assert (await client.get(f"/api/v1/career/{endpoint}", headers=hr)).status_code == 403
        assert (await client.get(f"/api/v1/career/{endpoint}")).status_code == 401
    assert (await client.put(path, headers=hr, json={})).status_code == 403
    response = await client.post(
        "/api/v1/career/analyze", headers=hr, json={"job_id": job_id, "resume_id": job_id}
    )
    assert response.status_code == 403


async def test_match_own_resume_against_public_job_and_history_isolation(client, monkeypatch):
    hr = await sign_in(client, name="hruser")
    seeker = await sign_in(client, name="seeker", role="JOB_SEEKER")
    other = await sign_in(client, name="other", role="JOB_SEEKER")
    job_id = await create_job(client, hr)
    resume_id = await upload(client, seeker)
    pipeline = AsyncMock(
        return_value=OrchestratorResult(
            {},
            {},
            {"overall_score": 78, "skill_match_score": 80, "experience_match_score": 75},
            {
                "summary": "有相关基础",
                "resume_tips": ["补充真实项目证据"],
                "learning_plan": ["练习 SQL"],
                "interview_preparation": ["准备项目复盘"],
            },
        )
    )
    monkeypatch.setattr(settings, "DEEPSEEK_API_KEY", "test-key")
    monkeypatch.setattr("app.agents.orchestrator.orchestrator.analyze", pipeline)
    response = await client.post(
        "/api/v1/career/analyze", headers=seeker, json={"job_id": job_id, "resume_id": resume_id}
    )
    assert response.status_code == 201, response.text
    report = response.json()
    assert report["status"] == "COMPLETED" and report["overall_score"] == 78
    assert report["created_at"].endswith("Z")
    assert report["result_data"]["report"]["resume_tips"] == ["补充真实项目证据"]
    pipeline.assert_awaited_once_with(
        resume_text="Python engineer", job_description="熟悉 Python", for_job_seeker=True
    )
    assert len((await client.get("/api/v1/career/reports", headers=seeker)).json()) == 1
    assert (await client.get("/api/v1/career/reports", headers=other)).json() == []
    for headers in [hr, other]:
        assert (
            await client.get(f"/api/v1/matches/{report['id']}", headers=headers)
        ).status_code == 404
        assert (
            await client.get(f"/api/v1/resumes/{resume_id}", headers=headers)
        ).status_code == 404


async def test_cannot_match_foreign_resume_closed_job_or_missing_key(client, monkeypatch):
    hr = await sign_in(client, name="hruser")
    seeker = await sign_in(client, name="seeker", role="JOB_SEEKER")
    job_id = await create_job(client, hr)
    foreign_resume = await upload(client, hr)
    own_resume = await upload(client, seeker)
    pipeline = AsyncMock()
    monkeypatch.setattr("app.agents.orchestrator.orchestrator.analyze", pipeline)
    for resume_id, code in [(foreign_resume, 404), (own_resume, 503)]:
        response = await client.post(
            "/api/v1/career/analyze",
            headers=seeker,
            json={"job_id": job_id, "resume_id": resume_id},
        )
        assert response.status_code == code, response.text
    await client.put(f"/api/v1/jobs/{job_id}", headers=hr, json={"status": "CLOSED"})
    monkeypatch.setattr(settings, "DEEPSEEK_API_KEY", "test-key")
    response = await client.post(
        "/api/v1/career/analyze", headers=seeker, json={"job_id": job_id, "resume_id": own_resume}
    )
    assert response.status_code == 404
    pipeline.assert_not_awaited()
    assert (await client.get("/api/v1/career/reports", headers=seeker)).json() == []


async def test_failed_ai_does_not_fabricate_score_or_leak_error(client, monkeypatch):
    hr = await sign_in(client, name="hruser")
    seeker = await sign_in(client, name="seeker", role="JOB_SEEKER")
    job_id = await create_job(client, hr)
    resume_id = await upload(client, seeker)
    monkeypatch.setattr(settings, "DEEPSEEK_API_KEY", "test-key")
    monkeypatch.setattr(
        "app.agents.orchestrator.orchestrator.analyze",
        AsyncMock(side_effect=AgentError("private-service-detail")),
    )
    response = await client.post(
        "/api/v1/career/analyze", headers=seeker, json={"job_id": job_id, "resume_id": resume_id}
    )
    assert response.status_code == 201, response.text
    assert response.json()["status"] == "FAILED"
    assert response.json()["overall_score"] is None
    assert "private-service-detail" not in response.text
    assert (await client.get("/api/v1/career/reports", headers=seeker)).json()[0][
        "status"
    ] == "FAILED"


async def test_hr_deletion_cascades_saved_records_and_reports(client, session_factory):
    hr = await sign_in(client, name="hruser")
    seeker = await sign_in(client, name="seeker", role="JOB_SEEKER")
    job_id = await create_job(client, hr)
    resume_id = await upload(client, seeker)
    await client.put(f"/api/v1/career/saved/{job_id}", headers=seeker, json={})
    async with session_factory() as session:
        session.add(MatchReport(job_id=UUID(job_id), resume_id=UUID(resume_id)))
        await session.commit()
    response = await client.delete(f"/api/v1/jobs/{job_id}", headers=hr)
    assert response.status_code == 204, response.text
    assert (await client.get("/api/v1/career/saved", headers=seeker)).json() == []
    assert (await client.get("/api/v1/career/reports", headers=seeker)).json() == []


async def test_orchestrator_uses_career_coach_only_for_job_seekers():
    flow = Orchestrator()
    for name in ["resume_agent", "job_agent", "match_agent", "report_agent", "career_agent"]:
        getattr(flow, name).run = AsyncMock(return_value={"agent": name})
    career_result = await flow.analyze("resume", "job", for_job_seeker=True)
    assert career_result.report == {"agent": "career_agent"}
    assert flow.match_agent.run.call_args.kwargs["job_description"] == "job"
    assert flow.career_agent.run.call_args.kwargs["resume_text"] == "resume"
    flow.report_agent.run.assert_not_awaited()
    hr_result = await flow.analyze("resume", "job")
    assert hr_result.report == {"agent": "report_agent"}
    flow.career_agent.run.assert_awaited_once()
