from datetime import datetime

from sqlalchemy import Boolean, DateTime, ForeignKey, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class ApplicationEvent(Base):
    """
    A single entry in an application's chronological timeline.

    Append-only by design — this table is never updated in place when an
    application moves to a new stage. `event_date` (when it happened) and
    `recorded_at` (when we logged it) are intentionally separate, since a
    future email-integration backfill may log an old event today.
    """

    __tablename__ = "application_events"

    id: Mapped[int] = mapped_column(primary_key=True)
    application_id: Mapped[int] = mapped_column(ForeignKey("applications.id"), nullable=False)
    event_type_id: Mapped[int] = mapped_column(ForeignKey("event_types.id"), nullable=False)

    event_date: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    recorded_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

    source: Mapped[str | None] = mapped_column(String, nullable=True)  # 'email' | 'manual' | 'portal' | 'phone' | 'linkedin'
    sender: Mapped[str | None] = mapped_column(String, nullable=True)
    subject: Mapped[str | None] = mapped_column(String, nullable=True)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)

    is_automated: Mapped[bool | None] = mapped_column(Boolean, nullable=True)
    requires_response: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    responded: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    response_date: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    next_action: Mapped[str | None] = mapped_column(Text, nullable=True)
    deadline: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    # Traceability for future email integration (nullable for manual entries)
    source_message_id: Mapped[str | None] = mapped_column(String, nullable=True)
    created_by: Mapped[str] = mapped_column(String, nullable=False, default="user")  # 'user' | 'email_integration' | 'system'

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

    application: Mapped["Application"] = relationship(back_populates="events")  # noqa: F821
    event_type: Mapped["EventType"] = relationship()
