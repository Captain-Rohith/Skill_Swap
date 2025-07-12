from pydantic import BaseModel, EmailStr, validator
from typing import Optional, List
from datetime import datetime
from models import SkillType, SwapStatus

# Base schemas
class BaseResponse(BaseModel):
    success: bool = True
    message: str = "Success"
    errors: List[str] = []

class UserBase(BaseModel):
    name: str
    email: EmailStr
    location: Optional[str] = None
    profile_photo_url: Optional[str] = None
    availability: Optional[str] = None
    is_public: bool = True

class UserCreate(UserBase):
    clerk_user_id: str

class UserUpdate(BaseModel):
    name: Optional[str] = None
    location: Optional[str] = None
    profile_photo_url: Optional[str] = None
    availability: Optional[str] = None
    is_public: Optional[bool] = None

class UserResponse(UserBase):
    clerk_user_id: str
    is_banned: bool
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True

class SkillBase(BaseModel):
    name: str
    category: Optional[str] = None

class SkillCreate(SkillBase):
    pass

class SkillResponse(SkillBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True

class UserSkillBase(BaseModel):
    skill_id: int
    skill_type: SkillType
    proficiency_level: Optional[str] = None

class UserSkillCreate(UserSkillBase):
    pass

class UserSkillResponse(UserSkillBase):
    id: int
    user_id: str
    created_at: datetime
    skill: SkillResponse

    class Config:
        from_attributes = True

class SwapRequestBase(BaseModel):
    requested_user_id: str
    offered_skill_id: int
    requested_skill_id: int
    message: Optional[str] = None

class SwapRequestCreate(SwapRequestBase):
    pass

class SwapRequestUpdate(BaseModel):
    message: Optional[str] = None

class SwapRequestResponse(SwapRequestBase):
    id: int
    requester_id: str
    status: SwapStatus
    created_at: datetime
    updated_at: Optional[datetime] = None
    requester: UserResponse
    requested_user: UserResponse
    offered_skill: SkillResponse
    requested_skill: SkillResponse

    class Config:
        from_attributes = True

class RatingBase(BaseModel):
    rating: int
    feedback: Optional[str] = None

    @validator('rating')
    def validate_rating(cls, v):
        if v < 1 or v > 5:
            raise ValueError('Rating must be between 1 and 5')
        return v

class RatingCreate(RatingBase):
    rated_user_id: str

class RatingResponse(RatingBase):
    id: int
    swap_request_id: int
    rater_id: str
    rated_user_id: str
    created_at: datetime

    class Config:
        from_attributes = True

# Search and filter schemas
class UserSearchParams(BaseModel):
    skill_name: Optional[str] = None
    location: Optional[str] = None
    availability: Optional[str] = None
    limit: int = 20
    offset: int = 0

class SkillSearchParams(BaseModel):
    name: Optional[str] = None
    category: Optional[str] = None
    limit: int = 50
    offset: int = 0

class SwapRequestFilterParams(BaseModel):
    status: Optional[SwapStatus] = None
    requester_id: Optional[str] = None
    requested_user_id: Optional[str] = None
    limit: int = 20
    offset: int = 0

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

# Response wrappers
class UserListResponse(BaseResponse):
    data: List[UserResponse]

class SkillListResponse(BaseResponse):
    data: List[SkillResponse]

class UserSkillListResponse(BaseResponse):
    data: List[UserSkillResponse]

class SwapRequestListResponse(BaseResponse):
    data: List[SwapRequestResponse]

class RatingListResponse(BaseResponse):
    data: List[RatingResponse]

class SingleUserResponse(BaseResponse):
    data: UserResponse

class SingleSkillResponse(BaseResponse):
    data: SkillResponse

class SingleSwapRequestResponse(BaseResponse):
    data: SwapRequestResponse

class SingleRatingResponse(BaseResponse):
    data: RatingResponse

class PlatformStatsResponse(BaseResponse):
    data: PlatformStats
