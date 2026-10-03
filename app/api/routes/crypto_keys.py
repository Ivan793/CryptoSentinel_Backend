import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.enums import CryptoKeyStatus
from app.schemas.crypto_key import CryptoKeyCreate, CryptoKeyRead
from app.services import crypto_key_service

router = APIRouter(tags=["Crypto Keys"])


class CryptoKeyStatusUpdate(BaseModel):
    status: CryptoKeyStatus


@router.post(
    "/projects/{project_id}/crypto-keys",
    response_model=CryptoKeyRead,
    status_code=status.HTTP_201_CREATED,
)
def create_crypto_key(
    project_id: uuid.UUID, data: CryptoKeyCreate, db: Session = Depends(get_db)
):
    try:
        return crypto_key_service.create_crypto_key(db, project_id, data)
    except crypto_key_service.ProjectNotFoundError:
        raise HTTPException(status_code=404, detail="Proyecto no encontrado")


@router.get("/projects/{project_id}/crypto-keys", response_model=list[CryptoKeyRead])
def list_crypto_keys(project_id: uuid.UUID, db: Session = Depends(get_db)):
    return crypto_key_service.list_crypto_keys_for_project(db, project_id)


@router.get("/crypto-keys/{crypto_key_id}", response_model=CryptoKeyRead)
def get_crypto_key(crypto_key_id: uuid.UUID, db: Session = Depends(get_db)):
    crypto_key = crypto_key_service.get_crypto_key(db, crypto_key_id)
    if crypto_key is None:
        raise HTTPException(status_code=404, detail="Clave no encontrada")
    return crypto_key


@router.patch("/crypto-keys/{crypto_key_id}", response_model=CryptoKeyRead)
def update_crypto_key_status(
    crypto_key_id: uuid.UUID, data: CryptoKeyStatusUpdate, db: Session = Depends(get_db)
):
    crypto_key = crypto_key_service.update_crypto_key_status(db, crypto_key_id, data.status)
    if crypto_key is None:
        raise HTTPException(status_code=404, detail="Clave no encontrada")
    return crypto_key