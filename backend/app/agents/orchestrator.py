"""Agent 编排器 — 按顺序串联 4 个分析 Agent。

流程：
  1. ResumeAnalysisAgent（简历文本 → 简历分析结果）
  2. JobAnalysisAgent（职位描述 → 职位分析结果）
  3. MatchingAgent（简历分析 + 职位分析 → 匹配结果）
  4. ReportAgent（简历分析 + 职位分析 + 匹配结果 → 报告）
"""

from __future__ import annotations

from typing import Any

from loguru import logger

from app.agents.career_agent import CareerAdviceAgent
from app.agents.job_agent import JobAnalysisAgent
from app.agents.match_agent import MatchingRecommendationAgent
from app.agents.report_agent import ReportGenerationAgent
from app.agents.resume_agent import ResumeAnalysisAgent


class OrchestratorResult:
    """完整链式输出的容器。"""

    def __init__(
        self,
        resume_analysis: dict[str, Any],
        job_analysis: dict[str, Any],
        match_result: dict[str, Any],
        report: dict[str, Any],
    ):
        self.resume_analysis = resume_analysis
        self.job_analysis = job_analysis
        self.match_result = match_result
        self.report = report

    def to_dict(self) -> dict[str, Any]:
        """将完整结果序列化为嵌套字典以用于 JSON 存储。"""
        return {
            "resume_analysis": self.resume_analysis,
            "job_analysis": self.job_analysis,
            "match_result": self.match_result,
            "report": self.report,
        }

    @property
    def overall_score(self) -> float:
        """总体匹配分数的便捷访问器。"""
        return self.match_result.get("overall_score", 0.0)


class Orchestrator:
    """编排多 Agent 分析流水线。

    为提升效率，每个 Agent 仅实例化一次并在多次 ``analyze()`` 调用间复用。
    流水线是顺序执行的 — 每一步依赖前一步的输出。
    """

    def __init__(self):
        self.resume_agent = ResumeAnalysisAgent()
        self.job_agent = JobAnalysisAgent()
        self.match_agent = MatchingRecommendationAgent()
        self.report_agent = ReportGenerationAgent()
        self.career_agent = CareerAdviceAgent()
        logger.info("Orchestrator initialized with 4 agents")

    async def analyze(
        self,
        resume_text: str,
        job_description: str,
        for_job_seeker: bool = False,
    ) -> OrchestratorResult:
        """运行完整的 4 Agent 分析流水线。

        Args:
            resume_text: 从候选人简历中提取的原始文本。
            job_description: 职位描述（JD）的原始文本。

        Returns:
            包含所有中间结果和最终输出的 ``OrchestratorResult``。

        Raises:
            RuntimeError: 如果链中任一 Agent 执行失败。
        """
        # ── 第 1 步：简历分析 ──────────────────────────────────────
        logger.info("Orchestrator: step 1/4 — Resume Analysis")
        try:
            resume_analysis = await self.resume_agent.run(resume_text=resume_text)
            logger.debug(f"Resume analysis completed: {len(resume_analysis)} fields")
        except Exception as e:
            logger.error(f"ResumeAnalysisAgent failed: {e}")
            raise RuntimeError(f"Resume analysis failed: {e}") from e

        # ── 第 2 步：职位分析 ─────────────────────────────────────────
        logger.info("Orchestrator: step 2/4 — Job Analysis")
        try:
            job_analysis = await self.job_agent.run(job_description=job_description)
            logger.debug(f"Job analysis completed: {len(job_analysis)} fields")
        except Exception as e:
            logger.error(f"JobAnalysisAgent failed: {e}")
            raise RuntimeError(f"Job analysis failed: {e}") from e

        # ── 第 3 步：匹配分析 ─────────────────────────────────────────────
        logger.info("Orchestrator: step 3/4 — Matching Analysis")
        try:
            match_result = await self.match_agent.run(
                resume_analysis=resume_analysis,
                job_analysis=job_analysis,
                resume_text=resume_text,
                job_description=job_description,
            )
            logger.debug(f"Matching completed: score={match_result.get('overall_score')}")
        except Exception as e:
            logger.error(f"MatchingRecommendationAgent failed: {e}")
            raise RuntimeError(f"Match analysis failed: {e}") from e

        # ── 第 4 步：报告生成 ────────────────────────────────────
        logger.info("Orchestrator: step 4/4 — Report Generation")
        try:
            report_agent = self.career_agent if for_job_seeker else self.report_agent
            report = await report_agent.run(
                resume_analysis=resume_analysis,
                job_analysis=job_analysis,
                match_result=match_result,
                **(
                    {"resume_text": resume_text, "job_description": job_description}
                    if for_job_seeker
                    else {}
                ),
            )
            logger.debug(f"Report completed: recommendation={report.get('hiring_recommendation')}")
        except Exception as e:
            logger.error(f"ReportGenerationAgent failed: {e}")
            raise RuntimeError(f"Report generation failed: {e}") from e

        return OrchestratorResult(
            resume_analysis=resume_analysis,
            job_analysis=job_analysis,
            match_result=match_result,
            report=report,
        )


# 单例，用于跨请求复用
orchestrator = Orchestrator()
