
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from db.database import get_db
from utils.auth_utils import get_current_user_id, get_current_user, get_current_user_data
from services.user_service import UserService
from schemas.user import UserCreate, UserUpdate, UserResponse, UserPublicResponse
from models.user import User

router = APIRouter(prefix="/users", tags=["users"])

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

@router.get("/search", response_model=List[UserPublicResponse])
def search_users(
    skill: str = None,
    current_user_id: str = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """Search public users by skill or get all public users"""
    if skill:
        users = UserService.search_users_by_skill(db, skill)
    else:
        # Include all public users (including current user for testing)
        users = UserService.get_all_public_users(db, exclude_user_id=None)
    
    return [UserPublicResponse.from_orm(user) for user in users]

@router.get("/debug-token")
def debug_token(
    current_user_data: dict = Depends(get_current_user_data)
):
    """Debug endpoint to see what's in the JWT token"""
    return {
        "message": "JWT token data",
        "data": current_user_data
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
    
    # Get user data from the JWT token
    user = UserService.get_user_by_id(db, current_user_id)
    if not user:
        # Create user if they don't exist using data from JWT token
        # Extract name from token data
        first_name = current_user_data.get('first_name', '')
        last_name = current_user_data.get('last_name', '')
        full_name = current_user_data.get('full_name', '')
        
        # Determine the name to use
        if first_name and last_name:
            name = f"{first_name} {last_name}"
        elif first_name:
            name = first_name
        elif full_name:
            name = full_name
        else:
            name = current_user_data.get('username', 'User')
        
        # Extract email from token data
        email = ''
        if current_user_data.get('email_addresses'):
            email = current_user_data['email_addresses'][0].get('email_address', '')
        
        user_data = UserCreate(
            name=name,
            email=email or f"{current_user_id}@example.com",
            location="",
            skills_offered=[],
            skills_wanted=[],
            availability="",
            is_public=True
        )
        user = UserService.create_user(db, user_data, current_user_id)
        print(f"Created new user: {user.name} ({user.email})")
    else:
        # Update existing user with Clerk data if available
        print(f"Found existing user: {user.name} ({user.email})")
        
        # Only update if we have new data from Clerk
        if current_user_data.get('first_name') or current_user_data.get('last_name') or current_user_data.get('full_name'):
            first_name = current_user_data.get('first_name', '')
            last_name = current_user_data.get('last_name', '')
            full_name = current_user_data.get('full_name', '')
            
            # Determine the name to use
            if first_name and last_name:
                name = f"{first_name} {last_name}"
            elif first_name:
                name = first_name
            elif full_name:
                name = full_name
            else:
                name = current_user_data.get('username', user.name)
            
            # Extract email from token data
            email = ''
            if current_user_data.get('email_addresses'):
                email = current_user_data['email_addresses'][0].get('email_address', '')
            
            if name != user.name and user:
                update_data = UserUpdate(name=name)
                updated_user = UserService.update_user(db, current_user_id, update_data)
                if updated_user:
                    print(f"Updated user: {updated_user.name} ({updated_user.email})")
                    user = updated_user
    
    return user
