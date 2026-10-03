import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.schemas.security_event import SecurityEventCreate, SecurityEventRead
from app.services import security_event_service

router = APIRouter(tags=["Security Events"])


@router.post(
    "/projects/{project_id}/security-events",
    response_model=SecurityEventRead,
    status_code=status.HTTP_201_CREATED,
)
def create_security_event(
    project_id: uuid.UUID, data: SecurityEventCreate, db: Session = Depends(get_db)
):
    try:
        return security_event_service.create_security_event(db, project_id, data)
    except security_event_service.ProjectNotFoundError:
        raise HTTPException(status_code=404, detail="Proyecto no encontrado")
    except security_event_service.ScanNotFoundError:
        raise HTTPException(status_code=404, detail="Análisis no encontrado")


@router.get("/projects/{project_id}/security-events", response_model=list[SecurityEventRead])
def list_security_events(project_id: uuid.UUID, db: Session = Depends(get_db)):
    return security_event_service.list_security_events_for_project(db, project_id)


@router.get("/security-events/{event_id}", response_model=SecurityEventRead)
def get_security_event(event_id: uuid.UUID, db: Session = Depends(get_db)):
    event = security_event_service.get_security_event(db, event_id)
    if event is None:
        raise HTTPException(status_code=404, detail="Evento no encontrado")
    return event