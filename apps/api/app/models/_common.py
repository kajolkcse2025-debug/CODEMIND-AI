"""Column helpers shared by all models."""

import uuid
from collections.abc import Sequence
from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, func, text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

TIMESTAMPTZ = DateTime(timezone=True)


def uuid_pk() -> Mapped[uuid.UUID]:
    return mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        server_default=text("gen_random_uuid()"),
    )


def created_at_col() -> Mapped[datetime]:
    return mapped_column(TIMESTAMPTZ, nullable=False, server_default=func.now())


def updated_at_col() -> Mapped[datetime]:
    return mapped_column(
        TIMESTAMPTZ, nullable=False, server_default=func.now(), onupdate=func.now()
    )


def user_fk(*, primary_key: bool = False, index: bool = False) -> Mapped[uuid.UUID]:
    """Owner column. Deleting a user cascades to everything they own."""
    return mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        primary_key=primary_key,
        nullable=False,
        index=index,
    )


def one_of(column: str, values: Sequence[str]) -> str:
    """SQL for a CHECK constraint restricting ``column`` to ``values`` (text, not PG enums)."""
    quoted = ", ".join(f"'{value}'" for value in values)
    return f"{column} IN ({quoted})"
