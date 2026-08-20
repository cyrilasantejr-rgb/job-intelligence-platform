from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class Resume(Base):
    """
    A single uploaded resume file.

    Note: this table doubles as "resume versions" from our original design —
    rather than a separate resume_versions table, each upload IS a version,
    distinguished by `version_label` (e.g. "SWE-focused v2"). This avoids an
    extra join for what would otherwise be a 1:1-ish relationship.
    """

    __tablename__ = "resumes"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)

    file_path: Mapped[str] = mapped_column(String, nullable=False)
    version_label: Mapped[str | None] = mapped_column(String, nullable=True)
    parsed_text: Mapped[str | None] = mapped_column(Text, nullable=True)

    uploaded_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

    user: Mapped["User"] = relationship(back_populates="resumes")  # noqa: F821
    applications: Mapped[list["Application"]] = relationship(back_populates="resume")  # noqa: F821
