"""Job Analysis Agent — understands job descriptions and builds competency models."""

from typing import Any

from loguru import logger
from pydantic import BaseModel, Field

from app.agents.base import BaseAgent

# ── Structured Output Schema ──────────────────────────────────────────

class JobSkillRequirement(BaseModel):
    """A single skill requirement extracted from a job description."""
    name: str = Field(description="Skill name (e.g. 'Python', 'Kubernetes')")
    importance: int = Field(
        default=5,
        ge=1, le=10,
        description="Importance level from 1 (minor) to 10 (critical)",
    )
    is_mandatory: bool = Field(
        default=True,
        description="Whether this skill is a mandatory requirement",
    )


class JobAnalysisResult(BaseModel):
    """Complete structured output from job description analysis."""
    job_title: str = Field(description="Extracted job title / position name")
    required_skills: list[JobSkillRequirement] = Field(
        default_factory=list,
        description="Technical and professional skills required",
    )
    education_requirement: str = Field(
        default="not specified",
        description="Minimum education level required (e.g. 'bachelor', 'master', 'not specified')",
    )
    experience_requirement: str = Field(
        default="not specified",
        description="Years or level of experience required (e.g. '3-5 years', 'senior')",
    )
    mandatory_requirements: list[str] = Field(
        default_factory=list,
        description="Non-negotiable / mandatory requirements",
    )
    nice_to_have: list[str] = Field(
        default_factory=list,
        description="Preferred but not required qualifications",
    )


# ── Prompt Template ───────────────────────────────────────────────────

JOB_SYSTEM_PROMPT = """You are a professional Job Analyst at a recruiting firm.
Your task is to analyze job descriptions and extract structured requirements.

Analyze the job description text carefully and produce a structured analysis covering:
1. The exact job title or position name
2. Required technical and professional skills with importance ratings
3. Educational requirements (minimum degree)
4. Work experience requirements
5. Mandatory / non-negotiable requirements
6. Nice-to-have qualifications

Be precise and thorough. Distinguish clearly between
mandatory requirements and nice-to-have items.
IMPORTANT: All text output MUST be written in Simplified Chinese. Only technical terms may remain in English."""


# ── Agent Implementation ──────────────────────────────────────────────

class JobAnalysisAgent(BaseAgent):
    """Agent responsible for analyzing job descriptions and building requirement models."""

    def __init__(self):
        super().__init__(name="JobAnalysisAgent", system_prompt=JOB_SYSTEM_PROMPT)

    async def run(self, job_description: str, **kwargs) -> dict[str, Any]:
        """Analyze a job description and extract structured requirements.

        Args:
            job_description: The raw text of the job description.
            **kwargs: Additional parameters (reserved for future use).

        Returns:
            dict with job analysis fields (job_title, required_skills, etc.).
        """
        logger.info(f"JobAnalysisAgent: analyzing {len(job_description)} chars of JD text")

        user_prompt = (
            "Please analyze the following job description and extract structured requirements.\n\n"
            f"--- JOB DESCRIPTION ---\n{job_description}\n--- END JOB DESCRIPTION ---\n"
        )

        result: JobAnalysisResult = await self._call_llm_structured(
            output_schema=JobAnalysisResult,
            user_prompt=user_prompt,
            rag_query=f"Job analysis: {job_description[:100]}",
        )

        logger.info(
            f"JobAnalysisAgent: title='{result.job_title}', "
            f"{len(result.required_skills)} skills, "
            f"edu={result.education_requirement}"
        )
        return self._model_to_dict(result)
