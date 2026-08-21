"""
End-to-end tests for the resume upload -> matching flow, using an
in-memory SQLite DB (same pattern as test_jobs.py). Only the tables these
tests actually touch are created; job_matches uses JSONB (Postgres-only)
for matched_skills/missing_skills, so we swap in plain JSON for the
SQLite test schema — production still uses real JSONB via Alembic.
"""

import io

import pytest
from docx import Document
from fastapi.testclient import TestClient
from sqlalchemy import JSON, create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.db.base import Base
from app.db.session import get_db
from app.main import app
from app.models.company import Company
from app.models.job import Job
from app.models.job_match import JobMatch
from app.models.job_skill import UserSkill
from app.models.resume import Resume
from app.models.skill import Skill
from app.models.user import User


def make_docx_bytes(paragraphs: list[str]) -> bytes:
    doc = Document()
    for p in paragraphs:
        doc.add_paragraph(p)
    buf = io.BytesIO()
    doc.save(buf)
    return buf.getvalue()


@pytest.fixture()
def db_session(monkeypatch):
    monkeypatch.setattr(JobMatch.__table__.c.matched_skills, "type", JSON())
    monkeypatch.setattr(JobMatch.__table__.c.missing_skills, "type", JSON())

    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(
        bind=engine,
        tables=[
            Company.__table__,
            Job.__table__,
            User.__table__,
            Resume.__table__,
            Skill.__table__,
            UserSkill.__table__,
            JobMatch.__table__,
        ],
    )
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()


@pytest.fixture()
def client(db_session):
    def override_get_db():
        try:
            yield db_session
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db
    yield TestClient(app)
    app.dependency_overrides.clear()


def test_upload_resume_txt(client):
    files = {"file": ("resume.txt", b"Experienced in Python, SQL, and AWS.", "text/plain")}
    response = client.post("/resumes", files=files, data={"version_label": "v1"})

    assert response.status_code == 201
    body = response.json()
    assert body["resume"]["version_label"] == "v1"
    assert set(body["extracted_skills"]) == {"AWS", "Python", "SQL"}


def test_upload_resume_docx(client):
    docx_bytes = make_docx_bytes(["Skills: Python, Airflow, dbt, PostgreSQL"])
    files = {
        "file": (
            "resume.docx",
            docx_bytes,
            "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        )
    }
    response = client.post("/resumes", files=files)

    assert response.status_code == 201
    body = response.json()
    assert "Airflow" in body["extracted_skills"]
    assert "PostgreSQL" in body["extracted_skills"]


def test_upload_resume_unsupported_type_returns_400(client):
    files = {"file": ("resume.pages", b"whatever", "application/octet-stream")}
    response = client.post("/resumes", files=files)
    assert response.status_code == 400


def test_list_resumes(client):
    files = {"file": ("resume.txt", b"Python developer", "text/plain")}
    client.post("/resumes", files=files)

    response = client.get("/resumes")
    assert response.status_code == 200
    assert len(response.json()) == 1


def test_compute_match_full_overlap(client):
    files = {"file": ("resume.txt", b"Skilled in Python and SQL.", "text/plain")}
    resume_id = client.post("/resumes", files=files).json()["resume"]["id"]

    job_payload = {
        "company_name": "Acme",
        "title": "Software Engineering Intern",
        "description": "Looking for someone skilled in Python and SQL.",
    }
    job_id = client.post("/jobs", json=job_payload).json()["id"]

    response = client.post(f"/jobs/{job_id}/match", params={"resume_id": resume_id})
    assert response.status_code == 201
    body = response.json()
    assert body["skill_score"] == 100.0
    assert body["overall_score"] == 100.0
    assert set(body["matched_skills"]) == {"Python", "SQL"}
    assert body["missing_skills"] == []


def test_compute_match_partial_overlap(client):
    files = {"file": ("resume.txt", b"Skilled in Python only.", "text/plain")}
    resume_id = client.post("/resumes", files=files).json()["resume"]["id"]

    job_payload = {
        "company_name": "Acme",
        "title": "Data Engineer Intern",
        "description": "Needs Python, SQL, and Airflow experience.",
    }
    job_id = client.post("/jobs", json=job_payload).json()["id"]

    response = client.post(f"/jobs/{job_id}/match", params={"resume_id": resume_id})
    body = response.json()
    assert body["matched_skills"] == ["Python"]
    assert set(body["missing_skills"]) == {"Airflow", "SQL"}
    assert 0 < body["skill_score"] < 100


def test_compute_match_job_with_no_detected_skills(client):
    files = {"file": ("resume.txt", b"Python developer.", "text/plain")}
    resume_id = client.post("/resumes", files=files).json()["resume"]["id"]

    job_payload = {
        "company_name": "Acme",
        "title": "Executive Assistant",
        "description": "Manage calendars and coordinate meetings.",
    }
    job_id = client.post("/jobs", json=job_payload).json()["id"]

    response = client.post(f"/jobs/{job_id}/match", params={"resume_id": resume_id})
    body = response.json()
    assert body["skill_score"] is None
    assert "couldn't be computed" in body["explanation"]


def test_compute_match_resume_not_found(client):
    job_payload = {"company_name": "Acme", "title": "Software Engineer"}
    job_id = client.post("/jobs", json=job_payload).json()["id"]

    response = client.post(f"/jobs/{job_id}/match", params={"resume_id": 9999})
    assert response.status_code == 404


def test_list_matches_for_resume_ranked(client):
    files = {"file": ("resume.txt", b"Python, SQL, AWS, Airflow expert.", "text/plain")}
    resume_id = client.post("/resumes", files=files).json()["resume"]["id"]

    strong_job = client.post(
        "/jobs",
        json={"company_name": "A", "title": "Job A", "description": "Needs Python."},
    ).json()["id"]
    weak_job = client.post(
        "/jobs",
        json={
            "company_name": "B",
            "title": "Job B",
            "description": "Needs Python, SQL, AWS, Airflow, and also Kubernetes and Docker.",
        },
    ).json()["id"]

    client.post(f"/jobs/{strong_job}/match", params={"resume_id": resume_id})
    client.post(f"/jobs/{weak_job}/match", params={"resume_id": resume_id})

    response = client.get(f"/resumes/{resume_id}/matches")
    results = response.json()
    assert len(results) == 2
    assert results[0]["overall_score"] >= results[1]["overall_score"]
