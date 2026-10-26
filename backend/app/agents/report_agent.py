"""Report Generation Agent — generates recruitment analysis reports and interview suggestions."""

from typing import Any

from loguru import logger
from pydantic import BaseModel, Field

from app.agents.base import BaseAgent

# ── Structured Output Schema ──────────────────────────────────────────


class ReportResult(BaseModel):
    """Structured output from the final recruitment report generator."""

    executive_summary: str = Field(
        description="Concise executive summary of the candidate-job match (2-3 paragraphs)",
    )
    interview_suggestions: list[str] = Field(
        default_factory=list,
        description="Specific questions and areas to explore during interviews",
    )
    hiring_recommendation: str = Field(
        description=(
            "Final recommendation: 'strong_hire', 'hire', 'consider', 'weak', or 'not_recommended'"
        ),
    )
    follow_up_questions: list[str] = Field(
        default_factory=list,
        description="Questions the candidate should be asked to clarify gaps or verify claims",
    )


# ── Prompt Template ───────────────────────────────────────────────────

REPORT_SYSTEM_PROMPT = """You are a professional Recruitment Report Writer.
Your task is to generate comprehensive recruitment analysis reports.

You will receive:
1. Resume analysis (candidate profile, skills, experience, strengths/weaknesses)
2. Job analysis (job title, required skills, experience, education)
3. Match analysis (scores, matched/missing skills, strengths/gap analysis)

Based on all this information, produce a final recruitment report covering:
1. Executive summary - a concise overview of the candidate-job match
2. Interview suggestions - specific areas to probe and questions to ask
3. Hiring recommendation - one of: strong_hire, hire, consider, weak, not_recommended
4. Follow-up questions - specific questions to verify claims or clarify gaps

Be professional, objective, and actionable. Provide concrete interview suggestions.
IMPORTANT: All text output MUST be written in Simplified Chinese.
Only technical terms may remain in English."""


# ── Agent Implementation ──────────────────────────────────────────────


class ReportGenerationAgent(BaseAgent):
    """Agent responsible for generating recruitment analysis reports."""

    def __init__(self):
        super().__init__(
            name="ReportGenerationAgent",
            system_prompt=REPORT_SYSTEM_PROMPT,
        )

    async def run(
        self,
        resume_analysis: dict,
        job_analysis: dict,
        match_result: dict,
        **kwargs,
    ) -> dict[str, Any]:
        """Generate a comprehensive recruitment report.

        Args:
            resume_analysis: Output from ResumeAnalysisAgent.
            job_analysis: Output from JobAnalysisAgent.
            match_result: Output from MatchingRecommendationAgent.
            **kwargs: Additional parameters (reserved for future use).

        Returns:
            dict with report fields (executive_summary, interview_suggestions, etc.).
        """
        logger.info("ReportGenerationAgent: generating final recruitment report")

        user_prompt = (
            "Please generate a comprehensive recruitment report "
            "based on the following analysis data.\n\n"
            f"--- RESUME ANALYSIS ---\n{resume_analysis}\n--- END RESUME ANALYSIS ---\n\n"
            f"--- JOB ANALYSIS ---\n{job_analysis}\n--- END JOB ANALYSIS ---\n\n"
            f"--- MATCH ANALYSIS ---\n{match_result}\n--- END MATCH ANALYSIS ---\n\n"
            "Provide a final recruitment report with executive summary, interview suggestions, "
            "hiring recommendation, and follow-up questions."
        )

        result: ReportResult = await self._call_llm_structured(
            output_schema=ReportResult,
            user_prompt=user_prompt,
            rag_query=(
                "Recruitment report generation: interview suggestions and hiring recommendations"
            ),
        )

        logger.info(
            f"ReportGenerationAgent: recommendation='{result.hiring_recommendation}', "
            f"{len(result.interview_suggestions)} interview suggestions"
        )
        return self._model_to_dict(result)
