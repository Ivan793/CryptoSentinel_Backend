import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict

from app.models.scan import ScanStatus


class ScanRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    project_id: uuid.UUID
    started_at: datetime | None
    finished_at: datetime | None
    status: ScanStatus
    files_scanned: int
    findings_count: int