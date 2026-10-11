import uuid
from datetime import date, datetime
from decimal import Decimal
from typing import Any

from sqlalchemy import (
    CheckConstraint,
    Date,
    ForeignKey,
    Index,
    Integer,
    Numeric,
    SmallInteger,
    Text,
    UniqueConstraint,
    func,
    text,
)
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base
from app.models._common import TIMESTAMPTZ, created_at_col, one_of, user_fk, uuid_pk

ROADMAP_KINDS = ("standard", "dream")
ROADMAP_STATUSES = ("active", "superseded", "completed")
ROADMAP_ITEM_TYPES = ("learn", "practice", "revise", "project", "milestone")
ROADMAP_ITEM_STATUSES = ("upcoming", "active", "done", "skipped")
MISSION_STATUSES = ("generated", "in_progress", "completed", "partial", "expired")
MISSION_SLOTS = ("easy", "medium", "revision", "interview")
MISSION_ITEM_STATUSES = ("pending", "started", "completed", "skipped", "swapped")


class Roadmap(Base):
    __tablename__ = "roadmaps"
    __table_args__ = (
        CheckConstraint(one_of("kind", ROADMAP_KINDS), name="kind_values"),
        CheckConstraint(one_of("status", ROADMAP_STATUSES), name="status_values"),
        CheckConstraint("version >= 1", name="version_positive"),
        Index(
            "uq_roadmaps_one_active_per_kind",
            "user_id",
            "kind",
            unique=True,
            postgresql_where=text("status = 'active'"),
        ),
    )

    id: Mapped[uuid.UUID] = uuid_pk()
    user_id: Mapped[uuid.UUID] = user_fk(index=True)
    kind: Mapped[str] = mapped_column(Text, nullable=False, server_default="standard")
    status: Mapped[str] = mapped_column(Text, nullable=False, server_default="active")
    version: Mapped[int] = mapped_column(Integer, nullable=False, server_default="1")
    parent_roadmap_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("roadmaps.id", ondelete="SET NULL")
    )
    company_slug: Mapped[str | None] = mapped_column(Text)
    target_date: Mapped[date | None] = mapped_column(Date)
    daily_minutes: Mapped[int | None] = mapped_column(SmallInteger)
    inputs_snapshot: Mapped[dict[str, Any] | None] = mapped_column(JSONB)
    rationale_md: Mapped[str | None] = mapped_column(Text)
    engine_version: Mapped[int | None] = mapped_column(SmallInteger)
    created_at: Mapped[datetime] = created_at_col()


class RoadmapItem(Base):
    __tablename__ = "roadmap_items"
    __table_args__ = (
        CheckConstraint(one_of("item_type", ROADMAP_ITEM_TYPES), name="item_type_values"),
        CheckConstraint(one_of("status", ROADMAP_ITEM_STATUSES), name="status_values"),
        CheckConstraint("completed_count <= target_problem_count", name="completed_le_target"),
        UniqueConstraint("roadmap_id", "position", name="uq_roadmap_items_roadmap_position"),
        Index("ix_roadmap_items_roadmap_status", "roadmap_id", "status"),
    )

    id: Mapped[uuid.UUID] = uuid_pk()
    roadmap_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("roadmaps.id", ondelete="CASCADE"), nullable=False
    )
    user_id: Mapped[uuid.UUID] = user_fk(index=True)
    position: Mapped[int] = mapped_column(Integer, nullable=False)
    phase_label: Mapped[str | None] = mapped_column(Text)
    topic_id: Mapped[int | None] = mapped_column(
        SmallInteger, ForeignKey("topics.id", ondelete="SET NULL")
    )
    item_type: Mapped[str] = mapped_column(Text, nullable=False)
    title: Mapped[str] = mapped_column(Text, nullable=False)
    target_problem_count: Mapped[int] = mapped_column(
        SmallInteger, nullable=False, server_default="0"
    )
    completed_count: Mapped[int] = mapped_column(SmallInteger, nullable=False, server_default="0")
    start_date: Mapped[date | None] = mapped_column(Date)
    due_date: Mapped[date | None] = mapped_column(Date)
    status: Mapped[str] = mapped_column(Text, nullable=False, server_default="upcoming")
    reason_code: Mapped[str | None] = mapped_column(Text)
    reason_detail: Mapped[dict[str, Any] | None] = mapped_column(JSONB)


class DailyMission(Base):
    __tablename__ = "daily_missions"
    __table_args__ = (
        CheckConstraint(one_of("status", MISSION_STATUSES), name="status_values"),
        CheckConstraint("pacing_factor BETWEEN 0.5 AND 1.5", name="pacing_factor_range"),
        UniqueConstraint("user_id", "mission_date", name="uq_daily_missions_user_date"),
    )

    id: Mapped[uuid.UUID] = uuid_pk()
    user_id: Mapped[uuid.UUID] = user_fk()
    mission_date: Mapped[date] = mapped_column(Date, nullable=False)
    status: Mapped[str] = mapped_column(Text, nullable=False, server_default="generated")
    budget_minutes: Mapped[int | None] = mapped_column(SmallInteger)
    estimated_minutes: Mapped[int | None] = mapped_column(SmallInteger)
    pacing_factor: Mapped[Decimal] = mapped_column(
        Numeric(3, 2), nullable=False, server_default="1.00"
    )
    roadmap_item_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("roadmap_items.id", ondelete="SET NULL")
    )
    engine_version: Mapped[int | None] = mapped_column(SmallInteger)
    generated_at: Mapped[datetime] = mapped_column(
        TIMESTAMPTZ, nullable=False, server_default=func.now()
    )


class MissionItem(Base):
    __tablename__ = "mission_items"
    __table_args__ = (
        CheckConstraint(one_of("slot", MISSION_SLOTS), name="slot_values"),
        CheckConstraint(one_of("status", MISSION_ITEM_STATUSES), name="status_values"),
        CheckConstraint(
            "num_nonnulls(problem_id, interview_question_id) = 1", name="exactly_one_target"
        ),
        UniqueConstraint("mission_id", "position", name="uq_mission_items_mission_position"),
    )

    id: Mapped[uuid.UUID] = uuid_pk()
    mission_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("daily_missions.id", ondelete="CASCADE"), nullable=False
    )
    user_id: Mapped[uuid.UUID] = user_fk(index=True)
    position: Mapped[int] = mapped_column(SmallInteger, nullable=False)
    slot: Mapped[str] = mapped_column(Text, nullable=False)
    problem_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("problems.id", ondelete="RESTRICT")
    )
    interview_question_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("interview_questions.id", ondelete="RESTRICT")
    )
    estimated_minutes: Mapped[int | None] = mapped_column(SmallInteger)
    reason_code: Mapped[str | None] = mapped_column(Text)
    weakness_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("detected_weaknesses.id", ondelete="SET NULL")
    )
    status: Mapped[str] = mapped_column(Text, nullable=False, server_default="pending")
    completed_attempt_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("coding_attempts.id", ondelete="SET NULL")
    )
