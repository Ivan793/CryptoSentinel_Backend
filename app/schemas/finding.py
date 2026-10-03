import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from app.models.enums import FindingStatus, SeverityLevel


class FindingCreate(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)

    rule_id: uuid.UUID
    file_path: str = Field(min_length=1, max_length=1000)
    line_number: int = Field(ge=1)
    evidence: str | None = Field(default=None, max_length=2000)
    description: str | None = Field(default=None, max_length=2000)
    severity: SeverityLevel


class FindingStatusUpdate(BaseModel):
    status: FindingStatus


class FindingRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    scan_id: uuid.UUID
    rule_id: uuid.UUID
    file_path: str
    line_number: int
    evidence: str | None
    description: str | None
    severity: SeverityLevel
    status: FindingStatus
    created_at: datetime