from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import or_, and_
from typing import List, Optional
from database import get_db
from models import User, UserSkill, Skill
from schemas import (
    UserCreate, UserUpdate, UserResponse, UserSearchParams,
    UserListResponse, SingleUserResponse, BaseResponse
)
from utils.auth import get_current_user, get_current_user_optional

router = APIRouter(prefix="/api/users", tags=["users"])

@router.post("/", response_model=SingleUserResponse, status_code=status.HTTP_201_CREATED)
async def create_user(
    user_data: UserCreate,
    db: Session = Depends(get_db)
):
    """Create a new user profile"""
    try:
        # Check if user already exists
        existing_user = db.query(User).filter(User.clerk_user_id == user_data.clerk_user_id).first()
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="User already exists"
            )
        
        # Check if email is already taken
        existing_email = db.query(User).filter(User.email == user_data.email).first()
        if existing_email:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered"
            )
        
        # Create new user
        db_user = User(**user_data.dict())
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
        
        return SingleUserResponse(
            data=db_user,
            message="User created successfully"
        )
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create user"
        )

@router.get("/me", response_model=SingleUserResponse)
async def get_current_user_profile(
    current_user: User = Depends(get_current_user)
):
    """Get current user's profile"""
    return SingleUserResponse(
        data=current_user,
        message="User profile retrieved successfully"
    )

@router.put("/me", response_model=SingleUserResponse)
async def update_user_profile(
    user_data: UserUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update current user's profile"""
    try:
        # Update only provided fields
        update_data = user_data.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(current_user, field, value)
        
        db.commit()
        db.refresh(current_user)
        
        return SingleUserResponse(
            data=current_user,
            message="User profile updated successfully"
        )
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update user profile"
        )

@router.get("/search", response_model=UserListResponse)
async def search_users(
    skill_name: Optional[str] = Query(None, description="Filter by skill name"),
    location: Optional[str] = Query(None, description="Filter by location"),
    availability: Optional[str] = Query(None, description="Filter by availability"),
    limit: int = Query(20, ge=1, le=100, description="Number of results to return"),
    offset: int = Query(0, ge=0, description="Number of results to skip"),
    current_user: Optional[User] = Depends(get_current_user_optional),
    db: Session = Depends(get_db)
):
    """Search users by various criteria"""
    try:
        query = db.query(User).filter(User.is_public == True, User.is_banned == False)
        
        # Filter by location
        if location:
            query = query.filter(User.location.ilike(f"%{location}%"))
        
        # Filter by availability
        if availability:
            query = query.filter(User.availability.ilike(f"%{availability}%"))
        
        # Filter by skill name
        if skill_name:
            query = query.join(UserSkill).join(Skill).filter(
                Skill.name.ilike(f"%{skill_name}%")
            )
        
        # Apply pagination
        total = query.count()
        users = query.offset(offset).limit(limit).all()
        
        return UserListResponse(
            data=users,
            message=f"Found {len(users)} users",
            errors=[]
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to search users"
        )

@router.get("/{user_id}", response_model=SingleUserResponse)
async def get_user_profile(
    user_id: str,
    current_user: Optional[User] = Depends(get_current_user_optional),
    db: Session = Depends(get_db)
):
    """Get a specific user's profile"""
    try:
        user = db.query(User).filter(User.clerk_user_id == user_id).first()
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        # Check if user is public or if current user is requesting their own profile
        if not user.is_public and (not current_user or current_user.clerk_user_id != user_id):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="User profile is private"
            )
        
        # Check if user is banned
        if user.is_banned:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        return SingleUserResponse(
            data=user,
            message="User profile retrieved successfully"
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve user profile"
        ) 