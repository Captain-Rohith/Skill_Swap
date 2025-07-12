
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from db.database import get_db
from utils.auth_utils import get_current_user
from services.user_service import UserService
from schemas.user import UserResponse
from models.user import User

router = APIRouter(prefix="/admin", tags=["admin"])

def verify_admin(current_user: User = Depends(get_current_user)):
    """Verify current user is admin (placeholder - implement admin logic)"""
    # TODO: Implement proper admin verification logic
    # For now, we'll assume any authenticated user can access admin endpoints
    return current_user

@router.get("/users", response_model=List[UserResponse])
def get_all_users(
    db: Session = Depends(get_db),
    admin_user: User = Depends(verify_admin)
):
    """Get all users (admin only)"""
    users = UserService.get_all_users(db)
    return users

@router.patch("/users/{user_id}/ban", response_model=UserResponse)
def ban_user(
    user_id: str,
    db: Session = Depends(get_db),
    admin_user: User = Depends(verify_admin)
):
    """Ban a user (admin only)"""
    user = UserService.ban_user(db, user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    return user

@router.get("/swaps", response_model=List[dict])
def get_all_swaps(
    db: Session = Depends(get_db),
    admin_user: User = Depends(verify_admin)
):
    """Get all swap requests (admin only)"""
    from services.swap_service import SwapService
    swaps = SwapService.get_all_swaps(db)
    return swaps
