import uuid


def _create_project(client):
    return client.post("/projects", json={"name": "DemoBank"}).json()


def _create_scan(client, project_id):
    return client.post(f"/projects/{project_id}/scans").json()


def _create_rule(client, code="CRYPTO-001"):
    return client.post(
        "/rules",
        json={
            "code": code,
            "name": "Potential Hardcoded Secret",
            "category": "Secrets Management",
            "severity": "HIGH",
        },
    ).json()


def _setup(client):
    project = _create_project(client)
    scan = _create_scan(client, project["id"])
    rule = _create_rule(client)
    return project, scan, rule


def _finding_payload(rule_id, **overrides):
    data = {
        "rule_id": rule_id,
        "file_path": "config.py",
        "line_number": 15,
        "evidence": "password = 'ab****ef'",
        "description": "Se detectó un posible secreto embebido en el código.",
        "severity": "HIGH",
    }
    data.update(overrides)
    return data


def test_create_finding(client):
    _, scan, rule = _setup(client)
    response = client.post(
        f"/scans/{scan['id']}/findings", json=_finding_payload(rule["id"])
    )
    assert response.status_code == 201
    body = response.json()
    assert body["scan_id"] == scan["id"]
    assert body["rule_id"] == rule["id"]
    assert body["status"] == "OPEN"
    uuid.UUID(body["id"])


def test_create_finding_scan_not_found(client):
    _, _, rule = _setup(client)
    response = client.post(
        f"/scans/{uuid.uuid4()}/findings", json=_finding_payload(rule["id"])
    )
    assert response.status_code == 404


def test_create_finding_rule_not_found(client):
    _, scan, _ = _setup(client)
    response = client.post(
        f"/scans/{scan['id']}/findings", json=_finding_payload(str(uuid.uuid4()))
    )
    assert response.status_code == 404


def test_list_findings_filters_by_status(client):
    _, scan, rule = _setup(client)
    f1 = client.post(
        f"/scans/{scan['id']}/findings", json=_finding_payload(rule["id"])
    ).json()
    client.post(f"/scans/{scan['id']}/findings", json=_finding_payload(rule["id"]))

    client.patch(f"/findings/{f1['id']}", json={"status": "FALSE_POSITIVE"})

    open_only = client.get(
        f"/scans/{scan['id']}/findings", params={"status": "OPEN"}
    ).json()
    assert len(open_only) == 1

    all_findings = client.get(f"/scans/{scan['id']}/findings").json()
    assert len(all_findings) == 2


def test_update_finding_status_not_found(client):
    response = client.patch(f"/findings/{uuid.uuid4()}", json={"status": "RESOLVED"})
    assert response.status_code == 404


def test_update_finding_status_invalid_value(client):
    _, scan, rule = _setup(client)
    created = client.post(
        f"/scans/{scan['id']}/findings", json=_finding_payload(rule["id"])
    ).json()
    response = client.patch(f"/findings/{created['id']}", json={"status": "CERRADO"})
    assert response.status_code == 422