"""
Seeds a handful of realistic sample jobs so there's something to look at
before real ingestion (Phase 3) exists.

Run with:
    docker compose exec backend python -m app.scripts.seed_jobs
"""

from datetime import date

from app.db.session import SessionLocal
from app.schemas.job import JobCreate
from app.services import job_service
from app.core.logging import get_logger

logger = get_logger(__name__)

SAMPLE_JOBS = [
    JobCreate(
        company_name="Google",
        title="Software Engineering Intern",
        category="Software Engineering",
        employment_type="Internship",
        location="Mountain View, CA",
        work_mode="On-site",
        salary_min=8000,
        salary_max=9500,
        description="Work on large-scale distributed systems alongside senior engineers.",
        application_url="https://careers.google.com/jobs/example",
        date_posted=date(2026, 8, 1),
        deadline=date(2026, 10, 1),
    ),
    JobCreate(
        company_name="Google",
        title="Data Engineer, New Grad",
        category="Data Engineering",
        employment_type="New Grad",
        location="New York, NY",
        work_mode="Hybrid",
        salary_min=120000,
        salary_max=150000,
        description="Build and maintain data pipelines powering analytics products.",
        application_url="https://careers.google.com/jobs/example-2",
        date_posted=date(2026, 8, 5),
    ),
    JobCreate(
        company_name="Netflix",
        title="Machine Learning Intern",
        category="Machine Learning / AI",
        employment_type="Internship",
        location="Los Gatos, CA",
        work_mode="On-site",
        description="Work on recommendation systems and personalization models.",
        application_url="https://jobs.netflix.com/example",
        date_posted=date(2026, 7, 20),
        deadline=date(2026, 9, 15),
    ),
    JobCreate(
        company_name="Stripe",
        title="Backend Software Engineer, New Grad",
        category="Software Engineering",
        employment_type="New Grad",
        location="Remote",
        work_mode="Remote",
        salary_min=130000,
        salary_max=160000,
        description="Build reliable, scalable payment infrastructure.",
        application_url="https://stripe.com/jobs/example",
        date_posted=date(2026, 8, 10),
    ),
    JobCreate(
        company_name="Snowflake",
        title="Cloud Platform Engineering Intern",
        category="Cloud / Platform Engineering",
        employment_type="Internship",
        location="San Mateo, CA",
        work_mode="Hybrid",
        description="Work on core platform infrastructure powering the Snowflake data cloud.",
        application_url="https://careers.snowflake.com/example",
        date_posted=date(2026, 8, 3),
        deadline=date(2026, 9, 30),
    ),
    JobCreate(
        company_name="Meta",
        title="Data Analyst, New Grad",
        category="Data Analytics",
        employment_type="New Grad",
        location="Menlo Park, CA",
        work_mode="On-site",
        salary_min=100000,
        salary_max=125000,
        description="Analyze product data to drive decisions across the Family of Apps.",
        application_url="https://metacareers.com/jobs/example",
        date_posted=date(2026, 8, 8),
    ),
]


def seed() -> None:
    db = SessionLocal()
    created, skipped = 0, 0
    try:
        for job_in in SAMPLE_JOBS:
            try:
                job_service.create_job(db, job_in)
                created += 1
            except Exception as e:  # noqa: BLE001 — deliberately broad for a seed script
                # Most likely a 409 duplicate on re-run; that's expected and fine.
                db.rollback()
                skipped += 1
                logger.info("Skipped '%s' at %s: %s", job_in.title, job_in.company_name, e)
    finally:
        db.close()

    logger.info("Seed complete: %d created, %d skipped", created, skipped)


if __name__ == "__main__":
    seed()
