import uuid


def _create_project(client):
    return client.post("/projects", json={"name": "DemoBank"}).json()


def _create_scan(client, project_id):
    return client.post(f"/projects/{project_id}/scans").json()


def _report_payload(**overrides):
    data = {"format": "PDF", "file_path": "/reports/demo-bank-scan-001.pdf"}
    data.update(overrides)
    return data


def test_create_report(client):
    project = _create_project(client)
    scan = _create_scan(client, project["id"])
    response = client.post(f"/scans/{scan['id']}/reports", json=_report_payload())
    assert response.status_code == 201
    body = response.json()
    assert body["scan_id"] == scan["id"]
    assert body["project_id"] == project["id"]
    assert body["format"] == "PDF"
    uuid.UUID(body["id"])


def test_create_report_scan_not_found(client):
    response = client.post(f"/scans/{uuid.uuid4()}/reports", json=_report_payload())
    assert response.status_code == 404


def test_create_report_rejects_invalid_format(client):
    project = _create_project(client)
    scan = _create_scan(client, project["id"])
    response = client.post(
        f"/scans/{scan['id']}/reports", json=_report_payload(format="DOCX")
    )
    assert response.status_code == 422


def test_list_reports_for_scan(client):
    project = _create_project(client)
    scan = _create_scan(client, project["id"])
    client.post(f"/scans/{scan['id']}/reports", json=_report_payload(format="HTML"))
    client.post(f"/scans/{scan['id']}/reports", json=_report_payload(format="PDF"))
    response = client.get(f"/scans/{scan['id']}/reports")
    assert response.status_code == 200
    assert len(response.json()) == 2


def test_list_reports_for_project_across_scans(client):
    project = _create_project(client)
    scan_a = _create_scan(client, project["id"])
    scan_b = _create_scan(client, project["id"])
    client.post(f"/scans/{scan_a['id']}/reports", json=_report_payload())
    client.post(f"/scans/{scan_b['id']}/reports", json=_report_payload())
    response = client.get(f"/projects/{project['id']}/reports")
    assert response.status_code == 200
    assert len(response.json()) == 2


def test_get_report_not_found(client):
    assert client.get(f"/reports/{uuid.uuid4()}").status_code == 404