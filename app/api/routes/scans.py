import uuid

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.schemas.scan import ScanRead
from app.services import scan_service

router = APIRouter(tags=["Scans"])


@router.post(
    "/projects/{project_id}/scans",
    response_model=ScanRead,
    status_code=status.HTTP_201_CREATED,
)
def create_scan(project_id: uuid.UUID, db: Session = Depends(get_db)):
    try:
        return scan_service.create_scan(db, project_id)
    except scan_service.ProjectNotFoundError:
        raise HTTPException(status_code=404, detail="Proyecto no encontrado")


@router.get("/projects/{project_id}/scans", response_model=list[ScanRead])
def list_scans(project_id: uuid.UUID, db: Session = Depends(get_db)):
    if not scan_service.project_exists(db, project_id):
        raise HTTPException(status_code=404, detail="Proyecto no encontrado")
    return scan_service.list_scans_for_project(db, project_id)


@router.get("/scans/{scan_id}", response_model=ScanRead)
def get_scan(scan_id: uuid.UUID, db: Session = Depends(get_db)):
    scan = scan_service.get_scan(db, scan_id)
    if scan is None:
        raise HTTPException(status_code=404, detail="Análisis no encontrado")
    return scan

@router.get("/scans", response_model=list[ScanRead])
def list_all_scans(
    project_id: uuid.UUID | None = Query(default=None), db: Session = Depends(get_db)
):
    return scan_service.list_scans(db, project_id)