"""
Job endpoints.

Routes stay thin — validation via Pydantic schemas, everything else
delegated to app.services.job_service and app.repositories.job_repository.
"""

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.repositories import job_repository
from app.schemas.job import JobCreate, JobListResponse, JobRead
from app.services import job_service

router = APIRouter(prefix="/jobs", tags=["jobs"])


@router.post("", response_model=JobRead, status_code=201)
def create_job(job_in: JobCreate, db: Session = Depends(get_db)) -> JobRead:
    job = job_service.create_job(db, job_in)
    return job


@router.get("", response_model=JobListResponse)
def list_jobs(
    category: str | None = Query(None, description="e.g. 'Software Engineering', 'Data Engineering'"),
    employment_type: str | None = Query(None, description="'Internship' or 'New Grad'"),
    work_mode: str | None = Query(None, description="'Remote', 'Hybrid', or 'On-site'"),
    location: str | None = Query(None, description="Partial match, e.g. 'New York'"),
    search: str | None = Query(None, description="Matches against title and description"),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
) -> JobListResponse:
    items, total = job_repository.list_jobs(
        db,
        category=category,
        employment_type=employment_type,
        work_mode=work_mode,
        location=location,
        search=search,
        page=page,
        page_size=page_size,
    )
    return JobListResponse(items=items, total=total, page=page, page_size=page_size)


@router.get("/{job_id}", response_model=JobRead)
def get_job(job_id: int, db: Session = Depends(get_db)) -> JobRead:
    return job_service.get_job_or_404(db, job_id)
