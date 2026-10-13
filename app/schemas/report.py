import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict

from app.models.enums import ReportFormat


class ReportCreate(BaseModel):
    format: ReportFormat


class ReportRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    project_id: uuid.UUID
    scan_id: uuid.UUID
    generated_at: datetime
    format: ReportFormat
    file_path: str