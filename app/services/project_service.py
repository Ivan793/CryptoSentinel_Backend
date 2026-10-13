import uuid

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models.project import Project, ProjectStatus
from app.models.scan import Scan
from app.schemas.project import ProjectCreate


def _attach_stats(db: Session, projects: list[Project]) -> list[Project]:
    """Agrega scans_count y last_scan_at (sección 2) con una sola consulta agrupada."""
    if not projects:
        return projects
    rows = db.execute(
        select(Scan.project_id, func.count(Scan.id), func.max(Scan.started_at))
        .where(Scan.project_id.in_([p.id for p in projects]))
        .group_by(Scan.project_id)
    ).all()
    stats = {project_id: (count, last) for project_id, count, last in rows}
    for project in projects:
        project.scans_count, project.last_scan_at = stats.get(project.id, (0, None))
    return projects


def create_project(db: Session, data: ProjectCreate) -> Project:
    project = Project(name=data.name, description=data.description)
    db.add(project)
    db.commit()
    db.refresh(project)
    return project


def list_projects(db: Session) -> list[Project]:
    projects = list(db.scalars(select(Project).order_by(Project.created_at.desc())))
    return _attach_stats(db, projects)


def get_project(db: Session, project_id: uuid.UUID) -> Project | None:
    project = db.get(Project, project_id)
    if project is None:
        return None
    _attach_stats(db, [project])
    return project


def update_project_status(
    db: Session, project_id: uuid.UUID, new_status: ProjectStatus
) -> Project | None:
    project = db.get(Project, project_id)
    if project is None:
        return None
    project.status = new_status
    db.commit()
    db.refresh(project)
    _attach_stats(db, [project])
    return project


def delete_project(db: Session, project_id: uuid.UUID) -> bool:
    project = db.get(Project, project_id)
    if project is None:
        return False
    db.delete(project)  # la cascada elimina scans, hallazgos, claves, eventos y reportes
    db.commit()
    return True