"""
Health check endpoint.

Confirms the API process is up and, separately, that it can reach the
database — the two most common "is anything broken" questions when
debugging the Docker stack.
"""

from fastapi import APIRouter, Depends
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.db.session import get_db

router = APIRouter()


@router.get("/health")
def health_check() -> dict:
    return {"status": "ok"}


@router.get("/health/db")
def health_check_db(db: Session = Depends(get_db)) -> dict:
    db.execute(text("SELECT 1"))
    return {"status": "ok", "database": "connected"}
