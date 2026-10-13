import pytest

# Elementos que crea _seed_two_projects por cada proyecto.
# Eventos: 2, generados solos (SCAN_STARTED al crear el scan y REPORT_GENERATED al crear el reporte).
PER_PROJECT = {
    "scans": 1,
    "crypto-keys": 1,
    "security-events": 2,
    "reports": 1,
    "findings": 1,
}
PATHS = list(PER_PROJECT)


def _seed_two_projects(client):
    """Dos proyectos; cada uno con un scan, una clave, un reporte y un hallazgo."""
    rule = client.post(
        "/api/rules",
        json={
            "code": "CRYPTO-001",
            "name": "Potential Hardcoded Secret",
            "category": "Secrets Management",
            "severity": "HIGH",
        },
    ).json()
    projects = []
    for index, name in enumerate(("DemoBank", "Inventario API"), start=1):
        project = client.post("/api/projects", json={"name": name}).json()
        scan = client.post(f"/api/projects/{project['id']}/scans").json()
        client.post(
            f"/api/projects/{project['id']}/crypto-keys",
            json={"key_identifier": f"KEY-{index}", "algorithm": "AES", "key_size": 256},
        )
        client.post(f"/api/scans/{scan['id']}/reports", json={"format": "HTML"})
        client.post(
            f"/api/scans/{scan['id']}/findings",
            json={"rule_id": rule["id"], "file_path": "config.py", "line_number": 1},
        )
        projects.append(project)
    return projects


@pytest.mark.parametrize("path", PATHS)
def test_global_listing_and_project_filter(client, path):
    first, _ = _seed_two_projects(client)
    per_project = PER_PROJECT[path]

    everything = client.get(f"/api/{path}")
    assert everything.status_code == 200
    assert len(everything.json()) == per_project * 2

    filtered = client.get(f"/api/{path}", params={"project_id": first["id"]})
    assert filtered.status_code == 200
    assert len(filtered.json()) == per_project


@pytest.mark.parametrize("path", PATHS)
def test_listing_with_unknown_project_is_empty(client, path):
    _seed_two_projects(client)
    response = client.get(
        f"/api/{path}", params={"project_id": "00000000-0000-4000-8000-000000000000"}
    )
    assert response.status_code == 200
    assert response.json() == []


@pytest.mark.parametrize("path", PATHS)
def test_listing_rejects_invalid_project_id(client, path):
    response = client.get(f"/api/{path}", params={"project_id": "no-es-un-uuid"})
    assert response.status_code == 422


def test_global_findings_filters_by_severity_and_status(client):
    _seed_two_projects(client)

    assert len(client.get("/api/findings", params={"severity": "HIGH"}).json()) == 2
    assert client.get("/api/findings", params={"severity": "LOW"}).json() == []
    assert len(client.get("/api/findings", params={"status": "OPEN"}).json()) == 2
    assert client.get("/api/findings", params={"status": "RESOLVED"}).json() == []