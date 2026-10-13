import uuid

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.security_event import SecurityEvent


def list_security_events(
    db: Session, project_id: uuid.UUID | None = None
) -> list[SecurityEvent]:
    stmt = select(SecurityEvent).order_by(SecurityEvent.created_at.desc())
    if project_id is not None:
        stmt = stmt.where(SecurityEvent.project_id == project_id)
    return list(db.scalars(stmt))


def list_security_events_for_project(db: Session, project_id: uuid.UUID) -> list[SecurityEvent]:
    return list_security_events(db, project_id)


def get_security_event(db: Session, event_id: uuid.UUID) -> SecurityEvent | None:
    return db.get(SecurityEvent, event_id)