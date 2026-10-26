"""验证 AI 初始化、JSON 解析及失败处理，无需真实 API Key。"""

from types import SimpleNamespace
from unittest.mock import AsyncMock

import pytest

from app.agents.base import AgentError
from app.agents.job_agent import JobAnalysisAgent, JobAnalysisResult
from app.config import settings


async def test_missing_key_reports_configuration_error(monkeypatch):
    monkeypatch.setattr(settings, "DEEPSEEK_API_KEY", "")
    with pytest.raises(AgentError, match="API Key"):
        await JobAnalysisAgent().run(job_description="Python developer")


async def test_first_llm_initialization_and_fenced_json(monkeypatch):
    monkeypatch.setattr(settings, "DEEPSEEK_API_KEY", "test-key")
    llm = SimpleNamespace(
        ainvoke=AsyncMock(
            return_value=SimpleNamespace(
                content='```json\n{"job_title": "Python 工程师"}\n```',
            )
        )
    )
    factory = lambda **kwargs: llm
    monkeypatch.setattr("app.agents.base.ChatOpenAI", factory)
    agent = JobAnalysisAgent()
    result = await agent.run(job_description="Python developer")
    assert result["job_title"] == "Python 工程师"
    assert agent._get_llm() is llm
    llm.ainvoke.assert_awaited_once()


async def test_invalid_json_retries_and_never_returns_empty_success(monkeypatch):
    monkeypatch.setattr(settings, "DEEPSEEK_API_KEY", "test-key")
    llm = SimpleNamespace(
        ainvoke=AsyncMock(
            side_effect=[
                SimpleNamespace(content="invalid"),
                SimpleNamespace(content="{}"),
            ]
        )
    )
    agent = JobAnalysisAgent()
    agent._llm = llm
    with pytest.raises(AgentError, match="格式无效"):
        await agent._call_llm_structured(JobAnalysisResult, "test")
    assert llm.ainvoke.await_count == 2


async def test_network_failure_has_actionable_error(monkeypatch):
    monkeypatch.setattr(settings, "DEEPSEEK_API_KEY", "test-key")
    agent = JobAnalysisAgent()
    agent._llm = SimpleNamespace(ainvoke=AsyncMock(side_effect=TimeoutError()))
    with pytest.raises(AgentError, match="服务调用失败"):
        await agent.run(job_description="test")
