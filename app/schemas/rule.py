import uuid

from pydantic import BaseModel, ConfigDict, Field

from app.models.enums import SeverityLevel


class RuleCreate(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)

    code: str = Field(min_length=1, max_length=50)
    name: str = Field(min_length=1, max_length=150)
    category: str = Field(min_length=1, max_length=100)
    description: str | None = Field(default=None, max_length=2000)
    severity: SeverityLevel
    recommendation: str | None = Field(default=None, max_length=2000)
    reference: str | None = Field(default=None, max_length=1000)
    enabled: bool = True


class RuleRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    code: str
    name: str
    category: str
    description: str | None
    severity: SeverityLevel
    recommendation: str | None
    reference: str | None
    enabled: bool


class RuleEnabledUpdate(BaseModel):
    enabled: bool