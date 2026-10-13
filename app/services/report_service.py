import uuid

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.report import Report
from app.models.scan import Scan
from app.schemas.report import ReportCreate
from app.models.enums import EventType
from app.services.event_recorder import record_event


class ScanNotFoundError(Exception):
    """El scan_id indicado no existe."""


def create_report(db: Session, scan_id: uuid.UUID, data: ReportCreate) -> Report:
    scan = db.get(Scan, scan_id)
    if scan is None:
        raise ScanNotFoundError(scan_id)

    report_id = uuid.uuid4()
    report = Report(
        id=report_id,
        project_id=scan.project_id,
        scan_id=scan_id,
        format=data.format,
        file_path=f"reports/{report_id}.{data.format.value.lower()}",
    )
    db.add(report)
    record_event(
        db,
        EventType.REPORT_GENERATED,
        f"Reporte {data.format.value} generado.",
        project_id=scan.project_id,
        scan_id=scan_id,
    )
    db.commit()
    db.refresh(report)
    return report


def list_reports_for_scan(db: Session, scan_id: uuid.UUID) -> list[Report]:
    stmt = select(Report).where(Report.scan_id == scan_id)
    return list(db.scalars(stmt))


def list_reports_for_project(db: Session, project_id: uuid.UUID) -> list[Report]:
    stmt = (
        select(Report)
        .where(Report.project_id == project_id)
        .order_by(Report.generated_at.desc())
    )
    return list(db.scalars(stmt))


def get_report(db: Session, report_id: uuid.UUID) -> Report | None:
    return db.get(Report, report_id)

def list_reports(db: Session, project_id: uuid.UUID | None = None) -> list[Report]:
    stmt = select(Report).order_by(Report.generated_at.desc())
    if project_id is not None:
        stmt = stmt.where(Report.project_id == project_id)
    return list(db.scalars(stmt))