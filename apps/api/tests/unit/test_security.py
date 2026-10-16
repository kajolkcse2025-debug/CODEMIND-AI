"""Token verification: real SDK code path (emulator mode) plus mapped failure modes."""

import base64
import contextlib
import json
import time
from collections.abc import Iterator
from typing import Any

import firebase_admin
import pytest
from firebase_admin import auth

from app.config import Settings
from app.core.errors import ServiceUnavailableError
from app.core.security import FirebaseTokenVerifier, TokenVerificationError

PROJECT = "demo-codemind"


def _segment(data: dict[str, Any]) -> str:
    return base64.urlsafe_b64encode(json.dumps(data).encode()).rstrip(b"=").decode()


def make_token(**overrides: Any) -> str:
    now = int(time.time())
    claims: dict[str, Any] = {
        "iss": f"https://securetoken.google.com/{PROJECT}",
        "aud": PROJECT,
        "sub": "uid-123",
        "auth_time": now - 10,
        "iat": now - 10,
        "exp": now + 3600,
        "email": "student@example.com",
        "email_verified": True,
        "name": "Asha",
        "firebase": {"identities": {}, "sign_in_provider": "password"},
    }
    claims.update(overrides)
    return f"{_segment({'alg': 'none', 'typ': 'JWT'})}.{_segment(claims)}."


@pytest.fixture
def verifier(monkeypatch: pytest.MonkeyPatch) -> Iterator[FirebaseTokenVerifier]:
    monkeypatch.setenv("FIREBASE_AUTH_EMULATOR_HOST", "localhost:9099")
    settings = Settings(
        _env_file=None,
        database_url="postgresql://u:p@h/d",
        redis_url="redis://x",
        firebase_project_id=PROJECT,
    )
    yield FirebaseTokenVerifier(settings)
    with contextlib.suppress(ValueError):
        firebase_admin.delete_app(firebase_admin.get_app())


def test_valid_emulator_token_is_verified(verifier: FirebaseTokenVerifier) -> None:
    result = verifier.verify(make_token())
    assert (result.uid, result.email, result.email_verified, result.name) == (
        "uid-123",
        "student@example.com",
        True,
        "Asha",
    )


def test_unverified_email_flag_is_preserved(verifier: FirebaseTokenVerifier) -> None:
    assert verifier.verify(make_token(email_verified=False)).email_verified is False


@pytest.mark.parametrize(
    "token",
    [make_token(aud="some-other-project"), "garbage", "a.b.c", make_token(sub="")],
)
def test_bad_tokens_are_rejected(verifier: FirebaseTokenVerifier, token: str) -> None:
    with pytest.raises(TokenVerificationError) as info:
        verifier.verify(token)
    assert info.value.reason == "token_invalid"


@pytest.mark.parametrize(
    ("error", "reason"),
    [
        (auth.ExpiredIdTokenError("expired", cause=None), "token_expired"),
        (auth.RevokedIdTokenError("revoked"), "token_revoked"),
        (auth.InvalidIdTokenError("invalid"), "token_invalid"),
    ],
)
def test_sdk_errors_map_to_reasons(
    verifier: FirebaseTokenVerifier,
    monkeypatch: pytest.MonkeyPatch,
    error: Exception,
    reason: str,
) -> None:
    def fail(*args: Any, **kwargs: Any) -> None:
        raise error

    monkeypatch.setattr(auth, "verify_id_token", fail)
    with pytest.raises(TokenVerificationError) as info:
        verifier.verify("anything")
    assert info.value.reason == reason


def test_certificate_fetch_failure_is_a_503_not_a_401(
    verifier: FirebaseTokenVerifier, monkeypatch: pytest.MonkeyPatch
) -> None:
    def fail(*args: Any, **kwargs: Any) -> None:
        raise auth.CertificateFetchError("network down", cause=None)

    monkeypatch.setattr(auth, "verify_id_token", fail)
    with pytest.raises(ServiceUnavailableError) as info:
        verifier.verify("anything")
    assert info.value.code == "auth_unavailable"


def test_unconfigured_server_fails_with_auth_not_configured(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.delenv("FIREBASE_AUTH_EMULATOR_HOST", raising=False)
    settings = Settings(_env_file=None, database_url="postgresql://u:p@h/d", redis_url="redis://x")
    with pytest.raises(ServiceUnavailableError) as info:
        FirebaseTokenVerifier(settings).verify("anything")
    assert info.value.code == "auth_not_configured"


# ---- production credential path and concurrency (regression tests) ----------------------


def _service_account_b64(project_id: str = "proj-prod") -> str:
    from cryptography.hazmat.primitives import serialization
    from cryptography.hazmat.primitives.asymmetric import rsa

    key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
    pem = key.private_bytes(
        serialization.Encoding.PEM,
        serialization.PrivateFormat.PKCS8,
        serialization.NoEncryption(),
    ).decode()
    info = {
        "type": "service_account",
        "project_id": project_id,
        "private_key_id": "key-id",
        "private_key": pem,
        "client_email": f"sa@{project_id}.iam.gserviceaccount.com",
        "client_id": "1",
        "token_uri": "https://oauth2.googleapis.com/token",
    }
    return base64.b64encode(json.dumps(info).encode()).decode()


def _prod_like_settings(b64: str) -> Settings:
    return Settings(
        _env_file=None,
        database_url="postgresql://u:p@h/d",
        redis_url="redis://x",
        firebase_project_id="proj-prod",
        firebase_service_account_b64=b64,
    )


@pytest.fixture
def no_firebase_app(monkeypatch: pytest.MonkeyPatch) -> Iterator[None]:
    monkeypatch.delenv("FIREBASE_AUTH_EMULATOR_HOST", raising=False)
    with contextlib.suppress(ValueError):
        firebase_admin.delete_app(firebase_admin.get_app())
    yield
    with contextlib.suppress(ValueError):
        firebase_admin.delete_app(firebase_admin.get_app())


def test_real_service_account_credentials_initialise_the_app(no_firebase_app: None) -> None:
    from app.core.security import _ensure_firebase_app

    app = _ensure_firebase_app(_prod_like_settings(_service_account_b64()))
    assert app.project_id == "proj-prod"


@pytest.mark.parametrize(
    "bad_b64",
    [
        "!!!not-base64!!!",
        base64.b64encode(b"this is not json").decode(),
        base64.b64encode(b'{"type": "service_account"}').decode(),  # valid JSON, unusable key
    ],
)
def test_bad_service_account_credentials_fail_cleanly(no_firebase_app: None, bad_b64: str) -> None:
    from app.core.security import _ensure_firebase_app

    with pytest.raises(ServiceUnavailableError) as info:
        _ensure_firebase_app(_prod_like_settings(bad_b64))
    assert info.value.code == "auth_not_configured"


def test_credentials_error_message_never_contains_the_secret(no_firebase_app: None) -> None:
    from app.core.security import _ensure_firebase_app

    secret_b64 = base64.b64encode(b'{"private_key": "TOP-SECRET-KEY-MATERIAL"}').decode()
    with pytest.raises(ServiceUnavailableError) as info:
        _ensure_firebase_app(_prod_like_settings(secret_b64))
    assert "TOP-SECRET" not in str(info.value) and "TOP-SECRET" not in info.value.message


def test_init_tolerates_the_app_being_created_by_someone_else_mid_call(
    no_firebase_app: None, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Deterministic reproduction of the check-then-act race: ``get_app`` says 'none yet', then
    ``initialize_app`` reports that another thread just created it. Must not raise."""
    from app.core import security

    sentinel = object()
    calls = iter([ValueError("no app"), sentinel])

    def fake_get_app(*args: Any, **kwargs: Any) -> object:
        item = next(calls)
        if isinstance(item, Exception):
            raise item
        return item

    def fake_initialize(*args: Any, **kwargs: Any) -> None:
        raise ValueError("The default Firebase app already exists.")

    # Scope the patches: the fixture's teardown must see the real firebase_admin functions.
    with monkeypatch.context() as patched:
        patched.setattr(firebase_admin, "get_app", fake_get_app)
        patched.setattr(firebase_admin, "initialize_app", fake_initialize)
        patched.setenv("FIREBASE_AUTH_EMULATOR_HOST", "localhost:9099")
        settings = Settings(
            _env_file=None,
            database_url="postgresql://u:p@h/d",
            redis_url="redis://x",
            firebase_project_id="demo-codemind",
        )
        assert security._ensure_firebase_app(settings) is sentinel


def test_many_threads_initialising_at_once_all_succeed(
    no_firebase_app: None, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Probabilistic companion to the test above (the unfixed code failed ~0.15% of calls)."""
    import sys
    import threading

    from app.core.security import _ensure_firebase_app

    monkeypatch.setenv("FIREBASE_AUTH_EMULATOR_HOST", "localhost:9099")
    settings = Settings(
        _env_file=None,
        database_url="postgresql://u:p@h/d",
        redis_url="redis://x",
        firebase_project_id="demo-codemind",
    )
    errors: list[Exception] = []
    previous = sys.getswitchinterval()
    sys.setswitchinterval(1e-6)
    try:
        for _ in range(15):
            with contextlib.suppress(ValueError):
                firebase_admin.delete_app(firebase_admin.get_app())
            barrier = threading.Barrier(32)

            def worker(barrier: threading.Barrier = barrier) -> None:
                barrier.wait()
                try:
                    _ensure_firebase_app(settings)
                except Exception as exc:
                    errors.append(exc)

            threads = [threading.Thread(target=worker) for _ in range(32)]
            for thread in threads:
                thread.start()
            for thread in threads:
                thread.join()
    finally:
        sys.setswitchinterval(previous)
    assert errors == []
