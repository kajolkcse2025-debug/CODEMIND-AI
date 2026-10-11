import uuid
from dataclasses import dataclass

from sqlalchemy import func, select
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.orm import Session

from app.models.user import User


@dataclass(frozen=True)
class Identity:
    firebase_uid: str
    email: str | None
    display_name: str | None


class UserRepository:
    def __init__(self, session: Session) -> None:
        self._session = session

    def get(self, user_id: uuid.UUID) -> User | None:
        return self._session.get(User, user_id)

    def get_by_firebase_uid(self, firebase_uid: str) -> User | None:
        return self._session.scalars(
            select(User).where(User.firebase_uid == firebase_uid)
        ).one_or_none()

    def upsert_from_identity(self, identity: Identity) -> User:
        """Race-safe provision: concurrent first requests converge on one row."""
        statement = insert(User).values(
            firebase_uid=identity.firebase_uid,
            email=identity.email,
            display_name=identity.display_name,
            last_active_at=func.now(),
        )
        statement = statement.on_conflict_do_update(
            index_elements=[User.firebase_uid],
            set_={
                "email": func.coalesce(statement.excluded.email, User.email),
                "display_name": func.coalesce(User.display_name, statement.excluded.display_name),
                "last_active_at": func.now(),
            },
        )
        return self._session.scalars(
            statement.returning(User), execution_options={"populate_existing": True}
        ).one()

    def set_onboarding_status(self, user: User, status: str) -> None:
        user.onboarding_status = status
        self._session.flush()
