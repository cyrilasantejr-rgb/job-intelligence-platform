from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class Skill(Base):
    """
    Normalized skill taxonomy (e.g. "Python", "AWS", "PySpark").

    Kept as its own table rather than free-text arrays on jobs/resumes so we
    can do skill-level analytics later (e.g. "which skills appear in 80% of
    rejected postings") without parsing text at query time.
    """

    __tablename__ = "skills"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String, nullable=False, unique=True)
