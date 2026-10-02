import uuid

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.schemas.rule import RuleCreate, RuleRead
from app.services import rule_service

router = APIRouter(prefix="/rules", tags=["Rules"])


@router.post("", response_model=RuleRead, status_code=status.HTTP_201_CREATED)
def create_rule(data: RuleCreate, db: Session = Depends(get_db)):
    try:
        return rule_service.create_rule(db, data)
    except rule_service.DuplicateRuleCodeError:
        raise HTTPException(
            status_code=409,
            detail=f"Ya existe una regla con el código '{data.code}'",
        )


@router.get("", response_model=list[RuleRead])
def list_rules(enabled_only: bool = Query(default=False), db: Session = Depends(get_db)):
    return rule_service.list_rules(db, enabled_only=enabled_only)


@router.get("/{rule_id}", response_model=RuleRead)
def get_rule(rule_id: uuid.UUID, db: Session = Depends(get_db)):
    rule = rule_service.get_rule(db, rule_id)
    if rule is None:
        raise HTTPException(status_code=404, detail="Regla no encontrada")
    return rule