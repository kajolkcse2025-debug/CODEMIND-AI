from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.core.errors import ConflictError, ForbiddenError
from app.models.user import User
from app.repositories.user import Identity, UserRepository


class UserService:
    def __init__(self, session: Session, users: UserRepository) -> None:
        self._session = session
        self._users = users

    def provision(self, identity: Identity) -> User:
        """Return the application user for a *verified* identity, creating it on first sight."""
        try:
            user = self._users.upsert_from_identity(identity)
            self._session.commit()
        except IntegrityError as exc:
            self._session.rollback()
            # Only reachable when two Firebase accounts claim the same e-mail address.
            raise ConflictError(
                "This e-mail address is already linked to another account.",
                code="email_in_use",
            ) from exc
        if user.account_status != "active":
            raise ForbiddenError(
                "This account is scheduled for deletion.", code="account_pending_deletion"
            )
        return user
