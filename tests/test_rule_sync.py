from sqlalchemy import select

from app.models.rule import Rule
from app.scanner.catalog import CATALOG
from app.services.rule_sync import sync_rules


def _spec(code):
    return next(spec for spec in CATALOG if spec.code == code)


def _rule(db, code):
    return db.scalars(select(Rule).where(Rule.code == code)).one()


def test_sync_creates_all_catalog_rules(db_session):
    result = sync_rules(db_session)
    assert result == {"created": len(CATALOG), "updated": 0}

    rules = {rule.code: rule for rule in db_session.scalars(select(Rule))}
    assert set(rules) == {spec.code for spec in CATALOG}
    assert rules["CRYPTO-001"].enabled is True
    assert rules["CRYPTO-007"].enabled is False  # nace desactivada, igual que en el front


def test_sync_is_idempotent(db_session):
    sync_rules(db_session)
    result = sync_rules(db_session)
    assert result == {"created": 0, "updated": 0}
    assert len(list(db_session.scalars(select(Rule)))) == len(CATALOG)


def test_sync_preserves_enabled_flag(db_session):
    sync_rules(db_session)
    rule = _rule(db_session, "CRYPTO-001")
    rule.enabled = False
    db_session.commit()

    sync_rules(db_session)
    db_session.refresh(rule)
    assert rule.enabled is False


def test_sync_restores_catalog_text_but_keeps_enabled(db_session):
    sync_rules(db_session)
    rule = _rule(db_session, "CRYPTO-001")
    rule.recommendation = "texto alterado a mano"
    rule.enabled = False
    db_session.commit()

    result = sync_rules(db_session)
    assert result == {"created": 0, "updated": 1}
    db_session.refresh(rule)
    assert rule.recommendation == _spec("CRYPTO-001").recommendation
    assert rule.enabled is False


def test_synced_rules_are_served_by_api(client, db_session):
    sync_rules(db_session)

    rules = client.get("/api/rules").json()
    assert len(rules) == len(CATALOG)

    enabled = client.get("/api/rules", params={"enabled_only": True}).json()
    assert len(enabled) == len(CATALOG) - 1  # CRYPTO-007 está desactivada