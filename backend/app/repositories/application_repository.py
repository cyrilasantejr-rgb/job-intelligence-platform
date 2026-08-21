"""
Application and application-event data access.

Same split as job_repository: raw query construction lives here, business
rules (status transitions, auto-logging) live in the service layer.
"""

from sqlalchemy import select
from sqlalchemy.orm import Session, joinedload

from app.models.application import Application
from app.models.application_event import ApplicationEvent
from app.models.event_type import EventType
from app.models.job import Job


def create_application(
    db: Session, user_id: int, job_id: int, resume_id: int | None, notes: str | None
) -> Application:
    application = Application(
        user_id=user_id,
        job_id=job_id,
        resume_id=resume_id,
        notes=notes,
        current_status="Saved",
    )
    db.add(application)
    db.commit()
    db.refresh(application)
    return application


def get_application_by_id(db: Session, application_id: int) -> Application | None:
    stmt = (
        select(Application)
        .options(joinedload(Application.job).joinedload(Job.company))
        .where(Application.id == application_id)
    )
    return db.execute(stmt).scalar_one_or_none()


def list_applications(db: Session, user_id: int) -> list[Application]:
    stmt = (
        select(Application)
        .options(joinedload(Application.job).joinedload(Job.company))
        .where(Application.user_id == user_id)
        .order_by(Application.created_at.desc())
    )
    return list(db.execute(stmt).unique().scalars().all())


def get_event_type_by_code(db: Session, code: str) -> EventType | None:
    stmt = select(EventType).where(EventType.code == code)
    return db.execute(stmt).scalar_one_or_none()


def get_event_type_mapping_to_status(db: Session, status: str) -> EventType | None:
    stmt = select(EventType).where(EventType.maps_to_status == status)
    return db.execute(stmt).scalar_one_or_none()


def list_event_types(db: Session) -> list[EventType]:
    stmt = select(EventType).order_by(EventType.id)
    return list(db.execute(stmt).scalars().all())


def create_event(db: Session, application_id: int, event_type_id: int, **fields) -> ApplicationEvent:
    event = ApplicationEvent(
        application_id=application_id,
        event_type_id=event_type_id,
        **fields,
    )
    db.add(event)
    db.commit()
    db.refresh(event)
    return event


def list_events(db: Session, application_id: int) -> list[ApplicationEvent]:
    stmt = (
        select(ApplicationEvent)
        .options(joinedload(ApplicationEvent.event_type))
        .where(ApplicationEvent.application_id == application_id)
        .order_by(ApplicationEvent.event_date.asc())
    )
    return list(db.execute(stmt).scalars().all())
