"""
Resume upload and text extraction.

Supports PDF, DOCX, and plain text — the three formats a person is
realistically going to upload a resume as. Extraction failures raise
HTTPException directly since this is only ever called from a route
handler; there's no reuse case yet that needs a cleaner exception type.
"""

import re
import uuid
from pathlib import Path

import pdfplumber
from docx import Document
from fastapi import HTTPException, UploadFile, status
from sqlalchemy.orm import Session

from app.core.logging import get_logger
from app.models.resume import Resume
from app.models.skill import Skill
from app.models.job_skill import UserSkill
from app.services.skills_taxonomy import extract_skills
from app.services.user_service import get_or_create_default_user

logger = get_logger(__name__)

UPLOAD_DIR = Path("uploads/resumes")
SUPPORTED_EXTENSIONS = {".pdf", ".docx", ".txt"}


def _extract_text_from_pdf(file_bytes: bytes) -> str:
    import io

    text_parts: list[str] = []
    with pdfplumber.open(io.BytesIO(file_bytes)) as pdf:
        for page in pdf.pages:
            page_text = page.extract_text()
            if page_text:
                text_parts.append(page_text)
    return "\n".join(text_parts)


def _extract_text_from_docx(file_bytes: bytes) -> str:
    import io

    document = Document(io.BytesIO(file_bytes))
    return "\n".join(paragraph.text for paragraph in document.paragraphs)


def extract_resume_text(filename: str, file_bytes: bytes) -> str:
    extension = Path(filename).suffix.lower()

    if extension == ".pdf":
        text = _extract_text_from_pdf(file_bytes)
    elif extension == ".docx":
        text = _extract_text_from_docx(file_bytes)
    elif extension == ".txt":
        text = file_bytes.decode("utf-8", errors="replace")
    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Unsupported file type '{extension}'. Supported: {', '.join(sorted(SUPPORTED_EXTENSIONS))}",
        )

    text = re.sub(r"\s+", " ", text).strip()
    if not text:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Couldn't extract any text from this file — it may be a scanned image or empty.",
        )
    return text


def _get_or_create_skill(db: Session, name: str) -> Skill:
    skill = db.query(Skill).filter(Skill.name == name).one_or_none()
    if skill is None:
        skill = Skill(name=name)
        db.add(skill)
        db.flush()
    return skill


def save_resume_skills(db: Session, resume_id: int, skill_names: list[str]) -> None:
    for name in skill_names:
        skill = _get_or_create_skill(db, name)
        exists = (
            db.query(UserSkill)
            .filter(UserSkill.resume_id == resume_id, UserSkill.skill_id == skill.id)
            .one_or_none()
        )
        if exists is None:
            db.add(UserSkill(resume_id=resume_id, skill_id=skill.id))


async def create_resume(
    db: Session, file: UploadFile, version_label: str | None = None
) -> tuple[Resume, list[str]]:
    """
    Handles a resume upload end to end: extracts text, saves the file to
    disk, creates the Resume row, extracts skills, and links them via
    UserSkill. Returns the created Resume and the list of extracted
    skill names.
    """
    file_bytes = await file.read()
    parsed_text = extract_resume_text(file.filename, file_bytes)

    UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
    extension = Path(file.filename).suffix.lower()
    stored_filename = f"{uuid.uuid4().hex}{extension}"
    file_path = UPLOAD_DIR / stored_filename
    file_path.write_bytes(file_bytes)

    user = get_or_create_default_user(db)

    resume = Resume(
        user_id=user.id,
        file_path=str(file_path),
        version_label=version_label,
        parsed_text=parsed_text,
    )
    db.add(resume)
    db.flush()

    skill_names = extract_skills(parsed_text)
    save_resume_skills(db, resume.id, skill_names)

    db.commit()
    db.refresh(resume)

    logger.info("Resume %d created with %d extracted skills.", resume.id, len(skill_names))
    return resume, skill_names
