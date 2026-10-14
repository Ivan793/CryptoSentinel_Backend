from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.rule import Rule
from app.scanner.catalog import CATALOG

# Campos que controla el catálogo. `enabled` NO está aquí a propósito:
# es una decisión del usuario y la sincronización nunca la pisa.
_SYNCED_FIELDS = (
    "name",
    "category",
    "severity",
    "description",
    "recommendation",
    "reference",
)


def sync_rules(db: Session) -> dict[str, int]:
    """Refleja el catálogo del código en la tabla rules. Es idempotente."""
    existing = {rule.code: rule for rule in db.scalars(select(Rule))}
    created = updated = 0

    for spec in CATALOG:
        rule = existing.get(spec.code)
        if rule is None:
            db.add(
                Rule(
                    code=spec.code,
                    name=spec.name,
                    category=spec.category,
                    severity=spec.severity,
                    description=spec.description,
                    recommendation=spec.recommendation,
                    reference=spec.reference,
                    enabled=spec.enabled_by_default,
                )
            )
            created += 1
            continue

        changed = False
        for field in _SYNCED_FIELDS:
            new_value = getattr(spec, field)
            if getattr(rule, field) != new_value:
                setattr(rule, field, new_value)
                changed = True
        if changed:
            updated += 1

    db.commit()
    return {"created": created, "updated": updated}