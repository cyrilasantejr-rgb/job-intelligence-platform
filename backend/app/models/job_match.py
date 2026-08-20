from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Numeric, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import JSONB

from app.db.base import Base


class JobMatch(Base):
    """
    A computed resume-to-job match score, stored rather than only computed
    on the fly — this gives us a queryable history (e.g. "match score before
    vs. after a resume update") and avoids recomputation on every page load.
    """

    __tablename__ = "job_matches"

    id: Mapped[int] = mapped_column(primary_key=True)
    job_id: Mapped[int] = mapped_column(ForeignKey("jobs.id"), nullable=False)
    resume_id: Mapped[int] = mapped_column(ForeignKey("resumes.id"), nullable=False)

    skill_score: Mapped[float | None] = mapped_column(Numeric, nullable=True)
    experience_score: Mapped[float | None] = mapped_column(Numeric, nullable=True)
    semantic_score: Mapped[float | None] = mapped_column(Numeric, nullable=True)
    education_score: Mapped[float | None] = mapped_column(Numeric, nullable=True)
    overall_score: Mapped[float | None] = mapped_column(Numeric, nullable=True)

    matched_skills: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    missing_skills: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    explanation: Mapped[str | None] = mapped_column(Text, nullable=True)

    computed_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

    job: Mapped["Job"] = relationship()  # noqa: F821
    resume: Mapped["Resume"] = relationship()  # noqa: F821
