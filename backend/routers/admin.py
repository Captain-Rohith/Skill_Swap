
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
    
    result = []
    for swap in swaps:
        from_user = db.query(User).filter(User.id == swap.from_user_id).first()
        to_user = db.query(User).filter(User.id == swap.to_user_id).first()
        
        result.append({
            "id": swap.id,
            "from_user_id": swap.from_user_id,
            "to_user_id": swap.to_user_id,
            "from_user_name": from_user.name if from_user else "Unknown",
            "to_user_name": to_user.name if to_user else "Unknown",
            "skill_offered": swap.skill_offered,
            "skill_wanted": swap.skill_wanted,
            "message": swap.message,
            "status": swap.status,
            "created_at": swap.created_at,
            "updated_at": swap.updated_at,
            "closed_count": swap.closed_count
        })
    
    return result

@router.post("/platform-message", response_model=dict)
def send_platform_message(
    message_data: dict,
    admin_user: User = Depends(verify_admin),
    db: Session = Depends(get_db)
):
    """Send a platform-wide message to all users"""
    from services.notification_service import NotificationService
    
    message = message_data.get("message", "").strip()
    if not message:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Message cannot be empty"
        )
    
    platform_message = NotificationService.send_platform_message(
        db, admin_user.id, admin_user.name, message
    )
    
    return {
        "id": platform_message.id,
        "message": platform_message.message,
        "admin_name": platform_message.admin_name,
        "created_at": platform_message.created_at.isoformat() if platform_message.created_at else None
    }
