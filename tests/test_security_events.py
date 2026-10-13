import uuid


def _create_project(client):
    return client.post("/api/projects", json={"name": "DemoBank"}).json()


def _create_scan(client, project_id):
    return client.post(f"/api/projects/{project_id}/scans").json()


def _events(client, project_id):
    return client.get("/api/security-events", params={"project_id": project_id}).json()


def _setup_finding(client):
    project = _create_project(client)
    scan = _create_scan(client, project["id"])
    rule = client.post(
        "/api/rules",
        json={
            "code": "CRYPTO-001",
            "name": "Potential Hardcoded Secret",
            "category": "Secrets Management",
            "severity": "HIGH",
        },
    ).json()
    finding = client.post(
        f"/api/scans/{scan['id']}/findings",
        json={"rule_id": rule["id"], "file_path": "config.py", "line_number": 15},
    ).json()
    return project, scan, finding


def test_security_events_cannot_be_created_via_api(client):
    project = _create_project(client)
    body = {"event_type": "SCAN_COMPLETED", "description": "Evento falso."}

    response = client.post(f"/api/projects/{project['id']}/security-events", json=body)
    assert response.status_code == 405
    assert client.post("/api/security-events", json=body).status_code == 405
    assert _events(client, project["id"]) == []


def test_list_security_events_ordered_desc(client):
    project = _create_project(client)
    scan = _create_scan(client, project["id"])
    client.post(f"/api/scans/{scan['id']}/reports", json={"format": "HTML"})

    events = _events(client, project["id"])
    assert [e["event_type"] for e in events] == ["REPORT_GENERATED", "SCAN_STARTED"]


def test_get_security_event(client):
    project = _create_project(client)
    _create_scan(client, project["id"])
    event = _events(client, project["id"])[0]

    response = client.get(f"/api/security-events/{event['id']}")
    assert response.status_code == 200
    assert response.json()["id"] == event["id"]


def test_get_security_event_not_found(client):
    assert client.get(f"/api/security-events/{uuid.uuid4()}").status_code == 404


def test_creating_scan_records_scan_started(client):
    project = _create_project(client)
    scan = _create_scan(client, project["id"])

    events = _events(client, project["id"])
    assert len(events) == 1
    assert events[0]["event_type"] == "SCAN_STARTED"
    assert events[0]["scan_id"] == scan["id"]


def test_changing_finding_status_records_finding_reviewed(client):
    project, scan, finding = _setup_finding(client)
    client.patch(f"/api/findings/{finding['id']}", json={"status": "REVIEWED"})

    reviewed = [
        e for e in _events(client, project["id"]) if e["event_type"] == "FINDING_REVIEWED"
    ]
    assert len(reviewed) == 1
    assert reviewed[0]["scan_id"] == scan["id"]
    assert "CRYPTO-001" in reviewed[0]["description"]
    assert "REVIEWED" in reviewed[0]["description"]


def test_same_finding_status_records_nothing(client):
    project, _, finding = _setup_finding(client)
    client.patch(f"/api/findings/{finding['id']}", json={"status": "OPEN"})  # ya estaba OPEN

    types = [e["event_type"] for e in _events(client, project["id"])]
    assert "FINDING_REVIEWED" not in types


def test_generating_report_records_report_generated(client):
    project = _create_project(client)
    scan = _create_scan(client, project["id"])
    client.post(f"/api/scans/{scan['id']}/reports", json={"format": "PDF"})

    generated = [
        e for e in _events(client, project["id"]) if e["event_type"] == "REPORT_GENERATED"
    ]
    assert len(generated) == 1
    assert "PDF" in generated[0]["description"]