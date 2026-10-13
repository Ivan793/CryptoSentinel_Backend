import uuid

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.project import Project
from app.models.scan import Scan

from datetime import datetime, timezone

class ProjectNotFoundError(Exception):
    """El project_id indicado no existe."""


def project_exists(db: Session, project_id: uuid.UUID) -> bool:
    return db.get(Project, project_id) is not None

def create_scan(db: Session, project_id: uuid.UUID) -> Scan:
    if not project_exists(db, project_id):
        raise ProjectNotFoundError(project_id)

    scan = Scan(project_id=project_id, started_at=datetime.now(timezone.utc))
    db.add(scan)
    db.commit()
    db.refresh(scan)
    return scan


def list_scans_for_project(db: Session, project_id: uuid.UUID) -> list[Scan]:
    stmt = select(Scan).where(Scan.project_id == project_id)
    return list(db.scalars(stmt))


def get_scan(db: Session, scan_id: uuid.UUID) -> Scan | None:
    return db.get(Scan, scan_id)