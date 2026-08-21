from datetime import datetime

from pydantic import BaseModel, ConfigDict


class JobMatchRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    job_id: int
    resume_id: int
    skill_score: float | None
    experience_score: float | None
    semantic_score: float | None
    education_score: float | None
    overall_score: float | None
    matched_skills: list[str] | None
    missing_skills: list[str] | None
    explanation: str | None
    computed_at: datetime
