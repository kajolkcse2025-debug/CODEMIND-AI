import uuid
from datetime import datetime
from decimal import Decimal
from typing import Any

from sqlalchemy import (
    Boolean,
    CheckConstraint,
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
from sqlalchemy.dialects.postgresql import ARRAY, JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base
from app.models._common import TIMESTAMPTZ, created_at_col, one_of, updated_at_col, user_fk, uuid_pk

INTERVIEW_KINDS = ("coding", "technical", "behavioral", "system_design")
INTERVIEW_STATUSES = ("active", "completed", "abandoned")
QUESTION_SOURCES = ("authored", "ai_drafted_reviewed")
QUESTION_STATUSES = ("draft", "review", "published", "retired")
INTERVIEW_DIMENSIONS = (
    "problem_solving",
    "technical_depth",
    "communication",
    "correctness",
    "structure",
    "ownership",
)


class InterviewQuestion(Base):
    __tablename__ = "interview_questions"
    __table_args__ = (
        CheckConstraint(one_of("kind", INTERVIEW_KINDS), name="kind_values"),
        CheckConstraint(one_of("difficulty", ("easy", "medium", "hard")), name="difficulty_values"),
        CheckConstraint(one_of("source", QUESTION_SOURCES), name="source_values"),
        CheckConstraint(one_of("status", QUESTION_STATUSES), name="status_values"),
        Index(
            "ix_interview_questions_kind_competency_difficulty", "kind", "competency", "difficulty"
        ),
    )

    id: Mapped[uuid.UUID] = uuid_pk()
    kind: Mapped[str] = mapped_column(Text, nullable=False)
    competency: Mapped[str] = mapped_column(Text, nullable=False)
    difficulty: Mapped[str] = mapped_column(Text, nullable=False)
    prompt_md: Mapped[str] = mapped_column(Text, nullable=False)
    rubric: Mapped[dict[str, Any] | None] = mapped_column(JSONB)
    company_slug: Mapped[str | None] = mapped_column(Text)
    source: Mapped[str] = mapped_column(Text, nullable=False, server_default="authored")
    status: Mapped[str] = mapped_column(Text, nullable=False, server_default="draft")
    created_at: Mapped[datetime] = created_at_col()
    updated_at: Mapped[datetime] = updated_at_col()


class InterviewSession(Base):
    __tablename__ = "interview_sessions"
    __table_args__ = (
        CheckConstraint(one_of("session_type", INTERVIEW_KINDS), name="session_type_values"),
        CheckConstraint(one_of("status", INTERVIEW_STATUSES), name="status_values"),
        CheckConstraint(
            "overall_score IS NULL OR overall_score BETWEEN 0 AND 100", name="overall_range"
        ),
        Index("ix_interview_sessions_user_started", "user_id", "started_at"),
    )

    id: Mapped[uuid.UUID] = uuid_pk()
    user_id: Mapped[uuid.UUID] = user_fk()
    session_type: Mapped[str] = mapped_column(Text, nullable=False)
    company_slug: Mapped[str | None] = mapped_column(Text)
    status: Mapped[str] = mapped_column(Text, nullable=False, server_default="active")
    rubric_version: Mapped[int | None] = mapped_column(SmallInteger)
    difficulty_start: Mapped[str | None] = mapped_column(Text)
    overall_score: Mapped[Decimal | None] = mapped_column(Numeric(5, 2))
    started_at: Mapped[datetime] = mapped_column(
        TIMESTAMPTZ, nullable=False, server_default=func.now()
    )
    ended_at: Mapped[datetime | None] = mapped_column(TIMESTAMPTZ)


class InterviewResponse(Base):
    """Immutable transcript turn. The prompt is snapshotted because follow-ups are generated."""

    __tablename__ = "interview_responses"
    __table_args__ = (
        UniqueConstraint("session_id", "turn_index", name="uq_interview_responses_session_turn"),
    )

    id: Mapped[uuid.UUID] = uuid_pk()
    session_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("interview_sessions.id", ondelete="CASCADE"), nullable=False
    )
    user_id: Mapped[uuid.UUID] = user_fk(index=True)
    turn_index: Mapped[int] = mapped_column(Integer, nullable=False)
    question_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("interview_questions.id", ondelete="SET NULL")
    )
    prompt_text: Mapped[str] = mapped_column(Text, nullable=False)
    response_text: Mapped[str] = mapped_column(Text, nullable=False)
    is_follow_up: Mapped[bool] = mapped_column(
        Boolean, nullable=False, server_default=text("false")
    )
    parent_response_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("interview_responses.id", ondelete="SET NULL")
    )
    response_time_sec: Mapped[int | None] = mapped_column(Integer)
    created_at: Mapped[datetime] = created_at_col()


class InterviewScore(Base):
    """Rubric level (from the AI, constrained to 1-5) and score (computed by code)."""

    __tablename__ = "interview_scores"
    __table_args__ = (
        CheckConstraint(one_of("dimension", INTERVIEW_DIMENSIONS), name="dimension_values"),
        CheckConstraint("rubric_level BETWEEN 1 AND 5", name="rubric_level_range"),
        CheckConstraint("score BETWEEN 0 AND 100", name="score_range"),
        UniqueConstraint("session_id", "dimension", name="uq_interview_scores_session_dimension"),
    )

    id: Mapped[uuid.UUID] = uuid_pk()
    session_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("interview_sessions.id", ondelete="CASCADE"), nullable=False
    )
    user_id: Mapped[uuid.UUID] = user_fk(index=True)
    dimension: Mapped[str] = mapped_column(Text, nullable=False)
    rubric_level: Mapped[int] = mapped_column(SmallInteger, nullable=False)
    score: Mapped[Decimal] = mapped_column(Numeric(5, 2), nullable=False)
    justification: Mapped[str | None] = mapped_column(Text)
    evidence_response_ids: Mapped[list[uuid.UUID]] = mapped_column(
        ARRAY(UUID(as_uuid=True)), nullable=False, server_default=text("'{}'::uuid[]")
    )
    rubric_version: Mapped[int] = mapped_column(SmallInteger, nullable=False)
