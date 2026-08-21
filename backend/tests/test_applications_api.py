"""
End-to-end tests for the application tracker: creation, status changes
with auto-logged events, manual event logging, and the timeline.
"""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.db.base import Base
from app.db.session import get_db
from app.main import app
from app.models.application import Application
from app.models.application_event import ApplicationEvent
from app.models.company import Company
from app.models.event_type import EventType
from app.models.job import Job
from app.models.user import User

EVENT_TYPES = [
    ("application_submitted", "Application Submitted", "Applied"),
    ("auto_confirmation", "Automated Confirmation Received", None),
    ("recruiter_response", "Recruiter Response Received", None),
    ("oa_received", "Online Assessment Received", "Online Assessment"),
    ("recruiter_screen_scheduled", "Recruiter Screen Scheduled", "Recruiter Screen"),
    ("technical_interview_scheduled", "Technical Interview Scheduled", "Technical Interview"),
    ("final_interview_scheduled", "Final Interview Scheduled", "Final Interview"),
    ("rejection_received", "Rejection Received", "Rejected"),
    ("offer_received", "Offer Received", "Offer"),
    ("withdrawn", "Application Withdrawn", "Withdrawn"),
]


@pytest.fixture()
def db_session():
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
            EventType.__table__,
            Application.__table__,
            ApplicationEvent.__table__,
        ],
    )
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    session = TestingSessionLocal()

    for code, display_name, maps_to_status in EVENT_TYPES:
        session.add(EventType(code=code, display_name=display_name, maps_to_status=maps_to_status))
    session.commit()

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


def create_test_job(client) -> int:
    payload = {"company_name": "Acme", "title": "Software Engineering Intern"}
    return client.post("/jobs", json=payload).json()["id"]


def test_create_application_starts_as_saved(client):
    job_id = create_test_job(client)
    response = client.post("/applications", json={"job_id": job_id})

    assert response.status_code == 201
    body = response.json()
    assert body["current_status"] == "Saved"
    assert body["job_id"] == job_id


def test_list_applications_includes_job_summary(client):
    job_id = create_test_job(client)
    client.post("/applications", json={"job_id": job_id})

    response = client.get("/applications")
    assert response.status_code == 200
    body = response.json()
    assert len(body) == 1
    assert body[0]["job"]["title"] == "Software Engineering Intern"
    assert body[0]["job"]["company_name"] == "Acme"


def test_get_application_detail(client):
    job_id = create_test_job(client)
    app_id = client.post("/applications", json={"job_id": job_id}).json()["id"]

    response = client.get(f"/applications/{app_id}")
    assert response.status_code == 200
    assert response.json()["job"]["title"] == "Software Engineering Intern"


def test_get_application_not_found(client):
    response = client.get("/applications/9999")
    assert response.status_code == 404


def test_status_update_auto_logs_event(client):
    job_id = create_test_job(client)
    app_id = client.post("/applications", json={"job_id": job_id}).json()["id"]

    response = client.patch(f"/applications/{app_id}/status", json={"new_status": "Applied"})
    assert response.status_code == 200
    assert response.json()["current_status"] == "Applied"

    events = client.get(f"/applications/{app_id}/events").json()
    assert len(events) == 1
    assert events[0]["event_type"]["code"] == "application_submitted"


def test_status_update_saved_logs_no_event(client):
    job_id = create_test_job(client)
    app_id = client.post("/applications", json={"job_id": job_id}).json()["id"]

    client.patch(f"/applications/{app_id}/status", json={"new_status": "Saved"})
    events = client.get(f"/applications/{app_id}/events").json()
    assert events == []


def test_status_update_invalid_status_rejected(client):
    job_id = create_test_job(client)
    app_id = client.post("/applications", json={"job_id": job_id}).json()["id"]

    response = client.patch(f"/applications/{app_id}/status", json={"new_status": "Not A Real Status"})
    assert response.status_code == 400


def test_full_pipeline_progression_builds_timeline(client):
    job_id = create_test_job(client)
    app_id = client.post("/applications", json={"job_id": job_id}).json()["id"]

    for new_status in ["Applied", "Online Assessment", "Technical Interview", "Offer"]:
        response = client.patch(f"/applications/{app_id}/status", json={"new_status": new_status})
        assert response.status_code == 200

    events = client.get(f"/applications/{app_id}/events").json()
    assert len(events) == 4
    codes = [e["event_type"]["code"] for e in events]
    assert codes == [
        "application_submitted",
        "oa_received",
        "technical_interview_scheduled",
        "offer_received",
    ]


def test_manual_event_does_not_change_status(client):
    job_id = create_test_job(client)
    app_id = client.post("/applications", json={"job_id": job_id}).json()["id"]
    client.patch(f"/applications/{app_id}/status", json={"new_status": "Applied"})

    event_payload = {
        "event_type_code": "recruiter_response",
        "sender": "recruiter@acme.com",
        "subject": "Following up",
        "notes": "Asked about my availability next week.",
        "source": "email",
        "is_automated": False,
        "requires_response": True,
    }
    response = client.post(f"/applications/{app_id}/events", json=event_payload)
    assert response.status_code == 201
    assert response.json()["sender"] == "recruiter@acme.com"

    application = client.get(f"/applications/{app_id}").json()
    assert application["current_status"] == "Applied"

    events = client.get(f"/applications/{app_id}/events").json()
    assert len(events) == 2


def test_manual_event_unknown_code_returns_400(client):
    job_id = create_test_job(client)
    app_id = client.post("/applications", json={"job_id": job_id}).json()["id"]

    response = client.post(
        f"/applications/{app_id}/events", json={"event_type_code": "not_a_real_code"}
    )
    assert response.status_code == 400


def test_events_ordered_chronologically(client):
    job_id = create_test_job(client)
    app_id = client.post("/applications", json={"job_id": job_id}).json()["id"]

    client.post(
        f"/applications/{app_id}/events",
        json={"event_type_code": "auto_confirmation", "event_date": "2026-08-20T10:00:00Z"},
    )
    client.post(
        f"/applications/{app_id}/events",
        json={"event_type_code": "recruiter_response", "event_date": "2026-08-18T10:00:00Z"},
    )

    events = client.get(f"/applications/{app_id}/events").json()
    assert events[0]["event_type"]["code"] == "recruiter_response"
    assert events[1]["event_type"]["code"] == "auto_confirmation"


def test_list_event_types(client):
    response = client.get("/event-types")
    assert response.status_code == 200
    codes = [et["code"] for et in response.json()]
    assert "application_submitted" in codes
    assert "offer_received" in codes
