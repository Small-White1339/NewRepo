"""Resume Analysis Agent — extracts structured info and capabilities from resumes."""

from typing import Any

from loguru import logger
from pydantic import BaseModel, Field

from app.agents.base import BaseAgent

# ── Structured Output Schema ──────────────────────────────────────────

class SkillInfo(BaseModel):
    """Individual skill extracted from a resume."""
    name: str = Field(description="Skill name (e.g. 'Python', 'Project Management')")
    level: str = Field(default="intermediate", description="Proficiency level: beginner / intermediate / advanced / expert")
    category: str = Field(default="general", description="Skill category (e.g. programming_language, framework, tool, soft_skill)")


class EducationInfo(BaseModel):
    """Education entry extracted from resume."""
    school: str = Field(description="School or university name")
    degree: str | None = Field(default=None, description="Degree: high_school / associate / bachelor / master / phd")
    field: str | None = Field(default=None, description="Field of study")
    start_date: str | None = Field(default=None, description="Start date (e.g. '2018-09')")
    end_date: str | None = Field(default=None, description="End date (e.g. '2022-06')")
    description: str | None = Field(default=None, description="Additional details")


class WorkExperienceInfo(BaseModel):
    """Work experience entry extracted from resume."""
    company: str = Field(description="Company name")
    title: str = Field(description="Job title")
    description: str | None = Field(default=None, description="Job description and responsibilities")
    start_date: str | None = Field(default=None, description="Start date (e.g. '2020-03')")
    end_date: str | None = Field(default=None, description="End date or 'present'")
    is_current: bool = Field(default=False, description="Whether this is the current position")


class ProjectInfo(BaseModel):
    """Project entry extracted from resume."""
    name: str = Field(description="Project name")
    role: str | None = Field(default=None, description="Role in the project")
    description: str | None = Field(default=None, description="Project description")
    tech_stack: list[str] = Field(default_factory=list, description="Technologies used")
    start_date: str | None = Field(default=None, description="Start date")
    end_date: str | None = Field(default=None, description="End date")


class ResumeAnalysisResult(BaseModel):
    """Complete structured output from resume analysis."""
    name: str = Field(default="未知", description="Candidate's full name (姓名)")
    phone: str | None = Field(default=None, description="Phone number (手机号)")
    email: str | None = Field(default=None, description="Email address (邮箱)")
    age: int | None = Field(default=None, description="Candidate's age in years (年龄)")
    summary: str = Field(description="One-paragraph overall summary of the candidate")
    skills: list[SkillInfo] = Field(default_factory=list, description="Extracted skills")
    experience_years: float = Field(default=0.0, description="Total years of professional experience")
    education_level: str = Field(default="unknown", description="Highest education: high_school/associate/bachelor/master/phd")
    educations: list[EducationInfo] = Field(default_factory=list, description="Education history")
    work_experiences: list[WorkExperienceInfo] = Field(default_factory=list, description="Work experience history")
    projects: list[ProjectInfo] = Field(default_factory=list, description="Project experience")
    strengths: list[str] = Field(default_factory=list, description="Key strengths of the candidate")
    weaknesses: list[str] = Field(default_factory=list, description="Potential gaps or weaknesses")
    key_achievements: list[str] = Field(default_factory=list, description="Notable accomplishments")


# ── Prompt Template ───────────────────────────────────────────────────

RESUME_SYSTEM_PROMPT = """You are a professional Resume Analyst at a recruiting firm.
Your task is to analyze a candidate's resume and extract structured information.

Analyze the resume text carefully and produce a structured assessment covering:
1. The candidate's full name (姓名)
2. Phone number (手机号) if available, otherwise null
3. Email address (邮箱) if available, otherwise null
4. Candidate's age (年龄) if available, otherwise null
5. A concise one-paragraph summary of the candidate's profile
4. Technical and professional skills with proficiency levels and categories
5. Total years of professional work experience
6. Highest education level attained
7. Education history (school, degree, field, dates)
8. Work experience history (company, title, dates, description)
9. Project experience (name, role, description, tech stack)
10. Key strengths that make the candidate stand out
11. Potential weaknesses or areas for improvement
12. Notable achievements and accomplishments

Be objective and evidence-based. Base your analysis only on what is present in the resume text.
IMPORTANT: All text output MUST be written in Simplified Chinese. Only technical terms may remain in English."""


# ── Agent Implementation ──────────────────────────────────────────────

class ResumeAnalysisAgent(BaseAgent):
    """Agent responsible for analyzing resumes and extracting candidate capabilities."""

    def __init__(self):
        super().__init__(name="ResumeAnalysisAgent", system_prompt=RESUME_SYSTEM_PROMPT)

    async def run(self, resume_text: str, **kwargs) -> dict[str, Any]:
        """Analyze a resume and extract structured information.

        Args:
            resume_text: The raw text content of the resume.
            **kwargs: Additional parameters (reserved for future use).

        Returns:
            dict with resume analysis fields (summary, skills, strengths, etc.).
        """
        logger.info(f"ResumeAnalysisAgent: analyzing {len(resume_text)} chars of text")

        user_prompt = (
            "Please analyze the following resume text and provide a structured assessment.\n\n"
            f"--- RESUME TEXT ---\n{resume_text}\n--- END RESUME ---\n"
        )

        result: ResumeAnalysisResult = await self._call_llm_structured(
            output_schema=ResumeAnalysisResult,
            user_prompt=user_prompt,
            rag_query="Resume analysis: skills and experience evaluation",
        )

        logger.info(
            f"ResumeAnalysisAgent: extracted {len(result.skills)} skills, "
            f"{result.experience_years}y experience, "
            f"education={result.education_level}"
        )
        return self._model_to_dict(result)
