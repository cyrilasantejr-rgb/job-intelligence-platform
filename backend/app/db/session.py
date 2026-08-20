"""
Database engine and session management.

`get_db` is a FastAPI dependency — routes/services request a session via
`Depends(get_db)` rather than importing SessionLocal directly, which keeps
DB lifecycle management out of business logic and makes testing easier
(sessions can be swapped out in tests via dependency overrides).
"""

from collections.abc import Generator

from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from app.core.config import settings

engine = create_engine(settings.database_url, pool_pre_ping=True)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db() -> Generator[Session, None, None]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
