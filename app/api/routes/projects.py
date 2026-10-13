import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.schemas.project import ProjectCreate, ProjectRead, ProjectStatusUpdate
from app.services import project_service

router = APIRouter(prefix="/projects", tags=["Projects"])


@router.post("", response_model=ProjectRead, status_code=status.HTTP_201_CREATED)
def create_project(data: ProjectCreate, db: Session = Depends(get_db)):
    return project_service.create_project(db, data)


@router.get("", response_model=list[ProjectRead])
def list_projects(db: Session = Depends(get_db)):
    return project_service.list_projects(db)


@router.get("/{project_id}", response_model=ProjectRead)
def get_project(project_id: uuid.UUID, db: Session = Depends(get_db)):
    project = project_service.get_project(db, project_id)
    if project is None:
        raise HTTPException(status_code=404, detail="Proyecto no encontrado")
    return project


@router.patch("/{project_id}", response_model=ProjectRead)
def update_project_status(
    project_id: uuid.UUID, data: ProjectStatusUpdate, db: Session = Depends(get_db)
):
    project = project_service.update_project_status(db, project_id, data.status)
    if project is None:
        raise HTTPException(status_code=404, detail="Proyecto no encontrado")
    return project


@router.delete("/{project_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_project(project_id: uuid.UUID, db: Session = Depends(get_db)):
    if not project_service.delete_project(db, project_id):
        raise HTTPException(status_code=404, detail="Proyecto no encontrado")