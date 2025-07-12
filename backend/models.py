from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text, ForeignKey, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from database import Base
import enum

class SkillType(str, enum.Enum):
    OFFERED = "offered"
    WANTED = "wanted"

class SwapStatus(str, enum.Enum):
    PENDING = "pending"
    ACCEPTED = "accepted"
    REJECTED = "rejected"
    COMPLETED = "completed"
    CANCELLED = "cancelled"

class User(Base):
    __tablename__ = "users"
    
    clerk_user_id = Column(String, primary_key=True, index=True)
    name = Column(String, nullable=False)
    email = Column(String, unique=True, nullable=False, index=True)
    location = Column(String, nullable=True)
    profile_photo_url = Column(String, nullable=True)
    availability = Column(String, nullable=True)
    is_public = Column(Boolean, default=True)
    is_banned = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    user_skills = relationship("UserSkill", back_populates="user", cascade="all, delete-orphan")
    sent_swap_requests = relationship("SwapRequest", foreign_keys="SwapRequest.requester_id", back_populates="requester")
    received_swap_requests = relationship("SwapRequest", foreign_keys="SwapRequest.requested_user_id", back_populates="requested_user")
    given_ratings = relationship("Rating", foreign_keys="Rating.rater_id", back_populates="rater")
    received_ratings = relationship("Rating", foreign_keys="Rating.rated_user_id", back_populates="rated_user")

class Skill(Base):
    __tablename__ = "skills"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, nullable=False, index=True)
    category = Column(String, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    user_skills = relationship("UserSkill", back_populates="skill", cascade="all, delete-orphan")
    offered_swap_requests = relationship("SwapRequest", foreign_keys="SwapRequest.offered_skill_id", back_populates="offered_skill")
    requested_swap_requests = relationship("SwapRequest", foreign_keys="SwapRequest.requested_skill_id", back_populates="requested_skill")

class UserSkill(Base):
    __tablename__ = "user_skills"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String, ForeignKey("users.clerk_user_id"), nullable=False)
    skill_id = Column(Integer, ForeignKey("skills.id"), nullable=False)
    skill_type = Column(Enum(SkillType), nullable=False)
    proficiency_level = Column(String, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    user = relationship("User", back_populates="user_skills")
    skill = relationship("Skill", back_populates="user_skills")

class SwapRequest(Base):
    __tablename__ = "swap_requests"
    
    id = Column(Integer, primary_key=True, index=True)
    requester_id = Column(String, ForeignKey("users.clerk_user_id"), nullable=False)
    requested_user_id = Column(String, ForeignKey("users.clerk_user_id"), nullable=False)
    offered_skill_id = Column(Integer, ForeignKey("skills.id"), nullable=False)
    requested_skill_id = Column(Integer, ForeignKey("skills.id"), nullable=False)
    status = Column(Enum(SwapStatus), default=SwapStatus.PENDING)
    message = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    requester = relationship("User", foreign_keys=[requester_id], back_populates="sent_swap_requests")
    requested_user = relationship("User", foreign_keys=[requested_user_id], back_populates="received_swap_requests")
    offered_skill = relationship("Skill", foreign_keys=[offered_skill_id], back_populates="offered_swap_requests")
    requested_skill = relationship("Skill", foreign_keys=[requested_skill_id], back_populates="requested_swap_requests")
    ratings = relationship("Rating", back_populates="swap_request", cascade="all, delete-orphan")

class Rating(Base):
    __tablename__ = "ratings"
    
    id = Column(Integer, primary_key=True, index=True)
    swap_request_id = Column(Integer, ForeignKey("swap_requests.id"), nullable=False)
    rater_id = Column(String, ForeignKey("users.clerk_user_id"), nullable=False)
    rated_user_id = Column(String, ForeignKey("users.clerk_user_id"), nullable=False)
    rating = Column(Integer, nullable=False)  # 1-5 scale
    feedback = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    swap_request = relationship("SwapRequest", back_populates="ratings")
    rater = relationship("User", foreign_keys=[rater_id], back_populates="given_ratings")
    rated_user = relationship("User", foreign_keys=[rated_user_id], back_populates="received_ratings") 