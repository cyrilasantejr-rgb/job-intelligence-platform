"""
Application business logic.

Key design decision (matches what we discussed when designing the
timeline): status changes are an explicit user action, and changing
status auto-logs the corresponding event — but the reverse never happens.
Logging a manual event (e.g. "Recruiter Response Received") never
silently changes current_status. One direction only, so the Kanban
column always reflects a deliberate choice, not an inferred one.
"""

from datetime import datetime, timezone

from fastapi import HTTPException, status as http_status
from sqlalchemy.orm import Session

from app.models.application import Application
from app.models.application_event import ApplicationEvent
from app.repositories import application_repository
from app.schemas.application import APPLICATION_STATUSES, ApplicationEventCreate
from app.services.user_service import get_or_create_default_user


def create_application(
    db: Session, job_id: int, resume_id: int | None, notes: str | None
) -> Application:
    user = get_or_create_default_user(db)
    db.commit()
    return application_repository.create_application(db, user.id, job_id, resume_id, notes)


def get_application_or_404(db: Session, application_id: int) -> Application:
    application = application_repository.get_application_by_id(db, application_id)
    if application is None:
        raise HTTPException(status_code=http_status.HTTP_404_NOT_FOUND, detail="Application not found")
    return application


def update_status(db: Session, application_id: int, new_status: str) -> Application:
    if new_status not in APPLICATION_STATUSES:
        raise HTTPException(
            status_code=http_status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid status '{new_status}'. Must be one of: {', '.join(APPLICATION_STATUSES)}",
        )

    application = get_application_or_404(db, application_id)
    application.current_status = new_status

    event_type = application_repository.get_event_type_mapping_to_status(db, new_status)
    if event_type is not None:
        application_repository.create_event(
            db,
            application_id=application.id,
            event_type_id=event_type.id,
            event_date=datetime.now(timezone.utc),
            source="manual",
            created_by="user",
            notes=f"Status changed to {new_status}",
        )

    db.commit()
    db.refresh(application)
    return application


def add_event(db: Session, application_id: int, event_in: ApplicationEventCreate) -> ApplicationEvent:
    get_application_or_404(db, application_id)

    event_type = application_repository.get_event_type_by_code(db, event_in.event_type_code)
    if event_type is None:
        raise HTTPException(
            status_code=http_status.HTTP_400_BAD_REQUEST,
            detail=f"Unknown event type code '{event_in.event_type_code}'. See GET /event-types.",
        )

    event_date = event_in.event_date or datetime.now(timezone.utc)

    return application_repository.create_event(
        db,
        application_id=application_id,
        event_type_id=event_type.id,
        event_date=event_date,
        source=event_in.source,
        sender=event_in.sender,
        subject=event_in.subject,
        notes=event_in.notes,
        is_automated=event_in.is_automated,
        requires_response=event_in.requires_response,
        responded=event_in.responded,
        response_date=event_in.response_date,
        next_action=event_in.next_action,
        deadline=event_in.deadline,
        created_by="user",
    )
