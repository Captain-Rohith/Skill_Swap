
from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from models.swap import SwapStatus

class SwapRequestBase(BaseModel):
    to_user_id: str
    skill_offered: str
    skill_wanted: str
    message: Optional[str] = None

class SwapRequestCreate(SwapRequestBase):
    pass

class SwapRequestResponse(BaseModel):
    id: str
    from_user_id: str
    to_user_id: str
    from_user_name: str
    to_user_name: str
    skill_offered: str
    skill_wanted: str
    message: Optional[str] = None
    status: SwapStatus
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True

class FeedbackBase(BaseModel):
    rating: int
    comment: Optional[str] = None

class FeedbackCreate(FeedbackBase):
    pass

class FeedbackResponse(BaseModel):
    id: str
    swap_request_id: str
    from_user_id: str
    to_user_id: str
    rating: int
    comment: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True
