from pydantic import BaseModel, EmailStr, validator, ConfigDict
from typing import Optional, List
from datetime import datetime
from models import SkillType, SwapStatus

# Base schemas
class UserBase(BaseModel):
    name: str
    email: EmailStr
    location: Optional[str] = None
    profile_photo_url: Optional[str] = None
    availability: Optional[str] = None
    is_public: bool = True

class SkillBase(BaseModel):
    name: str
    category: Optional[str] = None

class UserSkillBase(BaseModel):
    skill_id: int
    skill_type: SkillType
    proficiency_level: Optional[str] = None

class SwapRequestBase(BaseModel):
    requested_user_id: int
    offered_skill_id: int
    requested_skill_id: int
    message: Optional[str] = None

class RatingBase(BaseModel):
    rating: int
    feedback: Optional[str] = None
    
    @validator('rating')
    def validate_rating(cls, v):
        if v < 1 or v > 5:
            raise ValueError('Rating must be between 1 and 5')
        return v

# Create schemas
class UserCreate(UserBase):
    pass

class SkillCreate(SkillBase):
    pass

class UserSkillCreate(UserSkillBase):
    pass

class SwapRequestCreate(SwapRequestBase):
    pass

class RatingCreate(RatingBase):
    swap_request_id: int
    rated_user_id: int

# Update schemas
class UserUpdate(BaseModel):
    name: Optional[str] = None
    location: Optional[str] = None
    profile_photo_url: Optional[str] = None
    availability: Optional[str] = None
    is_public: Optional[bool] = None

class SkillUpdate(BaseModel):
    name: Optional[str] = None
    category: Optional[str] = None

class UserSkillUpdate(BaseModel):
    proficiency_level: Optional[str] = None

class SwapRequestUpdate(BaseModel):
    message: Optional[str] = None

# Response schemas
class SkillResponse(SkillBase):
    id: int
    created_at: datetime
    
    class Config:
        orm_mode = True

class UserSkillResponse(UserSkillBase):
    id: int
    created_at: datetime
    skill: SkillResponse
    
    class Config:
        orm_mode = True

class UserResponse(UserBase):
    id: int
    is_banned: bool
    created_at: datetime
    updated_at: Optional[datetime] = None
    user_skills: List[UserSkillResponse] = []
    
    class Config:
        orm_mode = True

class SwapRequestResponse(SwapRequestBase):
    id: int
    requester_id: int
    status: SwapStatus
    created_at: datetime
    updated_at: Optional[datetime] = None
    requester: UserResponse
    requested_user: UserResponse
    offered_skill: SkillResponse
    requested_skill: SkillResponse
    
    class Config:
        orm_mode = True

class RatingResponse(RatingBase):
    id: int
    swap_request_id: int
    rater_id: int
    rated_user_id: int
    created_at: datetime
    
    class Config:
        orm_mode = True

# Search and filter schemas
class UserSearch(BaseModel):
    skill_name: Optional[str] = None
    location: Optional[str] = None
    availability: Optional[str] = None
    skill_type: Optional[SkillType] = None

class SkillSearch(BaseModel):
    name: Optional[str] = None
    category: Optional[str] = None

class SwapRequestFilter(BaseModel):
    status: Optional[SwapStatus] = None
    requester_id: Optional[int] = None
    requested_user_id: Optional[int] = None

# Admin schemas
class AdminUserResponse(UserResponse):
    pass

class AdminSwapRequestResponse(SwapRequestResponse):
    pass

class PlatformStats(BaseModel):
    total_users: int
    total_skills: int
    total_swaps: int
    completed_swaps: int
    pending_swaps: int
    average_rating: float

class BroadcastMessage(BaseModel):
    message: str
    title: Optional[str] = None

# API Response wrapper
class APIResponse(BaseModel):
    success: bool
    data: Optional[dict] = None
    message: str
    errors: List[str] = []
