"""
Match endpoints: compute a resume-to-job match, or list existing matches
for a resume ranked by score.
"""

from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.job_match import JobMatch
from app.schemas.job_match import JobMatchRead
from app.services import matching_service

router = APIRouter(tags=["matches"])


@router.post("/jobs/{job_id}/match", response_model=JobMatchRead, status_code=201)
def compute_match(job_id: int, resume_id: int, db: Session = Depends(get_db)) -> JobMatchRead:
    """
    Computes a match between the given resume and job, and stores it.
    Every call creates a new JobMatch row (rather than overwriting) so
    match history is preserved — e.g. to compare scores before/after a
    resume update.
    """
    return matching_service.compute_match(db, resume_id=resume_id, job_id=job_id)


@router.get("/resumes/{resume_id}/matches", response_model=list[JobMatchRead])
def list_matches_for_resume(resume_id: int, db: Session = Depends(get_db)) -> list[JobMatchRead]:
    stmt = (
        select(JobMatch)
        .where(JobMatch.resume_id == resume_id)
        .order_by(JobMatch.overall_score.desc().nulls_last(), JobMatch.computed_at.desc())
    )
    return list(db.execute(stmt).scalars().all())
