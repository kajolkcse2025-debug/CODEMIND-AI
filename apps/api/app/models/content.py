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
    text,
)
from sqlalchemy.dialects.postgresql import ARRAY, JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base
from app.models._common import created_at_col, one_of, updated_at_col, uuid_pk

DIFFICULTIES = ("easy", "medium", "hard")
PROBLEM_STATUSES = ("draft", "review", "published", "retired")


class Topic(Base):
    """The single canonical topic taxonomy (assessment, analytics and roadmap all use it)."""

    __tablename__ = "topics"
    __table_args__ = (
        CheckConstraint("interview_weight BETWEEN 0 AND 3", name="interview_weight_range"),
        CheckConstraint(
            "diagnostic_round IS NULL OR diagnostic_round IN (1, 2, 3)",
            name="diagnostic_round_values",
        ),
    )

    id: Mapped[int] = mapped_column(SmallInteger, primary_key=True, autoincrement=False)
    slug: Mapped[str] = mapped_column(Text, nullable=False, unique=True)
    name: Mapped[str] = mapped_column(Text, nullable=False)
    display_order: Mapped[int] = mapped_column(SmallInteger, nullable=False)
    # 1 = easy round, 2 = medium round, 3 = advanced round; NULL = not part of the diagnostic.
    diagnostic_round: Mapped[int | None] = mapped_column(SmallInteger)
    # Tunable assumption, not measured data. Phase 1 seeds every topic at 1.00.
    interview_weight: Mapped[Decimal] = mapped_column(
        Numeric(3, 2), nullable=False, server_default="1.00"
    )
    created_at: Mapped[datetime] = created_at_col()
    updated_at: Mapped[datetime] = updated_at_col()


class Problem(Base):
    __tablename__ = "problems"
    __table_args__ = (
        CheckConstraint(one_of("difficulty", DIFFICULTIES), name="difficulty_values"),
        CheckConstraint(one_of("status", PROBLEM_STATUSES), name="status_values"),
        CheckConstraint("expected_time_sec > 0", name="expected_time_positive"),
        CheckConstraint("version >= 1", name="version_positive"),
        CheckConstraint(
            "diagnostic_level IS NULL OR (is_diagnostic AND diagnostic_level IN (1, 2, 3))",
            name="diagnostic_level_values",
        ),
        Index("ix_problems_status_difficulty", "status", "difficulty"),
    )

    id: Mapped[uuid.UUID] = uuid_pk()
    slug: Mapped[str] = mapped_column(Text, nullable=False, unique=True)
    title: Mapped[str] = mapped_column(Text, nullable=False)
    statement_md: Mapped[str] = mapped_column(Text, nullable=False)
    constraints_md: Mapped[str | None] = mapped_column(Text)
    difficulty: Mapped[str] = mapped_column(Text, nullable=False)
    expected_time_sec: Mapped[int] = mapped_column(Integer, nullable=False)
    optimal_time_complexity: Mapped[str | None] = mapped_column(Text)
    optimal_space_complexity: Mapped[str | None] = mapped_column(Text)
    complexity_options: Mapped[dict[str, Any] | None] = mapped_column(JSONB)
    starter_code: Mapped[dict[str, Any] | None] = mapped_column(JSONB)
    technique_tags: Mapped[list[str]] = mapped_column(
        ARRAY(Text), nullable=False, server_default=text("'{}'::text[]")
    )
    optimization_relevant: Mapped[bool] = mapped_column(
        Boolean, nullable=False, server_default=text("false")
    )
    status: Mapped[str] = mapped_column(Text, nullable=False, server_default="draft")
    is_diagnostic: Mapped[bool] = mapped_column(
        Boolean, nullable=False, server_default=text("false")
    )
    diagnostic_level: Mapped[int | None] = mapped_column(SmallInteger)
    version: Mapped[int] = mapped_column(Integer, nullable=False, server_default="1")
    created_at: Mapped[datetime] = created_at_col()
    updated_at: Mapped[datetime] = updated_at_col()


class ProblemTopic(Base):
    __tablename__ = "problem_topics"
    __table_args__ = (
        Index(
            "uq_problem_topics_one_primary",
            "problem_id",
            unique=True,
            postgresql_where=text("is_primary"),
        ),
    )

    problem_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("problems.id", ondelete="CASCADE"), primary_key=True
    )
    topic_id: Mapped[int] = mapped_column(
        SmallInteger, ForeignKey("topics.id", ondelete="RESTRICT"), primary_key=True, index=True
    )
    is_primary: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default=text("false"))
class ProblemTestCase(Base):
    """Input/output test case used to verify a coding problem."""

    __tablename__ = "problem_test_cases"
    __table_args__ = (
        UniqueConstraint(
            "problem_id",
            "problem_version",
            "case_index",
            name="problem_version_case_index",
        ),
        CheckConstraint("problem_version >= 1", name="version_positive"),
        CheckConstraint("case_index >= 1", name="case_index_positive"),
    )

    id: Mapped[uuid.UUID] = uuid_pk()
    problem_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("problems.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    problem_version: Mapped[int] = mapped_column(Integer, nullable=False)
    case_index: Mapped[int] = mapped_column(Integer, nullable=False)
    stdin: Mapped[str] = mapped_column(Text, nullable=False)
    expected_stdout: Mapped[str] = mapped_column(Text, nullable=False)
    is_hidden: Mapped[bool] = mapped_column(
        Boolean, nullable=False, server_default=text("true")
    )
    created_at: Mapped[datetime] = created_at_col()