ORIGIN = "http://localhost:5173"


def _preflight(client, origin):
    return client.options(
        "/api/projects",
        headers={"Origin": origin, "Access-Control-Request-Method": "POST"},
    )


def test_cors_allows_frontend_origin(client):
    response = _preflight(client, ORIGIN)
    assert response.status_code == 200
    assert response.headers["access-control-allow-origin"] == ORIGIN


def test_cors_rejects_unknown_origin(client):
    response = _preflight(client, "http://evil.example")
    assert "access-control-allow-origin" not in response.headers