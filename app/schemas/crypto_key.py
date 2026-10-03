import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from app.models.enums import CryptoKeyStatus


class CryptoKeyCreate(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)

    key_identifier: str = Field(min_length=1, max_length=100)
    algorithm: str = Field(min_length=1, max_length=50)
    key_size: int | None = Field(default=None, gt=0)
    purpose: str | None = Field(default=None, max_length=100)
    expires_at: datetime | None = None


class CryptoKeyRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    project_id: uuid.UUID
    key_identifier: str
    algorithm: str
    key_size: int | None
    purpose: str | None
    status: CryptoKeyStatus
    created_at: datetime
    expires_at: datetime | None