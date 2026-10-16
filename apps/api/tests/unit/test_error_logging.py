import json
import logging

from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.logging import JsonFormatter


def test_unhandled_exception_log_line_carries_the_request_id(app_no_db: FastAPI) -> None:
    """The id a student sees as 'Reference: <id>' must be searchable in the server log."""
    records: list[logging.LogRecord] = []

    class Capture(logging.Handler):
        def emit(self, record: logging.LogRecord) -> None:
            records.append(record)

    def boom() -> None:
        raise RuntimeError("kaboom")

    app_no_db.add_api_route("/boom", boom)
    logger = logging.getLogger("app.errors")
    handler = Capture()
    logger.addHandler(handler)
    try:
        response = TestClient(app_no_db, raise_server_exceptions=False).get("/boom")
    finally:
        logger.removeHandler(handler)

    request_id = response.headers["x-request-id"]
    assert response.json()["error"]["request_id"] == request_id
    unhandled = [r for r in records if r.getMessage() == "unhandled_exception"]
    assert len(unhandled) == 1
    logged = json.loads(JsonFormatter().format(unhandled[0]))
    assert logged["request_id"] == request_id


def test_request_log_line_has_metadata_only(app_no_db: FastAPI, caplog) -> None:  # type: ignore[no-untyped-def]
    logger = logging.getLogger("app.request")
    records: list[logging.LogRecord] = []

    class Capture(logging.Handler):
        def emit(self, record: logging.LogRecord) -> None:
            records.append(record)

    handler = Capture()
    logger.addHandler(handler)
    try:
        TestClient(app_no_db).get(
            "/api/v1/me", headers={"Authorization": "Bearer super-secret-token-value"}
        )
    finally:
        logger.removeHandler(handler)
    text = " ".join(JsonFormatter().format(r) for r in records)
    assert "super-secret-token-value" not in text
    assert "Authorization" not in text
    parsed = json.loads(JsonFormatter().format(records[-1]))
    assert set(parsed) >= {"method", "path", "status", "duration_ms", "request_id"}
