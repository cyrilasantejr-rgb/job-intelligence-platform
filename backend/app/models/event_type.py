from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class EventType(Base):
    """
    Controlled vocabulary for application timeline events.

    A lookup table rather than a hardcoded enum so new event types (e.g.
    "Offer Rescinded") can be added with an INSERT instead of a migration.
    `maps_to_status` is optional — most events (like an automated
    confirmation) enrich the timeline without moving the Kanban column.
    """

    __tablename__ = "event_types"

    id: Mapped[int] = mapped_column(primary_key=True)
    code: Mapped[str] = mapped_column(String, nullable=False, unique=True)
    display_name: Mapped[str] = mapped_column(String, nullable=False)
    maps_to_status: Mapped[str | None] = mapped_column(String, nullable=True)
