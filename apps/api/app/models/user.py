import uuid
from datetime import datetime
from decimal import Decimal

from sqlalchemy import (
    CheckConstraint,
    ForeignKey,
    Index,
    Integer,
    Numeric,
    SmallInteger,
    Text,
    text,
)
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base
from app.models._common import (
    TIMESTAMPTZ,
    created_at_col,
    one_of,
    updated_at_col,
    user_fk,
    uuid_pk,
)

ROLES = ("student", "admin")
PROGRESS_STATUSES = ("not_started", "in_progress", "complete")
ACCOUNT_STATUSES = ("active", "pending_deletion")
CGPA_SCALES = (4, 5, 10)
PREFERRED_LANGUAGES = ("python", "java", "cpp")


class User(Base):
    """Application user, keyed by the verified Firebase uid. Never created from client input."""

    __tablename__ = "users"
    __table_args__ = (
        CheckConstraint(one_of("role", ROLES), name="role_values"),
        CheckConstraint(one_of("onboarding_status", PROGRESS_STATUSES), name="onboarding_values"),
        CheckConstraint(one_of("assessment_status", PROGRESS_STATUSES), name="assessment_values"),
        CheckConstraint(one_of("account_status", ACCOUNT_STATUSES), name="account_status_values"),
        CheckConstraint("xp_total >= 0", name="xp_non_negative"),
        CheckConstraint("level >= 1", name="level_positive"),
        Index(
            "uq_users_email_lower",
            text("lower(email)"),
            unique=True,
            postgresql_where=text("email IS NOT NULL"),
        ),
    )

    id: Mapped[uuid.UUID] = uuid_pk()
    firebase_uid: Mapped[str] = mapped_column(Text, nullable=False, unique=True)
    email: Mapped[str | None] = mapped_column(Text)
    display_name: Mapped[str | None] = mapped_column(Text)
    role: Mapped[str] = mapped_column(Text, nullable=False, server_default="student")
    onboarding_status: Mapped[str] = mapped_column(
        Text, nullable=False, server_default="not_started"
    )
    assessment_status: Mapped[str] = mapped_column(
        Text, nullable=False, server_default="not_started"
    )
    xp_total: Mapped[int] = mapped_column(Integer, nullable=False, server_default="0")
    level: Mapped[int] = mapped_column(SmallInteger, nullable=False, server_default="1")
    account_status: Mapped[str] = mapped_column(Text, nullable=False, server_default="active")
    last_active_at: Mapped[datetime | None] = mapped_column(TIMESTAMPTZ)
    deleted_at: Mapped[datetime | None] = mapped_column(TIMESTAMPTZ)
    created_at: Mapped[datetime] = created_at_col()
    updated_at: Mapped[datetime] = updated_at_col()


class Profile(Base):
    __tablename__ = "profiles"
    __table_args__ = (
        CheckConstraint("current_year BETWEEN 1 AND 8", name="current_year_range"),
        CheckConstraint(
            "cgpa_scale IN (" + ", ".join(str(s) for s in CGPA_SCALES) + ")",
            name="cgpa_scale_values",
        ),
        CheckConstraint("cgpa IS NULL OR (cgpa >= 0 AND cgpa <= cgpa_scale)", name="cgpa_in_scale"),
        CheckConstraint(
            "target_package_lpa IS NULL OR target_package_lpa >= 0", name="package_non_negative"
        ),
        CheckConstraint(
            "daily_minutes IS NULL OR daily_minutes BETWEEN 15 AND 720", name="daily_minutes_range"
        ),
        CheckConstraint(
            "preferred_language IS NULL OR " + one_of("preferred_language", PREFERRED_LANGUAGES),
            name="preferred_language_values",
        ),
    )

    user_id: Mapped[uuid.UUID] = user_fk(primary_key=True)
    name: Mapped[str] = mapped_column(Text, nullable=False)
    college: Mapped[str | None] = mapped_column(Text)
    degree: Mapped[str | None] = mapped_column(Text)
    current_year: Mapped[int | None] = mapped_column(SmallInteger)
    cgpa: Mapped[Decimal | None] = mapped_column(Numeric(4, 2))
    cgpa_scale: Mapped[int] = mapped_column(SmallInteger, nullable=False, server_default="10")
    dream_company: Mapped[str | None] = mapped_column(Text)
    dream_role: Mapped[str | None] = mapped_column(Text)
    target_package_lpa: Mapped[Decimal | None] = mapped_column(Numeric(6, 2))
    github_username: Mapped[str | None] = mapped_column(Text)
    linkedin_url: Mapped[str | None] = mapped_column(Text)
    leetcode_username: Mapped[str | None] = mapped_column(Text)
    codeforces_username: Mapped[str | None] = mapped_column(Text)
    timezone: Mapped[str] = mapped_column(Text, nullable=False, server_default="UTC")
    daily_minutes: Mapped[int | None] = mapped_column(SmallInteger)
    preferred_language: Mapped[str | None] = mapped_column(Text)
    created_at: Mapped[datetime] = created_at_col()
    updated_at: Mapped[datetime] = updated_at_col()


class Skill(Base):
    """Skill catalogue. Phase 1 fills it from students' own profile entries."""

    __tablename__ = "skills"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    slug: Mapped[str] = mapped_column(Text, nullable=False, unique=True)
    name: Mapped[str] = mapped_column(Text, nullable=False)
    category: Mapped[str] = mapped_column(Text, nullable=False, server_default="user_defined")
    created_at: Mapped[datetime] = created_at_col()


class UserSkill(Base):
    __tablename__ = "user_skills"

    user_id: Mapped[uuid.UUID] = user_fk(primary_key=True)
    skill_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("skills.id", ondelete="CASCADE"), primary_key=True
    )
    created_at: Mapped[datetime] = created_at_col()
