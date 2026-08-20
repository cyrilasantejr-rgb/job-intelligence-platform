from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class JobSkill(Base):
    """
    Association between a job posting and a required/preferred skill.

    Composite primary key (job_id, skill_id) — a job can't list the same
    skill twice, which is exactly what we want enforced at the DB level.
    """

    __tablename__ = "job_skills"

    job_id: Mapped[int] = mapped_column(ForeignKey("jobs.id"), primary_key=True)
    skill_id: Mapped[int] = mapped_column(ForeignKey("skills.id"), primary_key=True)
    importance: Mapped[str | None] = mapped_column(String, nullable=True)  # 'required' | 'preferred'


class UserSkill(Base):
    """
    Association between a specific resume and a skill extracted from it.

    Scoped to resume_id (not user_id) since skills can change between
    resume versions — this is what lets the matching engine compare a
    specific resume version against a job, not just "the user" generically.
    """

    __tablename__ = "user_skills"

    resume_id: Mapped[int] = mapped_column(ForeignKey("resumes.id"), primary_key=True)
    skill_id: Mapped[int] = mapped_column(ForeignKey("skills.id"), primary_key=True)
