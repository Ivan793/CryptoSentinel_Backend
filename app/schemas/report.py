import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from app.models.enums import ReportFormat


class ReportCreate(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)

    format: ReportFormat
    file_path: str = Field(min_length=1, max_length=1000)


class ReportRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    project_id: uuid.UUID
    scan_id: uuid.UUID
    generated_at: datetime
    format: ReportFormat
    file_path: str