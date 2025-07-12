
from sqlalchemy import Column, String, DateTime, Text, Enum, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
import enum
from db.database import Base

class SwapStatus(str, enum.Enum):
    PENDING = "pending"
    ACCEPTED = "accepted"
    REJECTED = "rejected"
    COMPLETED = "completed"

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
    rating = Column(String, nullable=False)  # 1-5 stars
    comment = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    swap_request = relationship("SwapRequest")
    from_user = relationship("User", foreign_keys=[from_user_id])
    to_user = relationship("User", foreign_keys=[to_user_id])
