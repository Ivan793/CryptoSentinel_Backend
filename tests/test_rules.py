import uuid


def _sample_rule(**overrides):
    data = {
        "code": "CRYPTO-001",
        "name": "Potential Hardcoded Secret",
        "category": "Secrets Management",
        "severity": "HIGH",
        "recommendation": "No almacenar secretos en el código.",
        "reference": "OWASP Secrets Management Cheat Sheet",
    }
    data.update(overrides)
    return data


def test_create_rule(client):
    response = client.post("/api/rules", json=_sample_rule())
    assert response.status_code == 201
    body = response.json()
    assert body["code"] == "CRYPTO-001"
    assert body["enabled"] is True
    uuid.UUID(body["id"])


def test_create_rule_rejects_duplicate_code(client):
    client.post("/api/rules", json=_sample_rule())
    response = client.post("/api/rules", json=_sample_rule(name="Otro nombre"))
    assert response.status_code == 409


def test_create_rule_rejects_invalid_severity(client):
    response = client.post("/api/rules", json=_sample_rule(severity="CRITICA"))
    assert response.status_code == 422


def test_list_rules_filters_enabled(client):
    client.post("/api/rules", json=_sample_rule(code="CRYPTO-001"))
    client.post("/api/rules", json=_sample_rule(code="CRYPTO-002", enabled=False))

    all_rules = client.get("/api/rules").json()
    assert len(all_rules) == 2

    enabled_rules = client.get("/api/rules", params={"enabled_only": True}).json()
    assert len(enabled_rules) == 1
    assert enabled_rules[0]["code"] == "CRYPTO-001"


def test_get_rule_not_found(client):
    assert client.get(f"/api/rules/{uuid.uuid4()}").status_code == 404