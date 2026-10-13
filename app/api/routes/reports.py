import uuid

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.schemas.report import ReportCreate, ReportRead
from app.services import report_service

router = APIRouter(tags=["Reports"])


@router.post(
    "/scans/{scan_id}/reports",
    response_model=ReportRead,
    status_code=status.HTTP_201_CREATED,
)
def create_report(scan_id: uuid.UUID, data: ReportCreate, db: Session = Depends(get_db)):
    try:
        return report_service.create_report(db, scan_id, data)
    except report_service.ScanNotFoundError:
        raise HTTPException(status_code=404, detail="Análisis no encontrado")


@router.get("/scans/{scan_id}/reports", response_model=list[ReportRead])
def list_reports_for_scan(scan_id: uuid.UUID, db: Session = Depends(get_db)):
    return report_service.list_reports_for_scan(db, scan_id)


@router.get("/projects/{project_id}/reports", response_model=list[ReportRead])
def list_reports_for_project(project_id: uuid.UUID, db: Session = Depends(get_db)):
    return report_service.list_reports_for_project(db, project_id)


@router.get("/reports/{report_id}", response_model=ReportRead)
def get_report(report_id: uuid.UUID, db: Session = Depends(get_db)):
    report = report_service.get_report(db, report_id)
    if report is None:
        raise HTTPException(status_code=404, detail="Reporte no encontrado")
    return report

@router.get("/reports", response_model=list[ReportRead])
def list_all_reports(
    project_id: uuid.UUID | None = Query(default=None), db: Session = Depends(get_db)
):
    return report_service.list_reports(db, project_id)