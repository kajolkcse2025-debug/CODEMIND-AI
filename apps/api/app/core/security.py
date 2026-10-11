"""Firebase ID-token verification.

Identity comes ONLY from a token the Firebase Admin SDK has verified. No endpoint accepts a
user id from the client.
"""

import base64
import binascii
import json
import logging
from dataclasses import dataclass
from functools import lru_cache
from typing import Any, Protocol

import firebase_admin
from firebase_admin import auth, credentials

from app.config import Settings, get_settings
from app.core.errors import ServiceUnavailableError

logger = logging.getLogger("app.security")


@dataclass(frozen=True)
class VerifiedToken:
    uid: str
    email: str | None
    email_verified: bool
    name: str | None


class TokenVerificationError(Exception):
    """The token is missing, malformed, expired, revoked or otherwise not acceptable."""

    def __init__(self, reason: str) -> None:
        super().__init__(reason)
        self.reason = reason


class TokenVerifier(Protocol):
    def verify(self, token: str) -> VerifiedToken: ...


def _ensure_firebase_app(settings: Settings) -> firebase_admin.App:
    try:
        return firebase_admin.get_app()
    except ValueError:
        pass

    if settings.firebase_emulator_enabled:
        # The Admin SDK talks to the local Auth emulator when FIREBASE_AUTH_EMULATOR_HOST is set.
        return firebase_admin.initialize_app(
            options={"projectId": settings.firebase_project_id or "demo-codemind"}
        )

    if not settings.firebase_project_id or settings.firebase_service_account_b64 is None:
        raise ServiceUnavailableError(
            "Authentication is not configured on the server.", code="auth_not_configured"
        )
    try:
        info = json.loads(
            base64.b64decode(settings.firebase_service_account_b64.get_secret_value())
        )
        credential = credentials.Certificate(info)
    except (binascii.Error, ValueError) as exc:
        logger.error("firebase_credentials_invalid")
        raise ServiceUnavailableError(
            "Authentication is misconfigured on the server.", code="auth_not_configured"
        ) from exc
    return firebase_admin.initialize_app(credential, {"projectId": settings.firebase_project_id})


class FirebaseTokenVerifier:
    def __init__(self, settings: Settings) -> None:
        self._settings = settings

    def verify(self, token: str) -> VerifiedToken:
        app = _ensure_firebase_app(self._settings)
        try:
            claims: dict[str, Any] = auth.verify_id_token(token, app=app)
        except auth.ExpiredIdTokenError as exc:
            raise TokenVerificationError("token_expired") from exc
        except auth.RevokedIdTokenError as exc:
            raise TokenVerificationError("token_revoked") from exc
        except auth.CertificateFetchError as exc:
            logger.error("firebase_certificate_fetch_failed")
            raise ServiceUnavailableError(
                "Could not verify your session right now. Please retry.", code="auth_unavailable"
            ) from exc
        except (auth.InvalidIdTokenError, ValueError) as exc:
            raise TokenVerificationError("token_invalid") from exc

        uid = claims.get("uid") or claims.get("sub")
        if not isinstance(uid, str) or not uid:
            raise TokenVerificationError("token_invalid")
        email = claims.get("email")
        name = claims.get("name")
        return VerifiedToken(
            uid=uid,
            email=email if isinstance(email, str) else None,
            email_verified=bool(claims.get("email_verified", False)),
            name=name if isinstance(name, str) else None,
        )


@lru_cache
def get_token_verifier() -> TokenVerifier:
    return FirebaseTokenVerifier(get_settings())
