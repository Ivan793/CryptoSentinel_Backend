import uuid

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.crypto_key import CryptoKey
from app.models.enums import CryptoKeyStatus
from app.models.project import Project
from app.schemas.crypto_key import CryptoKeyCreate


class ProjectNotFoundError(Exception):
    """El project_id indicado no existe."""


def create_crypto_key(db: Session, project_id: uuid.UUID, data: CryptoKeyCreate) -> CryptoKey:
    if db.get(Project, project_id) is None:
        raise ProjectNotFoundError(project_id)

    crypto_key = CryptoKey(project_id=project_id, **data.model_dump())
    db.add(crypto_key)
    db.commit()
    db.refresh(crypto_key)
    return crypto_key


def list_crypto_keys_for_project(db: Session, project_id: uuid.UUID) -> list[CryptoKey]:
    stmt = select(CryptoKey).where(CryptoKey.project_id == project_id)
    return list(db.scalars(stmt))


def get_crypto_key(db: Session, crypto_key_id: uuid.UUID) -> CryptoKey | None:
    return db.get(CryptoKey, crypto_key_id)


def update_crypto_key_status(
    db: Session, crypto_key_id: uuid.UUID, new_status: CryptoKeyStatus
) -> CryptoKey | None:
    crypto_key = db.get(CryptoKey, crypto_key_id)
    if crypto_key is None:
        return None
    crypto_key.status = new_status
    db.commit()
    db.refresh(crypto_key)
    return crypto_key