"""FastAPI dependencies: the only place routers get collaborators from."""

from fastapi import Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session
from app.repositories.problems import ProblemsRepository
from app.services.problems_service import ProblemsService

from app.core.errors import UnauthenticatedError
from app.core.redis import KeyValueStore, get_store
from app.core.security import (
    TokenVerificationError,
    TokenVerifier,
    VerifiedToken,
    get_token_verifier,
)
from app.db.session import get_db
from app.models.user import User
from app.repositories.profile import ProfileRepository
from app.repositories.user import Identity, UserRepository
from app.services.health_service import HealthService
from app.services.profile_service import ProfileService
from app.services.user_service import UserService

_bearer = HTTPBearer(auto_error=False)
_WWW_AUTHENTICATE = {"WWW-Authenticate": "Bearer"}


def get_health_service(
    session: Session = Depends(get_db), store: KeyValueStore = Depends(get_store)
) -> HealthService:
    return HealthService(session, store)


def get_user_service(session: Session = Depends(get_db)) -> UserService:
    return UserService(session, UserRepository(session))


def get_profile_service(session: Session = Depends(get_db)) -> ProfileService:
    return ProfileService(session, ProfileRepository(session), UserRepository(session))


def get_verified_token(
    credentials: HTTPAuthorizationCredentials | None = Depends(_bearer),
    verifier: TokenVerifier = Depends(get_token_verifier),
) -> VerifiedToken:
    """Verify the Bearer token. FastAPI caches this per request, so it runs once."""
    if credentials is None or not credentials.credentials:
        raise UnauthenticatedError(
            "Sign in to continue.", details={"reason": "missing_token"}, headers=_WWW_AUTHENTICATE
        )
    try:
        return verifier.verify(credentials.credentials)
    except TokenVerificationError as exc:
        raise UnauthenticatedError(
            "Your session is not valid. Sign in again.",
            details={"reason": exc.reason},
            headers=_WWW_AUTHENTICATE,
        ) from exc


def get_current_user(
    token: VerifiedToken = Depends(get_verified_token),
    users: UserService = Depends(get_user_service),
) -> User:
    """The authenticated application user, derived solely from the verified token."""
    return users.provision(Identity(token.uid, token.email, token.name))
def get_problems_service(
    session: Session = Depends(get_db),
) -> ProblemsService:
    return ProblemsService(ProblemsRepository(session))
