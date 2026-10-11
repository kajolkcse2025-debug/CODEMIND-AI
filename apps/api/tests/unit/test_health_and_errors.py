import re

from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.main import create_app


def test_health_returns_ok(client_no_db: TestClient) -> None:
    response = client_no_db.get("/api/v1/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_unknown_route_uses_error_envelope(client_no_db: TestClient) -> None:
    response = client_no_db.get("/api/v1/does-not-exist")
    body = response.json()
    assert response.status_code == 404
    assert set(body) == {"error"}
    assert set(body["error"]) == {"code", "message", "details", "request_id"}
    assert body["error"]["code"] == "not_found"
    assert body["error"]["details"] == {}


def test_wrong_method_uses_error_envelope(client_no_db: TestClient) -> None:
    response = client_no_db.post("/api/v1/health")
    assert response.status_code == 405
    assert response.json()["error"]["code"] == "method_not_allowed"


def test_request_id_is_generated_and_matches_error_body(client_no_db: TestClient) -> None:
    response = client_no_db.get("/api/v1/nope")
    header = response.headers["x-request-id"]
    assert re.fullmatch(r"[0-9a-f]{32}", header)
    assert response.json()["error"]["request_id"] == header


def test_valid_incoming_request_id_is_echoed(client_no_db: TestClient) -> None:
    response = client_no_db.get("/api/v1/health", headers={"X-Request-ID": "trace-abc-12345"})
    assert response.headers["x-request-id"] == "trace-abc-12345"


def test_malicious_request_id_is_replaced(client_no_db: TestClient) -> None:
    response = client_no_db.get("/api/v1/health", headers={"X-Request-ID": "bad id\twith spaces"})
    assert response.headers["x-request-id"] != "bad id\twith spaces"
    assert re.fullmatch(r"[0-9a-f]{32}", response.headers["x-request-id"])


def test_unexpected_exception_returns_generic_envelope_without_leaking(app_no_db: FastAPI) -> None:
    def boom() -> None:
        raise RuntimeError("secret internal detail: password=hunter2")

    app_no_db.add_api_route("/boom", boom)
    client = TestClient(app_no_db, raise_server_exceptions=False)
    response = client.get("/boom")
    assert response.status_code == 500
    error = response.json()["error"]
    assert error["code"] == "internal_error"
    assert "hunter2" not in response.text
    assert error["request_id"] == response.headers["x-request-id"]


def test_cors_allows_only_configured_origin() -> None:
    client = TestClient(create_app())
    allowed = client.options(
        "/api/v1/health",
        headers={"Origin": "http://localhost:5173", "Access-Control-Request-Method": "GET"},
    )
    denied = client.options(
        "/api/v1/health",
        headers={"Origin": "https://evil.example", "Access-Control-Request-Method": "GET"},
    )
    assert allowed.headers.get("access-control-allow-origin") == "http://localhost:5173"
    assert "access-control-allow-origin" not in denied.headers
