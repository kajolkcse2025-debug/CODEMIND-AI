import uuid
from datetime import datetime

from sqlalchemy import CheckConstraint, Index, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import CheckConstraint, ForeignKey, Index, Text

from app.db.base import Base
from app.models._common import TIMESTAMPTZ, created_at_col, one_of, user_fk, uuid_pk

CONVERSATION_KINDS = ("coach", "teacher", "interview", "mentor")


class AiConversation(Base):
    __tablename__ = "ai_conversations"
    __table_args__ = (
        CheckConstraint(one_of("kind", CONVERSATION_KINDS), name="kind_values"),
        Index("ix_ai_conversations_user_created", "user_id", "created_at"),
    )

    id: Mapped[uuid.UUID] = uuid_pk()
    user_id: Mapped[uuid.UUID] = user_fk()
    kind: Mapped[str] = mapped_column(Text, nullable=False)
    context_ref_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True))
    created_at: Mapped[datetime] = created_at_col()
    retention_expires_at: Mapped[datetime | None] = mapped_column(TIMESTAMPTZ)
class AiMessage(Base):
    __tablename__ = "ai_messages"
    __table_args__ = (
        CheckConstraint(
            "role IN ('user', 'assistant')",
            name="role_values",
        ),
        Index("ix_ai_messages_conversation_created", "conversation_id", "created_at"),
    )

    id: Mapped[uuid.UUID] = uuid_pk()
    conversation_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("ai_conversations.id", ondelete="CASCADE"),
        nullable=False,
    )
    role: Mapped[str] = mapped_column(Text, nullable=False)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    created_at: Mapped[datetime] = created_at_col()
