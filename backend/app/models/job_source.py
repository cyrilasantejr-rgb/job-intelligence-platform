from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class JobSource(Base):
    __tablename__ = "job_sources"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String, nullable=False)
    source_type: Mapped[str] = mapped_column(String, nullable=False)  # 'api' | 'feed' | 'scrape'
    base_url: Mapped[str | None] = mapped_column(String, nullable=True)

    jobs: Mapped[list["Job"]] = relationship(back_populates="source")  # noqa: F821
