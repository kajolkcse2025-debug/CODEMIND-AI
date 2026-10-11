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
