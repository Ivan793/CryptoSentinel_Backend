import enum


class SeverityLevel(str, enum.Enum):
    HIGH = "HIGH"
    MEDIUM = "MEDIUM"
    LOW = "LOW"
    INFO = "INFO"


class FindingStatus(str, enum.Enum):
    OPEN = "OPEN"
    REVIEWED = "REVIEWED"
    FALSE_POSITIVE = "FALSE_POSITIVE"
    RESOLVED = "RESOLVED"

class CryptoKeyStatus(str, enum.Enum):
    ACTIVE = "ACTIVE"
    EXPIRED = "EXPIRED"
    REVOKED = "REVOKED"

class ReportFormat(str, enum.Enum):
    HTML = "HTML"
    PDF = "PDF"

class EventType(str, enum.Enum):
    """Tipos de evento de la sección 14. Se guardan como texto, sin enum en la base de datos."""

    SCAN_STARTED = "SCAN_STARTED"
    SCAN_COMPLETED = "SCAN_COMPLETED"
    SCAN_FAILED = "SCAN_FAILED"
    FINDING_CREATED = "FINDING_CREATED"
    FINDING_REVIEWED = "FINDING_REVIEWED"
    REPORT_GENERATED = "REPORT_GENERATED"