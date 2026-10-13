import uuid


def _create_project(client, name="DemoBank"):
    return client.post("/api/projects", json={"name": name}).json()


def test_create_scan(client):
    project = _create_project(client)
    response = client.post(f"/api/projects/{project['id']}/scans")
    assert response.status_code == 201
    body = response.json()
    assert body["project_id"] == project["id"]
    assert body["status"] == "PENDING"
    assert body["files_scanned"] == 0
    assert body["findings_count"] == 0
    uuid.UUID(body["id"])


def test_create_scan_project_not_found(client):
    response = client.post(f"/api/projects/{uuid.uuid4()}/scans")
    assert response.status_code == 404


def test_list_scans_for_project(client):
    project = _create_project(client)
    client.post(f"/api/projects/{project['id']}/scans")
    client.post(f"/api/projects/{project['id']}/scans")
    response = client.get(f"/api/projects/{project['id']}/scans")
    assert response.status_code == 200
    assert len(response.json()) == 2


def test_list_scans_project_not_found(client):
    response = client.get(f"/api/projects/{uuid.uuid4()}/scans")
    assert response.status_code == 404


def test_get_scan(client):
    project = _create_project(client)
    created = client.post(f"/api/projects/{project['id']}/scans").json()
    response = client.get(f"/api/scans/{created['id']}")
    assert response.status_code == 200
    assert response.json()["id"] == created["id"]


def test_get_scan_not_found(client):
    assert client.get(f"/api/scans/{uuid.uuid4()}").status_code == 404