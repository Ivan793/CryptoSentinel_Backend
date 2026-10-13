import uuid

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.schemas.security_event import SecurityEventRead
from app.services import security_event_service

router = APIRouter(tags=["Security Events"])


@router.get("/projects/{project_id}/security-events", response_model=list[SecurityEventRead])
def list_security_events(project_id: uuid.UUID, db: Session = Depends(get_db)):
    return security_event_service.list_security_events_for_project(db, project_id)


@router.get("/security-events", response_model=list[SecurityEventRead])
def list_all_security_events(
    project_id: uuid.UUID | None = Query(default=None), db: Session = Depends(get_db)
):
    return security_event_service.list_security_events(db, project_id)


@router.get("/security-events/{event_id}", response_model=SecurityEventRead)
def get_security_event(event_id: uuid.UUID, db: Session = Depends(get_db)):
    event = security_event_service.get_security_event(db, event_id)
    if event is None:
        raise HTTPException(status_code=404, detail="Evento no encontrado")
    return event