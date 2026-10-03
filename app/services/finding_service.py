import uuid

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.enums import FindingStatus, SeverityLevel
from app.models.finding import Finding
from app.models.rule import Rule
from app.models.scan import Scan
from app.schemas.finding import FindingCreate


class ScanNotFoundError(Exception):
    """El scan_id indicado no existe."""


class RuleNotFoundError(Exception):
    """El rule_id indicado no existe."""


def create_finding(db: Session, scan_id: uuid.UUID, data: FindingCreate) -> Finding:
    if db.get(Scan, scan_id) is None:
        raise ScanNotFoundError(scan_id)
    if db.get(Rule, data.rule_id) is None:
        raise RuleNotFoundError(data.rule_id)

    finding = Finding(scan_id=scan_id, **data.model_dump())
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
    finding.status = new_status
    db.commit()
    db.refresh(finding)
    return finding