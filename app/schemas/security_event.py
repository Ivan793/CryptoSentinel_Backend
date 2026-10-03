import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class SecurityEventCreate(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)

    event_type: str = Field(min_length=1, max_length=100)
    description: str | None = Field(default=None, max_length=2000)
    scan_id: uuid.UUID | None = None


class SecurityEventRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    event_type: str
    description: str | None
    project_id: uuid.UUID
    scan_id: uuid.UUID | None
    created_at: datetime