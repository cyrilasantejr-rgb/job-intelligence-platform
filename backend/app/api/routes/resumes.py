"""
Resume endpoints.

No auth yet, so these operate against the single default user
(see app.services.user_service). Every route here is scoped to "the
current person using this instance" rather than a specific logged-in user.
"""

from fastapi import APIRouter, Depends, File, Form, UploadFile
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.resume import Resume
from app.schemas.resume import ResumeRead, ResumeUploadResponse
from app.services import resume_service
from app.services.user_service import get_or_create_default_user

router = APIRouter(prefix="/resumes", tags=["resumes"])


@router.post("", response_model=ResumeUploadResponse, status_code=201)
async def upload_resume(
    file: UploadFile = File(...),
    version_label: str | None = Form(None),
    db: Session = Depends(get_db),
) -> ResumeUploadResponse:
    resume, extracted_skills = await resume_service.create_resume(db, file, version_label)
    return ResumeUploadResponse(resume=resume, extracted_skills=extracted_skills)


@router.get("", response_model=list[ResumeRead])
def list_resumes(db: Session = Depends(get_db)) -> list[ResumeRead]:
    user = get_or_create_default_user(db)
    db.commit()
    stmt = select(Resume).where(Resume.user_id == user.id).order_by(Resume.uploaded_at.desc())
    return list(db.execute(stmt).scalars().all())
