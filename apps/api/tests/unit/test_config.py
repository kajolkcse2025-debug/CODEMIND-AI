import pytest
from pydantic import ValidationError

from app.config import Settings

BASE = {"database_url": "postgresql://u:p@h/db", "redis_url": "redis://localhost:6379/0"}


def make(**overrides: object) -> Settings:
    return Settings(_env_file=None, **{**BASE, **overrides})  # type: ignore[arg-type]


def test_database_url_is_normalised_for_psycopg() -> None:
    assert make().database_url == "postgresql+psycopg://u:p@h/db"
    assert make(database_url="postgres://u:p@h/db").database_url == "postgresql+psycopg://u:p@h/db"


def test_database_url_has_no_default(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("DATABASE_URL", raising=False)
    with pytest.raises(ValidationError):
        Settings(_env_file=None, redis_url="redis://x")  # type: ignore[call-arg]


def test_cors_origins_parse_comma_separated() -> None:
    settings = make(cors_allowed_origins="https://a.example, https://b.example")
    assert settings.cors_allowed_origins == ["https://a.example", "https://b.example"]


def test_cors_wildcard_is_rejected() -> None:
    with pytest.raises(ValidationError):
        make(cors_allowed_origins="*")


def test_production_requires_firebase_credentials() -> None:
    with pytest.raises(ValidationError, match="FIREBASE_PROJECT_ID"):
        make(environment="production")


def test_production_rejects_fake_ai_provider() -> None:
    with pytest.raises(ValidationError, match="AI_PROVIDER=fake"):
        make(
            environment="production",
            firebase_project_id="p",
            firebase_service_account_b64="e30=",
            ai_provider="fake",
        )


def test_production_rejects_firebase_emulator(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("FIREBASE_AUTH_EMULATOR_HOST", "localhost:9099")
    with pytest.raises(ValidationError, match="emulator"):
        make(
            environment="production",
            firebase_project_id="p",
            firebase_service_account_b64="e30=",
        )


def test_secrets_are_not_printed() -> None:
    settings = make(gemini_api_key="super-secret-key")
    assert "super-secret-key" not in repr(settings)
    assert "super-secret-key" not in str(settings.model_dump())


def test_blank_optional_values_mean_unset() -> None:
    settings = make(
        firebase_project_id="",
        firebase_service_account_b64="  ",
        gemini_api_key="",
        ai_model_fast="",
    )
    assert settings.firebase_project_id is None
    assert settings.firebase_service_account_b64 is None
    assert settings.gemini_api_key is None
    assert settings.ai_model_fast is None


def test_shipped_env_example_loads_cleanly(monkeypatch: pytest.MonkeyPatch) -> None:
    from pathlib import Path

    # Real environment variables outrank the file, so clear the ones the test harness sets.
    for name in ("ENVIRONMENT", "DATABASE_URL", "REDIS_URL", "CORS_ALLOWED_ORIGINS"):
        monkeypatch.delenv(name, raising=False)
    example = Path(__file__).parents[4] / ".env.example"
    settings = Settings(_env_file=example)  # type: ignore[call-arg]
    assert settings.environment == "development"
    assert settings.cors_allowed_origins == ["http://localhost:5173"]
    assert settings.gemini_api_key is None
    assert settings.firebase_project_id is None
