from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, func

from app.core.database import Base

class PasswordResetToken(Base):
    __tablename__ = "password_reset_tokens"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(                                                    # TODO 74
        Integer, ForeignKey("users.user_id", ondelete="CASCADE"), nullable=False, index=True
    )
    token_hash = Column(String(64), unique=True, nullable=False, index=True)  # TODO 75
    expires_at = Column(DateTime(timezone=True), nullable=False)        # TODO 76
    used_at = Column(DateTime(timezone=True), nullable=True)            # TODO 77
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)