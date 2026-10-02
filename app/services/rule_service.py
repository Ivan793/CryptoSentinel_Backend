import uuid

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.models.rule import Rule
from app.schemas.rule import RuleCreate


class DuplicateRuleCodeError(Exception):
    """Se intentó crear una regla con un 'code' que ya existe."""


def create_rule(db: Session, data: RuleCreate) -> Rule:
    rule = Rule(**data.model_dump())
    db.add(rule)
    try:
        db.commit()
    except IntegrityError as exc:
        db.rollback()
        raise DuplicateRuleCodeError(data.code) from exc
    db.refresh(rule)
    return rule


def list_rules(db: Session, enabled_only: bool = False) -> list[Rule]:
    stmt = select(Rule).order_by(Rule.code)
    if enabled_only:
        stmt = stmt.where(Rule.enabled.is_(True))
    return list(db.scalars(stmt))


def get_rule(db: Session, rule_id: uuid.UUID) -> Rule | None:
    return db.get(Rule, rule_id)