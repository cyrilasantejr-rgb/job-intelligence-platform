"""
Tests for /jobs endpoints.

Uses an in-memory SQLite DB instead of Postgres so tests run fast and
without Docker. Only the tables actually needed for these tests are
created — the full schema includes Postgres-specific JSONB columns
(job_matches) that SQLite can't compile, so we create Company and Job
directly rather than the whole metadata.
"""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.db.base import Base
from app.db.session import get_db
from app.main import app
from app.models.company import Company  # noqa: F401  (registers table on Base.metadata)
from app.models.job import Job  # noqa: F401


@pytest.fixture()
def db_session():
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(bind=engine, tables=[Company.__table__, Job.__table__])
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


def make_job_payload(**overrides) -> dict:
    payload = {
        "company_name": "Acme Corp",
        "title": "Software Engineering Intern",
        "category": "Software Engineering",
        "employment_type": "Internship",
        "location": "New York, NY",
        "work_mode": "Hybrid",
        "description": "Work on backend systems.",
        "application_url": "https://example.com/apply",
    }
    payload.update(overrides)
    return payload


def test_create_job(client):
    response = client.post("/jobs", json=make_job_payload())
    assert response.status_code == 201
    body = response.json()
    assert body["title"] == "Software Engineering Intern"
    assert body["company"]["name"] == "Acme Corp"


def test_create_duplicate_job_returns_409(client):
    payload = make_job_payload()
    first = client.post("/jobs", json=payload)
    assert first.status_code == 201

    second = client.post("/jobs", json=payload)
    assert second.status_code == 409


def test_create_job_reuses_existing_company(client):
    client.post("/jobs", json=make_job_payload(title="Backend Intern"))
    response = client.post("/jobs", json=make_job_payload(title="Frontend Intern"))
    assert response.status_code == 201
    # Same company_name should resolve to the same company id both times.
    company_id_1 = client.get("/jobs?search=Backend").json()["items"][0]["company"]["id"]
    company_id_2 = response.json()["company"]["id"]
    assert company_id_1 == company_id_2


def test_list_jobs_empty(client):
    response = client.get("/jobs")
    assert response.status_code == 200
    body = response.json()
    assert body["items"] == []
    assert body["total"] == 0


def test_list_jobs_with_filters(client):
    client.post("/jobs", json=make_job_payload(title="SWE Intern", category="Software Engineering"))
    client.post(
        "/jobs",
        json=make_job_payload(
            title="Data Eng Intern", category="Data Engineering", company_name="Beta Inc"
        ),
    )

    response = client.get("/jobs", params={"category": "Data Engineering"})
    assert response.status_code == 200
    body = response.json()
    assert body["total"] == 1
    assert body["items"][0]["title"] == "Data Eng Intern"


def test_list_jobs_search(client):
    client.post("/jobs", json=make_job_payload(title="Backend Software Engineer"))
    client.post("/jobs", json=make_job_payload(title="Marketing Intern", company_name="Beta Inc"))

    response = client.get("/jobs", params={"search": "Software"})
    body = response.json()
    assert body["total"] == 1
    assert "Software" in body["items"][0]["title"]


def test_get_job_by_id(client):
    create_response = client.post("/jobs", json=make_job_payload())
    job_id = create_response.json()["id"]

    response = client.get(f"/jobs/{job_id}")
    assert response.status_code == 200
    assert response.json()["id"] == job_id


def test_get_job_not_found(client):
    response = client.get("/jobs/9999")
    assert response.status_code == 404


def test_pagination(client):
    for i in range(5):
        client.post("/jobs", json=make_job_payload(title=f"Intern Role {i}"))

    response = client.get("/jobs", params={"page": 1, "page_size": 2})
    body = response.json()
    assert len(body["items"]) == 2
    assert body["total"] == 5
