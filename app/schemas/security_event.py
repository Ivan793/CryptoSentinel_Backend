import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict


class SecurityEventRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    event_type: str
    description: str | None
    project_id: uuid.UUID
    scan_id: uuid.UUID | None
    created_at: datetime