
from sqlalchemy import Column, String, Boolean, DateTime, Text, ARRAY
from sqlalchemy.sql import func
from db.database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(String, primary_key=True, index=True)  # Clerk user ID
    name = Column(String, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    location = Column(String, nullable=True)
    profile_picture = Column(String, nullable=True)
    skills_offered = Column(ARRAY(String), default=[])
    skills_wanted = Column(ARRAY(String), default=[])
    availability = Column(String, nullable=True)
    is_public = Column(Boolean, default=True)
    is_active = Column(Boolean, default=True)
    is_banned = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
