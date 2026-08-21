"""
Resume-to-job matching.

Scope note: this implements skill-overlap matching only — a real,
explainable score, not a fabricated percentage. The original design
called for a weighted formula also covering experience relevance,
semantic similarity, and education (40/30/20/10 split); those need
resume experience/education parsing and embeddings, which are bigger
pieces of work appropriately left for later. Those score fields exist
and are left null here, ready to be filled in without a schema change
or a change to this function's return shape.
"""

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.job import Job
from app.models.job_match import JobMatch
from app.models.job_skill import UserSkill
from app.models.resume import Resume
from app.models.skill import Skill
from app.services.job_service import get_job_or_404
from app.services.skills_taxonomy import extract_skills


def _get_resume_skills(db: Session, resume_id: int) -> set[str]:
    stmt = (
        select(Skill.name)
        .join(UserSkill, UserSkill.skill_id == Skill.id)
        .where(UserSkill.resume_id == resume_id)
    )
    return set(db.execute(stmt).scalars().all())


def _get_job_skills(job: Job) -> set[str]:
    """
    Job skills are extracted on demand from title + description rather
    than read from the job_skills table. job_skills exists in the schema
    for future use (e.g. structured "required" vs "preferred" tagging by
    the ingestion pipeline), but populating it wasn't part of Phase 3 —
    on-demand extraction gets matching working now without a backfill.
    """
    text = f"{job.title} {job.description or ''}"
    return set(extract_skills(text))


def _build_explanation(matched: list[str], missing: list[str], score: float | None) -> str:
    if score is None:
        return "This job posting doesn't mention any recognized technical skills, so a skill-based match couldn't be computed."

    if not matched and not missing:
        return "No specific technical skills were detected in either the resume or this job posting."

    parts = []
    if matched:
        parts.append(f"Matches on {', '.join(matched)}")
    if missing:
        parts.append(f"missing {', '.join(missing)}")

    summary = "; ".join(parts) + "."
    return f"{summary} Overall skill overlap: {score}%."


def compute_match(db: Session, resume_id: int, job_id: int) -> JobMatch:
    job = get_job_or_404(db, job_id)

    resume = db.get(Resume, resume_id)
    if resume is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Resume not found")

    resume_skills = _get_resume_skills(db, resume_id)
    job_skills = _get_job_skills(job)

    matched = sorted(resume_skills & job_skills)
    missing = sorted(job_skills - resume_skills)

    if job_skills:
        skill_score = round(len(matched) / len(job_skills) * 100, 1)
    else:
        skill_score = None

    explanation = _build_explanation(matched, missing, skill_score)

    match = JobMatch(
        job_id=job_id,
        resume_id=resume_id,
        skill_score=skill_score,
        experience_score=None,
        semantic_score=None,
        education_score=None,
        overall_score=skill_score,
        matched_skills=matched,
        missing_skills=missing,
        explanation=explanation,
    )
    db.add(match)
    db.commit()
    db.refresh(match)
    return match
