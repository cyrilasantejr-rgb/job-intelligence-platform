"""
Job business logic: company get-or-create, dedup hashing, duplicate handling.

This is intentionally the only place that knows how a dedup_hash is
computed. If the hashing strategy changes later (e.g. adding a fuzzy-match
step), only this module needs to change.
"""

import hashlib
import re

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models.job import Job
from app.repositories import job_repository
from app.schemas.job import JobCreate


def normalize_text(value: str) -> str:
    """Lowercase, strip, and collapse internal whitespace — used for both
    company-name matching and dedup-hash inputs so 'Google  Inc.' and
    'google inc.' are treated as the same value."""
    return re.sub(r"\s+", " ", value.strip().lower())


def compute_dedup_hash(company_normalized_name: str, title: str, location: str | None) -> str:
    """
    Dedup key: normalized(company + title + location).

    This is a starting strategy, not a final one — it will miss near-dupes
    like "Software Engineer Intern" vs "Software Engineering Intern" at the
    same company. Fuzzy matching can replace this later (Phase 3) without
    changing anything that calls this function.
    """
    parts = [
        company_normalized_name,
        normalize_text(title),
        normalize_text(location) if location else "",
    ]
    raw = "|".join(parts)
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()


def get_or_create_company(db: Session, company_name: str):
    normalized = normalize_text(company_name)
    company = job_repository.get_company_by_normalized_name(db, normalized)
    if company is None:
        company = job_repository.create_company(db, name=company_name, normalized_name=normalized)
    return company


def create_job(db: Session, job_in: JobCreate) -> Job:
    company = get_or_create_company(db, job_in.company_name)

    dedup_hash = compute_dedup_hash(company.normalized_name, job_in.title, job_in.location)

    existing = job_repository.get_job_by_dedup_hash(db, dedup_hash)
    if existing is not None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"A job with this company, title, and location already exists (id={existing.id}).",
        )

    job = Job(
        company_id=company.id,
        title=job_in.title,
        category=job_in.category,
        employment_type=job_in.employment_type,
        location=job_in.location,
        work_mode=job_in.work_mode,
        salary_min=job_in.salary_min,
        salary_max=job_in.salary_max,
        description=job_in.description,
        application_url=job_in.application_url,
        date_posted=job_in.date_posted,
        deadline=job_in.deadline,
        dedup_hash=dedup_hash,
    )

    return job_repository.create_job(db, job)


def get_job_or_404(db: Session, job_id: int) -> Job:
    job = job_repository.get_job_by_id(db, job_id)
    if job is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Job not found")
    return job
