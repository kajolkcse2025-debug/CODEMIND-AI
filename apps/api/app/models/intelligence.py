"""Derived student-intelligence state. Rebuildable from the immutable activity events."""

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
    func,
    text,
)
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base
from app.models._common import TIMESTAMPTZ, created_at_col, one_of, updated_at_col, user_fk, uuid_pk

MASTERY_BANDS = ("unexplored", "weak", "developing", "proficient", "strong")
DNA_TRAITS = (
    "logical_reasoning",
    "debugging",
    "optimization",
    "edge_case_awareness",
    "time_management",
    "hint_independence",
    "consistency",
    "recursion_ability",
)
DNA_STATES = ("calibrating", "provisional", "established")
WEAKNESS_STATUSES = ("active", "improving", "resolved", "dismissed")


class TopicPerformance(Base):
    """Per-student, per-topic metrics. ``mastery_score`` stays NULL until it can be computed."""

    __tablename__ = "topic_performance"
    __table_args__ = (
        CheckConstraint(one_of("band", MASTERY_BANDS), name="band_values"),
        CheckConstraint(
            "mastery_score IS NULL OR mastery_score BETWEEN 0 AND 100", name="mastery_range"
        ),
        CheckConstraint("confidence BETWEEN 0 AND 1", name="confidence_range"),
        CheckConstraint("attempts_count >= 0 AND solved_count >= 0", name="counts_non_negative"),
        Index("ix_topic_performance_user_mastery", "user_id", "mastery_score"),
    )

    user_id: Mapped[uuid.UUID] = user_fk(primary_key=True)
    topic_id: Mapped[int] = mapped_column(
        SmallInteger, ForeignKey("topics.id", ondelete="CASCADE"), primary_key=True
    )
    attempts_count: Mapped[int] = mapped_column(Integer, nullable=False, server_default="0")
    solved_count: Mapped[int] = mapped_column(Integer, nullable=False, server_default="0")
    first_try_solved_count: Mapped[int] = mapped_column(Integer, nullable=False, server_default="0")
    accuracy: Mapped[Decimal | None] = mapped_column(Numeric(5, 4))
    success_rate: Mapped[Decimal | None] = mapped_column(Numeric(5, 4))
    avg_solve_time_sec: Mapped[int | None] = mapped_column(Integer)
    avg_hints: Mapped[Decimal | None] = mapped_column(Numeric(4, 2))
    mastery_score: Mapped[Decimal | None] = mapped_column(Numeric(5, 2))
    confidence: Mapped[Decimal] = mapped_column(Numeric(4, 3), nullable=False, server_default="0")
    band: Mapped[str] = mapped_column(Text, nullable=False, server_default="unexplored")
    last_practiced_at: Mapped[datetime | None] = mapped_column(TIMESTAMPTZ)
    engine_version: Mapped[int] = mapped_column(SmallInteger, nullable=False, server_default="0")
    updated_at: Mapped[datetime] = updated_at_col()


class CodingDnaTrait(Base):
    """One row per (student, trait). A calibrating trait can never carry a score."""

    __tablename__ = "coding_dna"
    __table_args__ = (
        CheckConstraint(one_of("trait", DNA_TRAITS), name="trait_values"),
        CheckConstraint(one_of("state", DNA_STATES), name="state_values"),
        CheckConstraint("score IS NULL OR score BETWEEN 0 AND 100", name="score_range"),
        CheckConstraint("confidence BETWEEN 0 AND 1", name="confidence_range"),
        CheckConstraint("state <> 'calibrating' OR score IS NULL", name="calibrating_has_no_score"),
    )

    user_id: Mapped[uuid.UUID] = user_fk(primary_key=True)
    trait: Mapped[str] = mapped_column(Text, primary_key=True)
    score: Mapped[Decimal | None] = mapped_column(Numeric(5, 2))
    sample_count: Mapped[int] = mapped_column(Integer, nullable=False, server_default="0")
    confidence: Mapped[Decimal] = mapped_column(Numeric(4, 3), nullable=False, server_default="0")
    state: Mapped[str] = mapped_column(Text, nullable=False, server_default="calibrating")
    engine_version: Mapped[int] = mapped_column(SmallInteger, nullable=False, server_default="0")
    updated_at: Mapped[datetime] = updated_at_col()


class DetectedWeakness(Base):
    __tablename__ = "detected_weaknesses"
    __table_args__ = (
        CheckConstraint(one_of("status", WEAKNESS_STATUSES), name="status_values"),
        CheckConstraint("severity BETWEEN 0 AND 1", name="severity_range"),
        CheckConstraint("confidence BETWEEN 0 AND 1", name="confidence_range"),
        Index(
            "uq_detected_weaknesses_open",
            "user_id",
            "weakness_code",
            text("coalesce(topic_id, 0)"),
            unique=True,
            postgresql_where=text("status IN ('active', 'improving')"),
        ),
        Index("ix_detected_weaknesses_user_status_severity", "user_id", "status", "severity"),
    )

    id: Mapped[uuid.UUID] = uuid_pk()
    user_id: Mapped[uuid.UUID] = user_fk()
    weakness_code: Mapped[str] = mapped_column(Text, nullable=False)
    topic_id: Mapped[int | None] = mapped_column(
        SmallInteger, ForeignKey("topics.id", ondelete="SET NULL")
    )
    severity: Mapped[Decimal] = mapped_column(Numeric(3, 2), nullable=False)
    confidence: Mapped[Decimal] = mapped_column(Numeric(3, 2), nullable=False)
    occurrences: Mapped[int] = mapped_column(Integer, nullable=False, server_default="0")
    first_detected_at: Mapped[datetime] = mapped_column(
        TIMESTAMPTZ, nullable=False, server_default=func.now()
    )
    last_detected_at: Mapped[datetime] = mapped_column(
        TIMESTAMPTZ, nullable=False, server_default=func.now()
    )
    status: Mapped[str] = mapped_column(Text, nullable=False, server_default="active")
    resolved_at: Mapped[datetime | None] = mapped_column(TIMESTAMPTZ)
    # Regenerable narrative text. It is never an input to any score.
    ai_interpretation: Mapped[str | None] = mapped_column(Text)
    interpretation_version: Mapped[int | None] = mapped_column(Integer)
    engine_version: Mapped[int] = mapped_column(SmallInteger, nullable=False, server_default="0")
    created_at: Mapped[datetime] = created_at_col()
    updated_at: Mapped[datetime] = updated_at_col()


class Streak(Base):
    __tablename__ = "streaks"
    __table_args__ = (
        CheckConstraint("current_streak >= 0 AND longest_streak >= 0", name="non_negative"),
        CheckConstraint("freezes_available >= 0", name="freezes_non_negative"),
    )

    user_id: Mapped[uuid.UUID] = user_fk(primary_key=True)
    current_streak: Mapped[int] = mapped_column(Integer, nullable=False, server_default="0")
    longest_streak: Mapped[int] = mapped_column(Integer, nullable=False, server_default="0")
    last_active_date: Mapped[date | None] = mapped_column(Date)
    freezes_available: Mapped[int] = mapped_column(SmallInteger, nullable=False, server_default="0")
    updated_at: Mapped[datetime] = updated_at_col()


__all__: list[Any] = []
