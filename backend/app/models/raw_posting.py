from datetime import datetime

from sqlalchemy import Boolean, DateTime, ForeignKey, func
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class RawPosting(Base):
    """
    Untouched ingestion payload, landed before any cleaning/normalization.

    This is what makes the ETL story real: ingestion writes here first,
    a separate cleaning step reads unprocessed rows and turns them into
    `jobs` records. If the cleaning logic changes later, raw data doesn't
    need to be re-fetched — just reprocessed.
    """

    __tablename__ = "raw_postings"

    id: Mapped[int] = mapped_column(primary_key=True)
    source_id: Mapped[int | None] = mapped_column(ForeignKey("job_sources.id"), nullable=True)

    raw_payload: Mapped[dict] = mapped_column(JSONB, nullable=False)
    fetched_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    processed: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)

    source: Mapped["JobSource | None"] = relationship()  # noqa: F821
