import uuid

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.enums import EventType, FindingStatus, SeverityLevel
from app.models.finding import Finding
from app.models.rule import Rule
from app.models.scan import Scan
from app.schemas.finding import FindingCreate
from app.services.event_recorder import record_event


class ScanNotFoundError(Exception):
    """El scan_id indicado no existe."""


class RuleNotFoundError(Exception):
    """El rule_id indicado no existe."""


def create_finding(db: Session, scan_id: uuid.UUID, data: FindingCreate) -> Finding:
    if db.get(Scan, scan_id) is None:
        raise ScanNotFoundError(scan_id)
    rule = db.get(Rule, data.rule_id)
    if rule is None:
        raise RuleNotFoundError(data.rule_id)

    # La severidad pertenece a la regla (sección 9): se copia, no se recibe.
    finding = Finding(scan_id=scan_id, severity=rule.severity, **data.model_dump())
    db.add(finding)
    db.commit()
    db.refresh(finding)
    return finding

def list_findings_for_scan(
    db: Session,
    scan_id: uuid.UUID,
    severity: SeverityLevel | None = None,
    status: FindingStatus | None = None,
) -> list[Finding]:
    stmt = select(Finding).where(Finding.scan_id == scan_id)
    if severity is not None:
        stmt = stmt.where(Finding.severity == severity)
    if status is not None:
        stmt = stmt.where(Finding.status == status)
    return list(db.scalars(stmt.order_by(Finding.created_at)))


def get_finding(db: Session, finding_id: uuid.UUID) -> Finding | None:
    return db.get(Finding, finding_id)


def update_finding_status(
    db: Session, finding_id: uuid.UUID, new_status: FindingStatus
) -> Finding | None:
    finding = db.get(Finding, finding_id)
    if finding is None:
        return None
    if finding.status != new_status:  # un cambio "a lo mismo" no genera evento
        finding.status = new_status
        record_event(
            db,
            EventType.FINDING_REVIEWED,
            f"Hallazgo {finding.rule.code} marcado como {new_status.value}.",
            project_id=finding.scan.project_id,
            scan_id=finding.scan_id,
        )
        db.commit()
        db.refresh(finding)
    return finding

def list_findings(
    db: Session,
    project_id: uuid.UUID | None = None,
    scan_id: uuid.UUID | None = None,
    severity: SeverityLevel | None = None,
    status: FindingStatus | None = None,
) -> list[Finding]:
    stmt = select(Finding)
    if project_id is not None:
        stmt = stmt.join(Scan, Finding.scan_id == Scan.id).where(Scan.project_id == project_id)
    if scan_id is not None:
        stmt = stmt.where(Finding.scan_id == scan_id)
    if severity is not None:
        stmt = stmt.where(Finding.severity == severity)
    if status is not None:
        stmt = stmt.where(Finding.status == status)
    return list(db.scalars(stmt.order_by(Finding.created_at.desc())))