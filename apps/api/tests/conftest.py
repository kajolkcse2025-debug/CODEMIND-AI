"""Shared fixtures.

Tests NEVER touch the development database: they use TEST_DATABASE_URL (default
``codemind_test``). The schema is built by running the real Alembic migrations.
"""

import os
from collections.abc import Iterator

# Environment must be set before ``app`` modules read settings.
TEST_DATABASE_URL = os.environ.get(
    "TEST_DATABASE_URL", "postgresql+psycopg://codemind:codemind@localhost:5432/codemind_test"
)
TEST_REDIS_URL = os.environ.get("TEST_REDIS_URL", "redis://localhost:6379/15")
os.environ["ENVIRONMENT"] = "test"
os.environ["DATABASE_URL"] = TEST_DATABASE_URL
os.environ["REDIS_URL"] = TEST_REDIS_URL
os.environ["CORS_ALLOWED_ORIGINS"] = "http://localhost:5173"
os.environ.pop("FIREBASE_AUTH_EMULATOR_HOST", None)

import pytest  # noqa: E402
from alembic.config import Config  # noqa: E402
from fastapi import FastAPI  # noqa: E402
from fastapi.testclient import TestClient  # noqa: E402
from sqlalchemy import Engine, create_engine, text  # noqa: E402
from sqlalchemy.orm import Session  # noqa: E402

from alembic import command  # noqa: E402
from app.config import get_settings  # noqa: E402
from app.core.redis import InMemoryStore, get_store  # noqa: E402
from app.core.security import (  # noqa: E402
    TokenVerificationError,
    VerifiedToken,
    get_token_verifier,
)
from app.db.session import get_db  # noqa: E402
from app.main import create_app  # noqa: E402


class FakeTokenVerifier:
    """Maps opaque test tokens to identities. Anything else is rejected."""

    def __init__(self) -> None:
        self.tokens: dict[str, VerifiedToken] = {}
        self.errors: dict[str, str] = {}

    def add(
        self,
        uid: str,
        email: str | None = None,
        *,
        email_verified: bool = True,
        name: str | None = None,
    ) -> dict[str, str]:
        token = f"token-{uid}"
        self.tokens[token] = VerifiedToken(uid, email, email_verified, name)
        return {"Authorization": f"Bearer {token}"}

    def verify(self, token: str) -> VerifiedToken:
        if token in self.errors:
            raise TokenVerificationError(self.errors[token])
        if token not in self.tokens:
            raise TokenVerificationError("token_invalid")
        return self.tokens[token]


@pytest.fixture(autouse=True)
def _clear_settings_cache() -> Iterator[None]:
    get_settings.cache_clear()
    yield
    get_settings.cache_clear()


@pytest.fixture(scope="session")
def engine() -> Iterator[Engine]:
    """A fresh database built by the real migrations (downgrade to base, then upgrade)."""
    engine = create_engine(TEST_DATABASE_URL)
    try:
        with engine.connect() as connection:
            connection.execute(text("SELECT 1"))
    except Exception as exc:  # pragma: no cover - environment problem, fail loudly
        pytest.fail(
            f"PostgreSQL is not reachable at TEST_DATABASE_URL ({exc.__class__.__name__}). "
            "Start it with `docker compose up -d postgres` or run `pytest -m 'not db'`.",
            pytrace=False,
        )
    config = Config(str(__import__("pathlib").Path(__file__).parents[1] / "alembic.ini"))
    config.set_main_option("sqlalchemy.url", TEST_DATABASE_URL)
    command.downgrade(config, "base")
    command.upgrade(config, "head")
    yield engine
    engine.dispose()


@pytest.fixture
def db_session(engine: Engine) -> Iterator[Session]:
    """A session wrapped in a transaction that is rolled back after each test."""
    connection = engine.connect()
    transaction = connection.begin()
    session = Session(
        bind=connection, join_transaction_mode="create_savepoint", expire_on_commit=False
    )
    try:
        yield session
    finally:
        session.close()
        transaction.rollback()
        connection.close()


@pytest.fixture
def verifier() -> FakeTokenVerifier:
    return FakeTokenVerifier()


@pytest.fixture
def app_no_db(verifier: FakeTokenVerifier) -> FastAPI:
    """App with auth and Redis faked and NO database override (for DB-free tests)."""
    app = create_app()
    app.dependency_overrides[get_token_verifier] = lambda: verifier
    app.dependency_overrides[get_store] = lambda: InMemoryStore()
    return app


@pytest.fixture
def client_no_db(app_no_db: FastAPI) -> TestClient:
    return TestClient(app_no_db, raise_server_exceptions=False)


@pytest.fixture
def client(app_no_db: FastAPI, db_session: Session) -> TestClient:
    app_no_db.dependency_overrides[get_db] = lambda: db_session
    return TestClient(app_no_db, raise_server_exceptions=False)
