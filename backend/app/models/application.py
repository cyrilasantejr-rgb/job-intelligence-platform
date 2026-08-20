from datetime import date, datetime

from sqlalchemy import Date, DateTime, ForeignKey, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class Application(Base):
    """
    A single application to a job.

    `current_status` is the Kanban column and is always overwritable —
    it does NOT preserve history on its own. The full chronological record
    lives in `application_events`, which is append-only and never rewritten
    when the application moves to a new stage.
    """

    __tablename__ = "applications"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    job_id: Mapped[int] = mapped_column(ForeignKey("jobs.id"), nullable=False)
    resume_id: Mapped[int | None] = mapped_column(ForeignKey("resumes.id"), nullable=True)

    current_status: Mapped[str] = mapped_column(String, nullable=False, default="saved")
    date_applied: Mapped[date | None] = mapped_column(Date, nullable=True)
    recruiter_contact: Mapped[str | None] = mapped_column(String, nullable=True)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

    user: Mapped["User"] = relationship(back_populates="applications")  # noqa: F821
    resume: Mapped["Resume | None"] = relationship(back_populates="applications")  # noqa: F821
    events: Mapped[list["ApplicationEvent"]] = relationship(  # noqa: F821
        back_populates="application", order_by="ApplicationEvent.event_date"
    )
    interviews: Mapped[list["Interview"]] = relationship(back_populates="application")  # noqa: F821
