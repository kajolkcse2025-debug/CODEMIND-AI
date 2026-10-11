import re
import uuid
from collections.abc import Sequence
from typing import Any

from sqlalchemy import delete, select
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.orm import Session

from app.models.user import Profile, Skill, UserSkill


def skill_slug(name: str) -> str:
    return re.sub(r"[^\w+#.]+", "-", name.casefold()).strip("-")


class ProfileRepository:
    def __init__(self, session: Session) -> None:
        self._session = session

    def get(self, user_id: uuid.UUID) -> Profile | None:
        return self._session.get(Profile, user_id)

    def create(self, user_id: uuid.UUID, values: dict[str, Any]) -> Profile:
        profile = Profile(user_id=user_id, **values)
        self._session.add(profile)
        self._session.flush()
        self._session.refresh(profile)
        return profile

    def update(self, profile: Profile, values: dict[str, Any]) -> Profile:
        for key, value in values.items():
            setattr(profile, key, value)
        self._session.flush()
        self._session.refresh(profile)
        return profile

    def skill_names(self, user_id: uuid.UUID) -> list[str]:
        rows = self._session.scalars(
            select(Skill.name)
            .join(UserSkill, UserSkill.skill_id == Skill.id)
            .where(UserSkill.user_id == user_id)
            .order_by(Skill.name)
        )
        return list(rows)

    def replace_skills(self, user_id: uuid.UUID, names: Sequence[str]) -> None:
        self._session.execute(delete(UserSkill).where(UserSkill.user_id == user_id))
        by_slug = {skill_slug(name): name for name in names if skill_slug(name)}
        if not by_slug:
            return
        upsert = insert(Skill).values(
            [{"slug": slug, "name": name} for slug, name in by_slug.items()]
        )
        # Keep the first-seen display name for a slug; only ensure the row exists.
        upsert = upsert.on_conflict_do_update(
            index_elements=[Skill.slug], set_={"slug": upsert.excluded.slug}
        )
        skill_ids = self._session.scalars(upsert.returning(Skill.id))
        self._session.execute(
            insert(UserSkill),
            [{"user_id": user_id, "skill_id": skill_id} for skill_id in skill_ids],
        )
