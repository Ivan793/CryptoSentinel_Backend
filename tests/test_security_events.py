import uuid


def _create_project(client):
    return client.post("/api/projects", json={"name": "DemoBank"}).json()


def _create_scan(client, project_id):
    return client.post(f"/api/projects/{project_id}/scans").json()


def test_create_security_event_without_scan(client):
    project = _create_project(client)
    response = client.post(
        f"/api/projects/{project['id']}/security-events",
        json={"event_type": "PROJECT_CREATED", "description": "Proyecto registrado."},
    )
    assert response.status_code == 201
    body = response.json()
    assert body["project_id"] == project["id"]
    assert body["scan_id"] is None
    uuid.UUID(body["id"])


def test_create_security_event_with_scan(client):
    project = _create_project(client)
    scan = _create_scan(client, project["id"])
    response = client.post(
        f"/api/projects/{project['id']}/security-events",
        json={
            "event_type": "SCAN_COMPLETED",
            "description": "Security scan completed successfully.",
            "scan_id": scan["id"],
        },
    )
    assert response.status_code == 201
    assert response.json()["scan_id"] == scan["id"]


def test_create_security_event_project_not_found(client):
    response = client.post(
        f"/api/projects/{uuid.uuid4()}/security-events",
        json={"event_type": "PROJECT_CREATED"},
    )
    assert response.status_code == 404


def test_create_security_event_scan_not_found(client):
    project = _create_project(client)
    response = client.post(
        f"/api/projects/{project['id']}/security-events",
        json={"event_type": "SCAN_COMPLETED", "scan_id": str(uuid.uuid4())},
    )
    assert response.status_code == 404


def test_list_security_events_ordered_desc(client):
    project = _create_project(client)
    client.post(
        f"/api/projects/{project['id']}/security-events", json={"event_type": "EVENT_A"}
    )
    client.post(
        f"/api/projects/{project['id']}/security-events", json={"event_type": "EVENT_B"}
    )
    response = client.get(f"/api/projects/{project['id']}/security-events")
    assert response.status_code == 200
    events = response.json()
    assert len(events) == 2
    assert events[0]["event_type"] == "EVENT_B"  # el más reciente primero


def test_get_security_event_not_found(client):
    assert client.get(f"/api/security-events/{uuid.uuid4()}").status_code == 404