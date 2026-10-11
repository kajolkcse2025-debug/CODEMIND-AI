import uuid
from datetime import datetime
from typing import Any

from sqlalchemy import Boolean, CheckConstraint, ForeignKey, Index, Integer, Text, text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base
from app.models._common import TIMESTAMPTZ, created_at_col, updated_at_col, user_fk, uuid_pk


class Achievement(Base):
    __tablename__ = "achievements"
    __table_args__ = (CheckConstraint("xp_reward >= 0", name="xp_reward_non_negative"),)

    id: Mapped[uuid.UUID] = uuid_pk()
    code: Mapped[str] = mapped_column(Text, nullable=False, unique=True)
    name: Mapped[str] = mapped_column(Text, nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    # Declarative rule evaluated by backend code, never by an LLM.
    criteria: Mapped[dict[str, Any]] = mapped_column(
        JSONB, nullable=False, server_default=text("'{}'::jsonb")
    )
    tier: Mapped[str | None] = mapped_column(Text)
    xp_reward: Mapped[int] = mapped_column(Integer, nullable=False, server_default="0")
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default=text("true"))
    created_at: Mapped[datetime] = created_at_col()
    updated_at: Mapped[datetime] = updated_at_col()


class UserAchievement(Base):
    __tablename__ = "user_achievements"
    __table_args__ = (Index("ix_user_achievements_user_earned", "user_id", "earned_at"),)

    user_id: Mapped[uuid.UUID] = user_fk(primary_key=True)
    achievement_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("achievements.id", ondelete="CASCADE"), primary_key=True
    )
    earned_at: Mapped[datetime] = mapped_column(
        TIMESTAMPTZ, nullable=False, server_default=text("now()")
    )
    source_ref: Mapped[str | None] = mapped_column(Text)
