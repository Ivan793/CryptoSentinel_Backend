import uuid

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.project import Project
from app.models.scan import Scan
from app.models.security_event import SecurityEvent
from app.schemas.security_event import SecurityEventCreate


class ProjectNotFoundError(Exception):
    """El project_id indicado no existe."""


class ScanNotFoundError(Exception):
    """El scan_id indicado no existe."""


def create_security_event(
    db: Session, project_id: uuid.UUID, data: SecurityEventCreate
) -> SecurityEvent:
    if db.get(Project, project_id) is None:
        raise ProjectNotFoundError(project_id)
    if data.scan_id is not None and db.get(Scan, data.scan_id) is None:
        raise ScanNotFoundError(data.scan_id)

    event = SecurityEvent(project_id=project_id, **data.model_dump())
    db.add(event)
    db.commit()
    db.refresh(event)
    return event


def list_security_events_for_project(db: Session, project_id: uuid.UUID) -> list[SecurityEvent]:
    stmt = (
        select(SecurityEvent)
        .where(SecurityEvent.project_id == project_id)
        .order_by(SecurityEvent.created_at.desc())
    )
    return list(db.scalars(stmt))


def get_security_event(db: Session, event_id: uuid.UUID) -> SecurityEvent | None:
    return db.get(SecurityEvent, event_id)