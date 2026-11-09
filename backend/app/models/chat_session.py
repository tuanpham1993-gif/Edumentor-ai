import uuid

from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, CheckConstraint, true
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func

from app.core.database import Base


class ChatSession(Base):
    __tablename__ = "chat_session"

    session_id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )   
    user_id = Column(
        Integer,
        ForeignKey("users.user_id", ondelete="CASCADE"),
        nullable=true,
    )
    session_type = Column(
        String(15),
        nullable=False,
        default="tutor",
        server_default="tutor",
    )
    topic = Column(String(255), nullable=True)
    status = Column(
        String(10),
        nullable=False,
        default="active",
        server_default="active",
    )
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(
        DateTime,
        server_default=func.now(),
        onupdate=func.now(),
    )

    __table_args__ = (
        CheckConstraint(
            "session_type IN ('tutor', 'learning_path')",
            name="ck_chat_session_type",
        ),
        CheckConstraint(
            "status IN ('active', 'archived')",
            name="ck_chat_session_status",
        ),
    )