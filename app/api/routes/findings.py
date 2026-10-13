import uuid

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.enums import FindingStatus, SeverityLevel
from app.schemas.finding import FindingCreate, FindingRead, FindingStatusUpdate
from app.services import finding_service

router = APIRouter(tags=["Findings"])


@router.post(
    "/scans/{scan_id}/findings",
    response_model=FindingRead,
    status_code=status.HTTP_201_CREATED,
)
def create_finding(scan_id: uuid.UUID, data: FindingCreate, db: Session = Depends(get_db)):
    try:
        return finding_service.create_finding(db, scan_id, data)
    except finding_service.ScanNotFoundError:
        raise HTTPException(status_code=404, detail="Análisis no encontrado")
    except finding_service.RuleNotFoundError:
        raise HTTPException(status_code=404, detail="Regla no encontrada")


@router.get("/scans/{scan_id}/findings", response_model=list[FindingRead])
def list_findings(
    scan_id: uuid.UUID,
    severity: SeverityLevel | None = Query(default=None),
    status_filter: FindingStatus | None = Query(default=None, alias="status"),
    db: Session = Depends(get_db),
):
    return finding_service.list_findings_for_scan(
        db, scan_id, severity=severity, status=status_filter
    )


@router.get("/findings/{finding_id}", response_model=FindingRead)
def get_finding(finding_id: uuid.UUID, db: Session = Depends(get_db)):
    finding = finding_service.get_finding(db, finding_id)
    if finding is None:
        raise HTTPException(status_code=404, detail="Hallazgo no encontrado")
    return finding


@router.patch("/findings/{finding_id}", response_model=FindingRead)
def update_finding_status(
    finding_id: uuid.UUID, data: FindingStatusUpdate, db: Session = Depends(get_db)
):
    finding = finding_service.update_finding_status(db, finding_id, data.status)
    if finding is None:
        raise HTTPException(status_code=404, detail="Hallazgo no encontrado")
    return finding

@router.get("/findings", response_model=list[FindingRead])
def list_all_findings(
    project_id: uuid.UUID | None = Query(default=None),
    scan_id: uuid.UUID | None = Query(default=None),
    severity: SeverityLevel | None = Query(default=None),
    status_filter: FindingStatus | None = Query(default=None, alias="status"),
    db: Session = Depends(get_db),
):
    return finding_service.list_findings(
        db,
        project_id=project_id,
        scan_id=scan_id,
        severity=severity,
        status=status_filter,
    )