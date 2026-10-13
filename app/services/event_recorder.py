import uuid

from sqlalchemy.orm import Session

from app.models.enums import EventType
from app.models.security_event import SecurityEvent


def record_event(
    db: Session,
    event_type: EventType,
    description: str,
    project_id: uuid.UUID,
    scan_id: uuid.UUID | None = None,
) -> SecurityEvent:
    """Agrega un evento a la sesión SIN hacer commit.

    Así queda en la misma transacción que la operación que lo origina:
    o se guardan los dos, o no se guarda ninguno.
    """
    event = SecurityEvent(
        event_type=event_type.value,
        description=description,
        project_id=project_id,
        scan_id=scan_id,
    )
    db.add(event)
    return event