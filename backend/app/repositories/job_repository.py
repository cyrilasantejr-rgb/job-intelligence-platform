"""
Job data-access layer.

Keeps raw SQLAlchemy query construction out of the service layer, so the
service can focus on business rules (dedup, normalization) and the routes
can focus on HTTP concerns. Nothing in here should know about Pydantic
schemas or HTTP status codes.
"""

from sqlalchemy import func, select
from sqlalchemy.orm import Session, joinedload

from app.models.company import Company
from app.models.job import Job


def get_company_by_normalized_name(db: Session, normalized_name: str) -> Company | None:
    stmt = select(Company).where(Company.normalized_name == normalized_name)
    return db.execute(stmt).scalar_one_or_none()


def create_company(db: Session, name: str, normalized_name: str) -> Company:
    company = Company(name=name, normalized_name=normalized_name)
    db.add(company)
    db.flush()  # populate company.id without committing yet
    return company


def get_job_by_dedup_hash(db: Session, dedup_hash: str) -> Job | None:
    stmt = select(Job).where(Job.dedup_hash == dedup_hash)
    return db.execute(stmt).scalar_one_or_none()


def create_job(db: Session, job: Job) -> Job:
    db.add(job)
    db.commit()
    db.refresh(job)
    return job


def get_job_by_id(db: Session, job_id: int) -> Job | None:
    stmt = select(Job).options(joinedload(Job.company)).where(Job.id == job_id)
    return db.execute(stmt).scalar_one_or_none()


def list_jobs(
    db: Session,
    *,
    category: str | None = None,
    employment_type: str | None = None,
    work_mode: str | None = None,
    location: str | None = None,
    search: str | None = None,
    page: int = 1,
    page_size: int = 20,
) -> tuple[list[Job], int]:
    """
    Returns (items, total_count) for the given filters, paginated.

    `search` does a simple case-insensitive match against title and
    description — good enough for the MVP; full-text search can replace
    this later without changing the function's signature.
    """
    stmt = select(Job).options(joinedload(Job.company))
    count_stmt = select(func.count()).select_from(Job)

    if category:
        stmt = stmt.where(Job.category == category)
        count_stmt = count_stmt.where(Job.category == category)
    if employment_type:
        stmt = stmt.where(Job.employment_type == employment_type)
        count_stmt = count_stmt.where(Job.employment_type == employment_type)
    if work_mode:
        stmt = stmt.where(Job.work_mode == work_mode)
        count_stmt = count_stmt.where(Job.work_mode == work_mode)
    if location:
        stmt = stmt.where(Job.location.ilike(f"%{location}%"))
        count_stmt = count_stmt.where(Job.location.ilike(f"%{location}%"))
    if search:
        pattern = f"%{search}%"
        search_clause = Job.title.ilike(pattern) | Job.description.ilike(pattern)
        stmt = stmt.where(search_clause)
        count_stmt = count_stmt.where(search_clause)

    total = db.execute(count_stmt).scalar_one()

    stmt = stmt.order_by(Job.created_at.desc()).offset((page - 1) * page_size).limit(page_size)
    items = list(db.execute(stmt).scalars().all())

    return items, total
