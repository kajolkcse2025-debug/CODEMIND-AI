import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.api.v1.deps import get_health_service
from app.core.redis import InMemoryStore
from app.services.health_service import HealthService

pytestmark = pytest.mark.db


def test_ready_reports_ok_when_dependencies_are_up(client: TestClient) -> None:
    response = client.get("/api/v1/health/ready")
    assert response.status_code == 200
    assert response.json() == {"status": "ok", "checks": {"database": "ok", "redis": "ok"}}


class BrokenStore(InMemoryStore):
    def ping(self) -> bool:
        raise ConnectionError("redis://user:secret@host exploded")


def test_ready_returns_503_without_leaking_details(app_no_db: FastAPI, db_session) -> None:  # type: ignore[no-untyped-def]
    app_no_db.dependency_overrides[get_health_service] = lambda: HealthService(
        db_session, BrokenStore()
    )
    response = TestClient(app_no_db).get("/api/v1/health/ready")
    assert response.status_code == 503
    assert response.json() == {
        "status": "unavailable",
        "checks": {"database": "ok", "redis": "failing"},
    }
    assert "secret" not in response.text
