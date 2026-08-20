from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class IngestionRun(Base):
    """
    Metadata about a single ingestion pipeline run — this is what makes the
    data-engineering side observable rather than a black box. Populated by
    ingestion scripts starting in Phase 3.
    """

    __tablename__ = "ingestion_runs"

    id: Mapped[int] = mapped_column(primary_key=True)
    source_id: Mapped[int | None] = mapped_column(ForeignKey("job_sources.id"), nullable=True)

    started_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    finished_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    records_fetched: Mapped[int | None] = mapped_column(Integer, nullable=True)
    records_new: Mapped[int | None] = mapped_column(Integer, nullable=True)
    records_duplicate: Mapped[int | None] = mapped_column(Integer, nullable=True)

    status: Mapped[str | None] = mapped_column(String, nullable=True)  # 'success' | 'failed'
    error_message: Mapped[str | None] = mapped_column(Text, nullable=True)

    source: Mapped["JobSource | None"] = relationship()  # noqa: F821
