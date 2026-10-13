import uuid


def test_create_project(client):
    response = client.post("/api/projects", json={"name": "Mi app", "description": "Demo"})
    assert response.status_code == 201
    body = response.json()
    assert body["name"] == "Mi app"
    assert body["status"] == "ACTIVE"
    uuid.UUID(body["id"])  # valida que sea un UUID bien formado


def test_list_projects(client):
    client.post("/api/projects", json={"name": "A"})
    client.post("/api/projects", json={"name": "B"})
    response = client.get("/api/projects")
    assert response.status_code == 200
    assert len(response.json()) == 2


def test_get_project_not_found(client):
    random_id = uuid.uuid4()
    assert client.get(f"/api/projects/{random_id}").status_code == 404


def test_get_project_invalid_id_returns_422(client):
    assert client.get("/api/projects/no-es-un-uuid").status_code == 422


def test_create_project_rejects_empty_name(client):
    response = client.post("/api/projects", json={"name": "   "})
    assert response.status_code == 422

def test_update_project_status(client):
    created = client.post("/api/projects", json={"name": "A"}).json()

    archived = client.patch(f"/api/projects/{created['id']}", json={"status": "ARCHIVED"})
    assert archived.status_code == 200
    assert archived.json()["status"] == "ARCHIVED"

    restored = client.patch(f"/api/projects/{created['id']}", json={"status": "ACTIVE"})
    assert restored.json()["status"] == "ACTIVE"


def test_update_project_status_rejects_invalid_value(client):
    created = client.post("/api/projects", json={"name": "A"}).json()
    response = client.patch(f"/api/projects/{created['id']}", json={"status": "BORRADO"})
    assert response.status_code == 422


def test_update_project_status_not_found(client):
    response = client.patch(f"/api/projects/{uuid.uuid4()}", json={"status": "ARCHIVED"})
    assert response.status_code == 404


def test_project_includes_scan_stats(client):
    project = client.post("/api/projects", json={"name": "A"}).json()
    assert project["scans_count"] == 0
    assert project["last_scan_at"] is None

    client.post(f"/api/projects/{project['id']}/scans")
    client.post(f"/api/projects/{project['id']}/scans")

    detail = client.get(f"/api/projects/{project['id']}").json()
    assert detail["scans_count"] == 2
    assert detail["last_scan_at"] is not None

    listed = client.get("/api/projects").json()
    assert listed[0]["scans_count"] == 2


def test_delete_project_cascades_to_related_data(client):
    pid = client.post("/api/projects", json={"name": "DemoBank"}).json()["id"]
    scan = client.post(f"/api/projects/{pid}/scans").json()
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
    key = client.post(
        f"/api/projects/{pid}/crypto-keys",
        json={"key_identifier": "KEY-001", "algorithm": "AES", "key_size": 256},
    ).json()
    event = client.post(
        f"/api/projects/{pid}/security-events",
        json={"event_type": "SCAN_COMPLETED", "scan_id": scan["id"]},
    ).json()
    report = client.post(f"/api/scans/{scan['id']}/reports", json={"format": "HTML"}).json()

    assert client.delete(f"/api/projects/{pid}").status_code == 204

    assert client.get(f"/api/projects/{pid}").status_code == 404
    assert client.get(f"/api/scans/{scan['id']}").status_code == 404
    assert client.get(f"/api/findings/{finding['id']}").status_code == 404
    assert client.get(f"/api/crypto-keys/{key['id']}").status_code == 404
    assert client.get(f"/api/security-events/{event['id']}").status_code == 404
    assert client.get(f"/api/reports/{report['id']}").status_code == 404
    # La regla es independiente del proyecto: debe seguir existiendo.
    assert client.get(f"/api/rules/{rule['id']}").status_code == 200


def test_delete_project_not_found(client):
    assert client.delete(f"/api/projects/{uuid.uuid4()}").status_code == 404