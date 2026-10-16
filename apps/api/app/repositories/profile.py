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
        by_slug: dict[str, str] = {}
        for name in names:
            slug = skill_slug(name)
            if slug:
                by_slug.setdefault(slug, name)  # first spelling wins within one call
        if not by_slug:
            return
        # Insert in a fixed (sorted) order and never UPDATE existing rows. Two requests that
        # insert the same skills in opposite orders and take row locks in opposite orders can
        # deadlock (PostgreSQL error 40P01); a stress test hit this in ~8% of concurrent writes.
        slugs = sorted(by_slug)
        self._session.execute(
            insert(Skill)
            .values([{"slug": slug, "name": by_slug[slug]} for slug in slugs])
            .on_conflict_do_nothing(index_elements=[Skill.slug])
        )
        skill_ids = self._session.scalars(select(Skill.id).where(Skill.slug.in_(slugs))).all()
        self._session.execute(
            insert(UserSkill),
            [{"user_id": user_id, "skill_id": skill_id} for skill_id in skill_ids],
        )
