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
from app.models._common import TIMESTAMPTZ, created_at_col, one_of, user_fk, uuid_pk

ATTEMPT_CONTEXTS = ("assessment", "mission", "practice", "revision", "coach")
ATTEMPT_OUTCOMES = ("in_progress", "accepted", "failed", "abandoned")
SUBMISSION_KINDS = ("run", "submit")
VERDICTS = (
    "accepted",
    "wrong_answer",
    "runtime_error",
    "time_limit",
    "memory_limit",
    "compile_error",
    "runner_unavailable",
)
DETECTORS = ("rule", "statistical", "ai_assist")


class CodingAttempt(Base):
    """One student's sitting with one problem. Closed attempts are treated as immutable."""

    __tablename__ = "coding_attempts"
    __table_args__ = (
        CheckConstraint(one_of("context", ATTEMPT_CONTEXTS), name="context_values"),
        CheckConstraint(one_of("outcome", ATTEMPT_OUTCOMES), name="outcome_values"),
        CheckConstraint("attempt_index >= 1", name="attempt_index_positive"),
        CheckConstraint("active_time_sec >= 0", name="active_time_non_negative"),
        CheckConstraint("hints_used >= 0", name="hints_non_negative"),
        UniqueConstraint("user_id", "idempotency_key", name="uq_coding_attempts_user_idempotency"),
        Index("ix_coding_attempts_user_problem_started", "user_id", "problem_id", "started_at"),
        Index("ix_coding_attempts_user_ended", "user_id", "ended_at"),
    )

    id: Mapped[uuid.UUID] = uuid_pk()
    user_id: Mapped[uuid.UUID] = user_fk()
    problem_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("problems.id", ondelete="RESTRICT"), nullable=False
    )
    problem_version: Mapped[int] = mapped_column(Integer, nullable=False)
    context: Mapped[str] = mapped_column(Text, nullable=False)
    context_ref_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True))
    attempt_index: Mapped[int] = mapped_column(Integer, nullable=False, server_default="1")
    started_at: Mapped[datetime] = mapped_column(
        TIMESTAMPTZ, nullable=False, server_default=func.now()
    )
    ended_at: Mapped[datetime | None] = mapped_column(TIMESTAMPTZ)
    outcome: Mapped[str] = mapped_column(Text, nullable=False, server_default="in_progress")
    active_time_sec: Mapped[int] = mapped_column(Integer, nullable=False, server_default="0")
    submission_count: Mapped[int] = mapped_column(SmallInteger, nullable=False, server_default="0")
    hints_used: Mapped[int] = mapped_column(SmallInteger, nullable=False, server_default="0")
    declared_time_complexity: Mapped[str | None] = mapped_column(Text)
    declared_space_complexity: Mapped[str | None] = mapped_column(Text)
    complexity_correct: Mapped[bool | None] = mapped_column(Boolean)
    idempotency_key: Mapped[str | None] = mapped_column(Text)
    created_at: Mapped[datetime] = created_at_col()


class CodeSubmission(Base):
    """Immutable record of one run or submit.

    ``verified`` is true only when a real, sandboxed runner produced the verdict. Unverified
    results (for example ``runner_unavailable``) must never feed mastery, XP, DNA or readiness.
    """

    __tablename__ = "code_submissions"
    __table_args__ = (
        CheckConstraint(one_of("kind", SUBMISSION_KINDS), name="kind_values"),
        CheckConstraint(one_of("verdict", VERDICTS), name="verdict_values"),
        CheckConstraint("tests_passed <= tests_total", name="tests_passed_le_total"),
        CheckConstraint("octet_length(code) <= 65536", name="code_size_limit"),
        CheckConstraint(
            "verdict <> 'runner_unavailable' OR NOT verified", name="unavailable_is_unverified"
        ),
        Index("ix_code_submissions_attempt_submitted", "attempt_id", "submitted_at"),
        Index("ix_code_submissions_user_submitted", "user_id", "submitted_at"),
        Index("ix_code_submissions_failed_test_tags", "failed_test_tags", postgresql_using="gin"),
    )

    id: Mapped[uuid.UUID] = uuid_pk()
    attempt_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("coding_attempts.id", ondelete="CASCADE"), nullable=False
    )
    user_id: Mapped[uuid.UUID] = user_fk()
    language: Mapped[str] = mapped_column(Text, nullable=False)
    # Nullable so the retention job can drop the body but keep verdict metadata.
    code: Mapped[str | None] = mapped_column(Text)
    code_sha256: Mapped[str] = mapped_column(Text, nullable=False)
    kind: Mapped[str] = mapped_column(Text, nullable=False)
    verdict: Mapped[str] = mapped_column(Text, nullable=False)
    verified: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default=text("false"))
    tests_passed: Mapped[int] = mapped_column(SmallInteger, nullable=False, server_default="0")
    tests_total: Mapped[int] = mapped_column(SmallInteger, nullable=False, server_default="0")
    failed_test_tags: Mapped[list[str]] = mapped_column(
        ARRAY(Text), nullable=False, server_default=text("'{}'::text[]")
    )
    max_time_ms: Mapped[int | None] = mapped_column(Integer)
    max_memory_kb: Mapped[int | None] = mapped_column(Integer)
    runner_job_id: Mapped[str | None] = mapped_column(Text)
    submitted_at: Mapped[datetime] = mapped_column(
        TIMESTAMPTZ, nullable=False, server_default=func.now()
    )


class DetectedError(Base):
    __tablename__ = "detected_errors"
    __table_args__ = (
        CheckConstraint(one_of("detector", DETECTORS), name="detector_values"),
        CheckConstraint("confidence BETWEEN 0 AND 1", name="confidence_range"),
        Index("ix_detected_errors_user_code_detected", "user_id", "error_code", "detected_at"),
        Index("ix_detected_errors_submission", "submission_id"),
    )

    id: Mapped[uuid.UUID] = uuid_pk()
    user_id: Mapped[uuid.UUID] = user_fk()
    submission_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("code_submissions.id", ondelete="CASCADE"), nullable=False
    )
    topic_id: Mapped[int | None] = mapped_column(
        SmallInteger, ForeignKey("topics.id", ondelete="SET NULL")
    )
    error_code: Mapped[str] = mapped_column(Text, nullable=False)
    detector: Mapped[str] = mapped_column(Text, nullable=False)
    confidence: Mapped[Decimal] = mapped_column(Numeric(3, 2), nullable=False)
    evidence: Mapped[dict[str, Any] | None] = mapped_column(JSONB)
    detected_at: Mapped[datetime] = mapped_column(
        TIMESTAMPTZ, nullable=False, server_default=func.now()
    )
