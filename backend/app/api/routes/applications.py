"""
Application tracking endpoints: create/list/detail, status changes
(Kanban), and the event timeline.
"""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.repositories import application_repository
from app.schemas.application import (
    ApplicationCreate,
    ApplicationDetail,
    ApplicationEventCreate,
    ApplicationEventRead,
    ApplicationRead,
    ApplicationStatusUpdate,
    EventTypeRead,
    JobSummary,
)
from app.services import application_service
from app.services.user_service import get_or_create_default_user

router = APIRouter(tags=["applications"])


@router.post("/applications", response_model=ApplicationRead, status_code=201)
def create_application(payload: ApplicationCreate, db: Session = Depends(get_db)) -> ApplicationRead:
    return application_service.create_application(db, payload.job_id, payload.resume_id, payload.notes)


@router.get("/applications", response_model=list[ApplicationDetail])
def list_applications(db: Session = Depends(get_db)) -> list[ApplicationDetail]:
    user = get_or_create_default_user(db)
    db.commit()
    applications = application_repository.list_applications(db, user.id)
    return [
        ApplicationDetail(
            **ApplicationRead.model_validate(app).model_dump(),
            job=JobSummary.from_job(app.job),
        )
        for app in applications
    ]


@router.get("/applications/{application_id}", response_model=ApplicationDetail)
def get_application(application_id: int, db: Session = Depends(get_db)) -> ApplicationDetail:
    application = application_service.get_application_or_404(db, application_id)
    return ApplicationDetail(
        **ApplicationRead.model_validate(application).model_dump(),
        job=JobSummary.from_job(application.job),
    )


@router.patch("/applications/{application_id}/status", response_model=ApplicationRead)
def update_application_status(
    application_id: int, payload: ApplicationStatusUpdate, db: Session = Depends(get_db)
) -> ApplicationRead:
    return application_service.update_status(db, application_id, payload.new_status)


@router.get("/applications/{application_id}/events", response_model=list[ApplicationEventRead])
def list_application_events(application_id: int, db: Session = Depends(get_db)) -> list[ApplicationEventRead]:
    application_service.get_application_or_404(db, application_id)
    return application_repository.list_events(db, application_id)


@router.post("/applications/{application_id}/events", response_model=ApplicationEventRead, status_code=201)
def create_application_event(
    application_id: int, payload: ApplicationEventCreate, db: Session = Depends(get_db)
) -> ApplicationEventRead:
    return application_service.add_event(db, application_id, payload)


@router.get("/event-types", response_model=list[EventTypeRead])
def list_event_types(db: Session = Depends(get_db)) -> list[EventTypeRead]:
    return application_repository.list_event_types(db)
