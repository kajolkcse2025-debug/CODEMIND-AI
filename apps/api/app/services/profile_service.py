from typing import Any

from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.core.errors import ConflictError, NotFoundError
from app.models.user import Profile, User
from app.repositories.profile import ProfileRepository
from app.repositories.user import UserRepository
from app.schemas.profile import ProfileIn, ProfileOut


def _violated_constraint(exc: IntegrityError) -> str | None:
    """The name of the constraint a PostgreSQL integrity error refers to, if known."""
    diag = getattr(exc.orig, "diag", None)
    name = getattr(diag, "constraint_name", None)
    return name if isinstance(name, str) else None


class ProfileService:
    def __init__(
        self, session: Session, profiles: ProfileRepository, users: UserRepository
    ) -> None:
        self._session = session
        self._profiles = profiles
        self._users = users

    def _to_out(self, profile: Profile) -> ProfileOut:
        base = ProfileOut.model_validate(
            {
                **{c: getattr(profile, c) for c in ProfileOut.model_fields if c != "skills"},
                "skills": self._profiles.skill_names(profile.user_id),
            }
        )
        return base

    @staticmethod
    def _column_values(data: ProfileIn) -> dict[str, Any]:
        return data.model_dump(exclude={"skills"})

    def get_optional(self, user: User) -> ProfileOut | None:
        profile = self._profiles.get(user.id)
        return self._to_out(profile) if profile else None

    def get(self, user: User) -> ProfileOut:
        profile = self.get_optional(user)
        if profile is None:
            raise NotFoundError("You have not created a profile yet.", code="profile_not_found")
        return profile

    def create(self, user: User, data: ProfileIn) -> ProfileOut:
        if self._profiles.get(user.id) is not None:
            raise ConflictError(
                "A profile already exists. Use PUT to update it.", code="profile_exists"
            )
        try:
            profile = self._profiles.create(user.id, self._column_values(data))
        except IntegrityError as exc:
            self._session.rollback()
            # Two simultaneous submissions both passed the check above; the database primary key
            # decided the winner. That is a normal conflict, not a server error.
            if _violated_constraint(exc) == "pk_profiles":
                raise ConflictError(
                    "A profile already exists. Use PUT to update it.", code="profile_exists"
                ) from exc
            raise
        self._profiles.replace_skills(user.id, data.skills)
        # Phase 1: creating the profile is the whole onboarding. Consent capture comes later.
        self._users.set_onboarding_status(user, "complete")
        self._session.commit()
        return self._to_out(profile)

    def update(self, user: User, data: ProfileIn) -> ProfileOut:
        profile = self._profiles.get(user.id)
        if profile is None:
            raise NotFoundError("You have not created a profile yet.", code="profile_not_found")
        profile = self._profiles.update(profile, self._column_values(data))
        self._profiles.replace_skills(user.id, data.skills)
        self._session.commit()
        return self._to_out(profile)
