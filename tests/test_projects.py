import uuid


def test_create_project(client):
    response = client.post("/projects", json={"name": "Mi app", "description": "Demo"})
    assert response.status_code == 201
    body = response.json()
    assert body["name"] == "Mi app"
    assert body["status"] == "ACTIVE"
    uuid.UUID(body["id"])  # valida que sea un UUID bien formado


def test_list_projects(client):
    client.post("/projects", json={"name": "A"})
    client.post("/projects", json={"name": "B"})
    response = client.get("/projects")
    assert response.status_code == 200
    assert len(response.json()) == 2


def test_get_project_not_found(client):
    random_id = uuid.uuid4()
    assert client.get(f"/projects/{random_id}").status_code == 404


def test_get_project_invalid_id_returns_422(client):
    assert client.get("/projects/no-es-un-uuid").status_code == 422


def test_create_project_rejects_empty_name(client):
    response = client.post("/projects", json={"name": "   "})
    assert response.status_code == 422