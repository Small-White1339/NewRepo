"""Matching Recommendation Agent — matches candidates to positions."""

from typing import Any

from loguru import logger
from pydantic import BaseModel, Field

from app.agents.base import BaseAgent

# ── Structured Output Schema ──────────────────────────────────────────

class MatchAnalysisResult(BaseModel):
    """Structured output from candidate-job matching analysis."""
    overall_score: float = Field(
        default=0.0, ge=0.0, le=100.0,
        description="Overall match score from 0 to 100",
    )
    skill_match_score: float = Field(
        default=0.0, ge=0.0, le=100.0,
        description="How well the candidate's skills match the job requirements (0-100)",
    )
    experience_match_score: float = Field(
        default=0.0, ge=0.0, le=100.0,
        description="How well the candidate's experience matches (0-100)",
    )
    matched_skills: list[str] = Field(
        default_factory=list,
        description="Skills the candidate has that match job requirements",
    )
    missing_skills: list[str] = Field(
        default_factory=list,
        description="Required skills the candidate is missing",
    )
    strengths_analysis: str = Field(
        description="Analysis of candidate's strengths relative to this position",
    )
    gap_analysis: str = Field(
        description="Analysis of gaps between candidate profile and job requirements",
    )


# ── Prompt Template ───────────────────────────────────────────────────

MATCH_SYSTEM_PROMPT = """You are a professional Recruitment Matching Specialist.
Your task is to evaluate how well a candidate's profile matches a job position.

You will receive:
1. Resume analysis output (candidate's skills, experience, strengths, weaknesses)
2. Job analysis output (required skills, education, experience, mandatory requirements)

Evaluate the match thoroughly and produce a structured assessment:
1. Overall match score (0-100) based on a weighted combination of factors
2. Separate skill match and experience match scores
3. List of skills the candidate has that match job requirements
4. List of required skills the candidate is missing
5. Detailed analysis of the candidate's strengths for this role
6. Detailed analysis of gaps or areas of concern

Be objective and fair. Explain your reasoning clearly in the analysis fields.
IMPORTANT: All text output MUST be written in Simplified Chinese. Only technical terms may remain in English."""


# ── Agent Implementation ──────────────────────────────────────────────

class MatchingRecommendationAgent(BaseAgent):
    """Agent responsible for matching candidate profiles with job requirements."""

    def __init__(self):
        super().__init__(
            name="MatchingRecommendationAgent",
            system_prompt=MATCH_SYSTEM_PROMPT,
        )

    async def run(
        self,
        resume_analysis: dict,
        job_analysis: dict,
        **kwargs,
    ) -> dict[str, Any]:
        """Match a candidate's resume analysis against job requirements.

        Args:
            resume_analysis: Output from ResumeAnalysisAgent.
            job_analysis: Output from JobAnalysisAgent.
            **kwargs: Additional parameters (reserved for future use).

        Returns:
            dict with match analysis fields (overall_score, matched_skills, etc.).
        """
        logger.info("MatchingRecommendationAgent: analyzing candidate-job match")

        user_prompt = (
            "Please evaluate the match between the following "
            "candidate profile and job requirements.\n\n"
            f"--- RESUME ANALYSIS ---\n{resume_analysis}\n--- END RESUME ANALYSIS ---\n\n"
            f"--- JOB ANALYSIS ---\n{job_analysis}\n--- END JOB ANALYSIS ---\n\n"
            "Provide a detailed match assessment with scores and analysis."
        )

        result: MatchAnalysisResult = await self._call_llm_structured(
            output_schema=MatchAnalysisResult,
            user_prompt=user_prompt,
            rag_query="Candidate-job matching: skills gap analysis and score evaluation",
        )

        logger.info(
            f"MatchingRecommendationAgent: overall_score={result.overall_score}, "
            f"skill_match={result.skill_match_score}, "
            f"matched={len(result.matched_skills)} skills, "
            f"missing={len(result.missing_skills)} skills"
        )
        return self._model_to_dict(result)
