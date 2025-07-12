
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from db.database import get_db
from utils.auth_utils import get_current_user_id, get_current_user, get_current_user_data
from services.user_service import UserService
from schemas.user import UserCreate, UserUpdate, UserResponse, UserPublicResponse
from models.user import User

router = APIRouter(prefix="/users", tags=["users"])

@router.get("/{user_id}/ratings", response_model=dict)
def get_user_ratings(
    user_id: str,
    db: Session = Depends(get_db)
):
    """Get user's ratings and feedback"""
    from services.swap_service import SwapService
    ratings = SwapService.get_user_ratings(db, user_id)
    return ratings

@router.post("/profile", response_model=UserResponse)
def create_or_update_profile(
    user_data: UserCreate,
    current_user_id: str = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """Create or update user profile"""
    existing_user = UserService.get_user_by_id(db, current_user_id)
    
    if existing_user:
        # Update existing user
        update_data = UserUpdate(**user_data.dict())
        user = UserService.update_user(db, current_user_id, update_data)
    else:
        # Create new user
        user = UserService.create_user(db, user_data, current_user_id)
    
    return user

@router.get("/profile", response_model=UserResponse)
def get_profile(current_user: User = Depends(get_current_user)):
    """Get current user's profile"""
    return current_user

@router.put("/profile", response_model=UserResponse)
def update_profile(
    user_data: UserUpdate,
    current_user_id: str = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """Update current user's profile"""
    print(f"Updating profile for user {current_user_id} with data: {user_data.dict()}")
    user = UserService.update_user(db, current_user_id, user_data)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    print(f"Updated user: {user.name}, skills_offered: {user.skills_offered}, skills_wanted: {user.skills_wanted}")
    return user

@router.get("/search", response_model=List[dict])
def search_users(
    skill: str | None = None,
    current_user_id: str = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """Search public users by skill or get all public users with ratings"""
    if skill:
        # For skill-based search, we'll need to implement a different approach
        # For now, get all users and filter by skill
        users = UserService.get_all_public_users_with_ratings(db, exclude_user_id=None)
        # Filter by skill
        filtered_users = []
        for user in users:
            if (skill.lower() in [s.lower() for s in user.get('skills_offered', [])] or
                skill.lower() in [s.lower() for s in user.get('skills_wanted', [])]):
                filtered_users.append(user)
        return filtered_users
    else:
        # Include all public users with ratings
        return UserService.get_all_public_users_with_ratings(db, exclude_user_id=None)

@router.get("/debug-token")
def debug_token(
    current_user_data: dict = Depends(get_current_user_data)
):
    """Debug endpoint to see what's in the JWT token"""
    return {
        "message": "JWT token data",
        "data": current_user_data
    }

@router.get("/debug-profile")
def debug_profile(
    current_user_id: str = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """Debug endpoint to see current user's profile data"""
    user = UserService.get_user_by_id(db, current_user_id)
    if not user:
        return {"error": "User not found"}
    
    return {
        "id": user.id,
        "name": user.name,
        "email": user.email,
        "phone_number": user.phone_number,
        "location": user.location,
        "skills_offered": user.skills_offered,
        "skills_wanted": user.skills_wanted,
        "availability": user.availability,
        "is_public": user.is_public,
        "is_active": user.is_active,
        "is_banned": user.is_banned,
        "created_at": user.created_at.isoformat() if user.created_at else None
    }

@router.post("/sync-from-clerk", response_model=UserResponse)
def sync_user_from_clerk(
    current_user_id: str = Depends(get_current_user_id),
    current_user_data: dict = Depends(get_current_user_data),
    db: Session = Depends(get_db)
):
    """Sync user data from Clerk profile"""
    if not current_user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid user ID"
        )
    
    print(f"Syncing user {current_user_id} with data: {current_user_data}")
    
    # Use the service method to sync user data from Clerk
    user = UserService.sync_user_from_clerk(db, current_user_data, current_user_id)
    
    return user
