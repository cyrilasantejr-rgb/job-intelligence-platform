from datetime import date, datetime

from sqlalchemy import Date, DateTime, ForeignKey, Numeric, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class Job(Base):
    __tablename__ = "jobs"

    id: Mapped[int] = mapped_column(primary_key=True)

    company_id: Mapped[int] = mapped_column(ForeignKey("companies.id"), nullable=False)
    source_id: Mapped[int | None] = mapped_column(ForeignKey("job_sources.id"), nullable=True)
    raw_posting_id: Mapped[int | None] = mapped_column(ForeignKey("raw_postings.id"), nullable=True)

    title: Mapped[str] = mapped_column(String, nullable=False)
    category: Mapped[str | None] = mapped_column(String, nullable=True)  # SWE, Data Eng, ML/AI, etc.
    employment_type: Mapped[str | None] = mapped_column(String, nullable=True)  # Internship | New Grad
    location: Mapped[str | None] = mapped_column(String, nullable=True)
    work_mode: Mapped[str | None] = mapped_column(String, nullable=True)  # Remote | Hybrid | On-site

    salary_min: Mapped[float | None] = mapped_column(Numeric, nullable=True)
    salary_max: Mapped[float | None] = mapped_column(Numeric, nullable=True)

    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    application_url: Mapped[str | None] = mapped_column(String, nullable=True)

    date_posted: Mapped[date | None] = mapped_column(Date, nullable=True)
    deadline: Mapped[date | None] = mapped_column(Date, nullable=True)

    # Used for dedup: hash of normalized(company + title + location).
    # Computed in the ingestion/cleaning service, not in the DB layer.
    dedup_hash: Mapped[str] = mapped_column(String, nullable=False, unique=True)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

    company: Mapped["Company"] = relationship(back_populates="jobs")  # noqa: F821
    source: Mapped["JobSource | None"] = relationship(back_populates="jobs")  # noqa: F821
