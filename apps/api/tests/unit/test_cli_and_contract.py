import json
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from app.cli import describe_schema, main
from app.config import Settings
from app.core.redis import InMemoryStore
from app.main import create_app
from app.services.health_service import HealthService

REPO_ROOT = Path(__file__).parents[4]


def test_committed_openapi_schema_matches_the_running_app() -> None:
    """Catches a stale packages/shared/openapi.json (and so stale generated TypeScript types).
    If this fails after a dependency or endpoint change, run `npm run gen:api` and commit."""
    committed = json.loads((REPO_ROOT / "packages/shared/openapi.json").read_text())
    assert committed == create_app().openapi()


def test_export_openapi_command_writes_valid_json(tmp_path: Path) -> None:
    target = tmp_path / "nested" / "openapi.json"
    assert main(["export-openapi", str(target)]) == 0
    schema = json.loads(target.read_text())
    assert "/api/v1/me" in schema["paths"]


def test_describe_schema_documents_every_table() -> None:
    from app.db.base import Base

    text = describe_schema()
    for name in Base.metadata.tables:
        assert f"### `{name}`" in text


def test_committed_database_docs_list_every_table() -> None:
    from app.db.base import Base

    docs = (REPO_ROOT / "docs/database.md").read_text()
    missing = [name for name in Base.metadata.tables if f"### `{name}`" not in docs]
    assert missing == [], "docs/database.md is stale: run `python -m app.cli describe-schema`"


def test_api_docs_are_disabled_in_production() -> None:
    settings = Settings(
        _env_file=None,
        environment="production",
        database_url="postgresql://u:p@h/d",
        redis_url="redis://x",
        firebase_project_id="p",
        firebase_service_account_b64="e30=",
        cors_allowed_origins="https://app.example.com",
    )
    client = TestClient(create_app(settings))
    assert [client.get(p).status_code for p in ("/docs", "/redoc", "/openapi.json")] == [404] * 3
    assert client.get("/api/v1/health").status_code == 200


def test_lifespan_events_do_not_break_the_middleware(app_no_db) -> None:  # type: ignore[no-untyped-def]
    with TestClient(app_no_db) as client:  # enters and exits the ASGI lifespan scope
        assert client.get("/api/v1/health").json() == {"status": "ok"}


def test_cors_origins_accept_a_json_list() -> None:
    settings = Settings(
        _env_file=None,
        database_url="postgresql://u:p@h/d",
        redis_url="redis://x",
        cors_allowed_origins='["https://a.example", "https://b.example"]',
    )
    assert settings.cors_allowed_origins == ["https://a.example", "https://b.example"]


def test_readiness_reports_a_failing_database_without_details() -> None:
    class BrokenSession:
        def execute(self, *args: object, **kwargs: object) -> None:
            raise ConnectionError("postgresql://user:hunter2@host exploded")

    checks = HealthService(BrokenSession(), InMemoryStore()).check()  # type: ignore[arg-type]
    assert checks == {"database": "failing", "redis": "ok"}


@pytest.mark.db
def test_seed_topics_command_populates_the_database(engine, capsys) -> None:  # type: ignore[no-untyped-def]
    from sqlalchemy import text

    try:
        assert main(["seed-topics"]) == 0
        assert "Seeded 17" in capsys.readouterr().out
        with engine.connect() as conn:
            assert conn.execute(text("SELECT count(*) FROM topics")).scalar_one() == 17
    finally:
        with engine.begin() as conn:
            conn.execute(text("DELETE FROM topics"))


@pytest.mark.db
def test_get_db_yields_a_working_session_and_closes_it(engine) -> None:  # type: ignore[no-untyped-def]
    from sqlalchemy import text

    from app.db.session import get_db

    generator = get_db()
    session = next(generator)
    assert session.execute(text("SELECT 1")).scalar_one() == 1
    generator.close()
    assert session.in_transaction() is False
