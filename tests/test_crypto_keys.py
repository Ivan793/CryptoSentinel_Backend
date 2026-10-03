import uuid


def _create_project(client):
    return client.post("/projects", json={"name": "DemoBank"}).json()


def _key_payload(**overrides):
    data = {
        "key_identifier": "KEY-001",
        "algorithm": "AES",
        "key_size": 256,
        "purpose": "DATA_ENCRYPTION",
    }
    data.update(overrides)
    return data


def test_create_crypto_key(client):
    project = _create_project(client)
    response = client.post(
        f"/projects/{project['id']}/crypto-keys", json=_key_payload()
    )
    assert response.status_code == 201
    body = response.json()
    assert body["project_id"] == project["id"]
    assert body["status"] == "ACTIVE"
    uuid.UUID(body["id"])


def test_create_crypto_key_project_not_found(client):
    response = client.post(
        f"/projects/{uuid.uuid4()}/crypto-keys", json=_key_payload()
    )
    assert response.status_code == 404


def test_list_crypto_keys_for_project(client):
    project = _create_project(client)
    client.post(f"/projects/{project['id']}/crypto-keys", json=_key_payload())
    client.post(
        f"/projects/{project['id']}/crypto-keys",
        json=_key_payload(key_identifier="KEY-002"),
    )
    response = client.get(f"/projects/{project['id']}/crypto-keys")
    assert response.status_code == 200
    assert len(response.json()) == 2


def test_update_crypto_key_status(client):
    project = _create_project(client)
    created = client.post(
        f"/projects/{project['id']}/crypto-keys", json=_key_payload()
    ).json()
    response = client.patch(
        f"/crypto-keys/{created['id']}", json={"status": "REVOKED"}
    )
    assert response.status_code == 200
    assert response.json()["status"] == "REVOKED"


def test_get_crypto_key_not_found(client):
    assert client.get(f"/crypto-keys/{uuid.uuid4()}").status_code == 404