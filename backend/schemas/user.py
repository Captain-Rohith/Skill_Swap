
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

class UserBase(BaseModel):
    name: str
    email: str
    location: Optional[str] = None
    profile_picture: Optional[str] = None
    skills_offered: List[str] = []
    skills_wanted: List[str] = []
    availability: Optional[str] = None
    is_public: bool = True

class UserCreate(UserBase):
    pass

class UserUpdate(BaseModel):
    name: Optional[str] = None
    location: Optional[str] = None
    profile_picture: Optional[str] = None
    skills_offered: Optional[List[str]] = None
    skills_wanted: Optional[List[str]] = None
    availability: Optional[str] = None
    is_public: Optional[bool] = None

class UserResponse(UserBase):
    id: str
    is_active: bool
    is_banned: bool
    created_at: datetime

    class Config:
        from_attributes = True

class UserPublicResponse(BaseModel):
    id: str
    name: str
    location: Optional[str] = None
    profile_picture: Optional[str] = None
    skills_offered: List[str] = []
    skills_wanted: List[str] = []
    availability: Optional[str] = None

    class Config:
        from_attributes = True
