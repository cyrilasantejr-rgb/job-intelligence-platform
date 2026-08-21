"""
Turns raw Greenhouse job payloads into normalized Job records.

This is the "cleaning" step in the raw -> clean architecture: it reads
already-landed raw_postings rows and produces jobs rows, rather than
going straight from the API response to the jobs table. That separation
is what lets reprocessing happen later (e.g. improved categorization)
without re-fetching from Greenhouse.
"""

import html
import re
from datetime import date, datetime

from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.core.logging import get_logger
from app.models.raw_posting import RawPosting
from app.schemas.job import JobCreate
from app.services import job_service
from app.services.categorization import infer_category, infer_employment_type

logger = get_logger(__name__)

_TAG_RE = re.compile(r"<[^>]+>")


def strip_html(raw: str | None) -> str | None:
    """
    Converts a Greenhouse `content` HTML string into clean plain text.

    Greenhouse's payload is double-escaped: tags themselves arrive as
    entities (e.g. "&lt;div&gt;" rather than "<div>"), not just the inner
    text. So this unescapes first to turn those into real "<div>" tags,
    strips the now-literal tags, then unescapes again to resolve any
    remaining entities in the text content itself (e.g. "&nbsp;", "&amp;").
    """
    if not raw:
        return None
    text = html.unescape(raw)
    text = _TAG_RE.sub(" ", text)
    text = html.unescape(text)
    text = re.sub(r"\s+", " ", text).strip()
    return text or None


def _parse_greenhouse_date(value: str | None) -> date | None:
    if not value:
        return None
    try:
        return datetime.fromisoformat(value.replace("Z", "+00:00")).date()
    except ValueError:
        return None


def transform_greenhouse_job(raw_job: dict, company_name: str) -> JobCreate:
    """
    Maps a single Greenhouse job dict to our JobCreate schema.

    Greenhouse doesn't expose a "date posted" field directly — `updated_at`
    is used as a reasonable proxy. It's not perfectly accurate (a job could
    be edited without being newly posted), but it's the closest available
    signal without scraping the career page itself.
    """
    title = raw_job.get("title", "").strip()
    location = (raw_job.get("location") or {}).get("name")
    description = strip_html(raw_job.get("content"))

    return JobCreate(
        company_name=company_name,
        title=title,
        category=infer_category(title, description),
        employment_type=infer_employment_type(title),
        location=location,
        work_mode=None,
        description=description,
        application_url=raw_job.get("absolute_url"),
        date_posted=_parse_greenhouse_date(raw_job.get("updated_at")),
        deadline=None,
    )


def process_raw_posting(db: Session, raw_posting: RawPosting, company_name: str) -> bool:
    """
    Cleans and loads a single raw_postings row into `jobs`.

    Returns True if a new job was created, False if it was skipped
    (duplicate or malformed). Always marks the raw posting as processed,
    even on skip — a duplicate is a fully handled outcome, not an error.
    """
    try:
        job_in = transform_greenhouse_job(raw_posting.raw_payload, company_name)
        if not job_in.title:
            logger.warning("Raw posting %d has no title — skipping.", raw_posting.id)
            raw_posting.processed = True
            return False

        job = job_service.create_job(db, job_in)
        job.raw_posting_id = raw_posting.id
        raw_posting.processed = True
        db.commit()
        return True

    except HTTPException as e:
        db.rollback()
        raw_posting.processed = True
        db.commit()
        logger.info("Raw posting %d skipped: %s", raw_posting.id, e.detail)
        return False
