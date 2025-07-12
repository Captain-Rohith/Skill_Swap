
from sqlalchemy import Column, String, DateTime, Text, Enum, ForeignKey, Integer, Boolean
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
import enum
from db.database import Base

class SwapStatus(str, enum.Enum):
    PENDING = "pending"
    ACCEPTED = "accepted"
    REJECTED = "rejected"
    COMPLETED = "completed"
    CLOSED = "closed"

class SwapRequest(Base):
    __tablename__ = "swap_requests"

    id = Column(String, primary_key=True, index=True)
    from_user_id = Column(String, ForeignKey("users.id"), nullable=False)
    to_user_id = Column(String, ForeignKey("users.id"), nullable=False)
    from_user_name = Column(String, nullable=False)
    to_user_name = Column(String, nullable=False)
    skill_offered = Column(String, nullable=False)
    skill_wanted = Column(String, nullable=False)
    message = Column(Text, nullable=True)
    status = Column(Enum(SwapStatus), default=SwapStatus.PENDING)
    closed_count = Column(Integer, default=0)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    from_user = relationship("User", foreign_keys=[from_user_id])
    to_user = relationship("User", foreign_keys=[to_user_id])

class Feedback(Base):
    __tablename__ = "feedback"

    id = Column(String, primary_key=True, index=True)
    swap_request_id = Column(String, ForeignKey("swap_requests.id"), nullable=False)
    from_user_id = Column(String, ForeignKey("users.id"), nullable=False)
    to_user_id = Column(String, ForeignKey("users.id"), nullable=False)
    rating = Column(Integer, nullable=False)  # 1-5 stars
    comment = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    swap_request = relationship("SwapRequest")
    from_user = relationship("User", foreign_keys=[from_user_id])
    to_user = relationship("User", foreign_keys=[to_user_id])

class ChatMessage(Base):
    __tablename__ = "chat_messages"

    id = Column(String, primary_key=True, index=True)
    swap_request_id = Column(String, ForeignKey("swap_requests.id"), nullable=False)
    from_user_id = Column(String, ForeignKey("users.id"), nullable=False)
    message = Column(Text, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    swap_request = relationship("SwapRequest")
    from_user = relationship("User", foreign_keys=[from_user_id])

class Notification(Base):
    __tablename__ = "notifications"

    id = Column(String, primary_key=True, index=True)
    user_id = Column(String, ForeignKey("users.id"), nullable=False)
    type = Column(String, nullable=False)  # 'swap_request', 'platform_message', 'swap_accepted', 'swap_rejected'
    title = Column(String, nullable=False)
    message = Column(Text, nullable=False)
    related_id = Column(String, nullable=True)  # swap request id, etc.
    is_read = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    user = relationship("User", foreign_keys=[user_id])

class PlatformMessage(Base):
    __tablename__ = "platform_messages"

    id = Column(String, primary_key=True, index=True)
    message = Column(Text, nullable=False)
    admin_id = Column(String, ForeignKey("users.id"), nullable=False)
    admin_name = Column(String, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    admin = relationship("User", foreign_keys=[admin_id])
