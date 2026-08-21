"""
Ingestion pipeline entrypoint.

Run with:
    docker compose exec backend python -m app.ingestion.run_ingestion

For each configured board token: fetch jobs from Greenhouse, land them
raw in `raw_postings`, then clean/normalize them into `jobs`. Every run
is recorded in `ingestion_runs` for observability — this is what makes
the data-engineering side auditable rather than a black box.
"""

from datetime import datetime, timezone

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.session import SessionLocal
from app.core.logging import get_logger
from app.ingestion.config import BOARD_TOKENS
from app.ingestion.greenhouse_client import GreenhouseFetchError, fetch_jobs_for_board
from app.models.ingestion_run import IngestionRun
from app.models.job_source import JobSource
from app.models.raw_posting import RawPosting
from app.services import ingestion_service

logger = get_logger(__name__)


def get_or_create_job_source(db: Session, board_token: str) -> JobSource:
    stmt = select(JobSource).where(JobSource.name == f"Greenhouse - {board_token}")
    source = db.execute(stmt).scalar_one_or_none()
    if source is None:
        source = JobSource(
            name=f"Greenhouse - {board_token}",
            source_type="api",
            base_url=f"https://boards-api.greenhouse.io/v1/boards/{board_token}/jobs",
        )
        db.add(source)
        db.flush()
    return source


def ingest_board(db: Session, board_token: str) -> None:
    source = get_or_create_job_source(db, board_token)

    run = IngestionRun(source_id=source.id, started_at=datetime.now(timezone.utc), status="running")
    db.add(run)
    db.commit()
    db.refresh(run)

    try:
        raw_jobs = fetch_jobs_for_board(board_token)
    except GreenhouseFetchError as e:
        logger.error("Ingestion failed for board '%s': %s", board_token, e)
        run.finished_at = datetime.now(timezone.utc)
        run.status = "failed"
        run.error_message = str(e)
        db.commit()
        return

    company_name = board_token.replace("-", " ").title()

    created_count, duplicate_count = 0, 0
    for raw_job in raw_jobs:
        raw_posting = RawPosting(source_id=source.id, raw_payload=raw_job, processed=False)
        db.add(raw_posting)
        db.commit()
        db.refresh(raw_posting)

        was_created = ingestion_service.process_raw_posting(db, raw_posting, company_name)
        if was_created:
            created_count += 1
        else:
            duplicate_count += 1

    run.finished_at = datetime.now(timezone.utc)
    run.records_fetched = len(raw_jobs)
    run.records_new = created_count
    run.records_duplicate = duplicate_count
    run.status = "success"
    db.commit()

    logger.info(
        "Board '%s': %d fetched, %d new, %d duplicate/skipped.",
        board_token,
        len(raw_jobs),
        created_count,
        duplicate_count,
    )


def run() -> None:
    db = SessionLocal()
    try:
        for board_token in BOARD_TOKENS:
            ingest_board(db, board_token)
    finally:
        db.close()


if __name__ == "__main__":
    run()
