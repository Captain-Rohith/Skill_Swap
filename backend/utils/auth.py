from fastapi import HTTPException, Depends, status, Header
from sqlalchemy.orm import Session
from typing import Optional
from database import get_db
from models import User

async def get_current_user(
    user_id: str = Header(..., alias="X-User-ID"),
    db: Session = Depends(get_db)
) -> User:
    """
    Get current user from database based on user ID passed from frontend
    """
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User ID header is required"
        )
    
    user = db.query(User).filter(User.clerk_user_id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    if user.is_banned == True:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account is banned"
        )
    
    return user

async def get_current_user_optional(
    user_id: Optional[str] = Header(None, alias="X-User-ID"),
    db: Session = Depends(get_db)
) -> Optional[User]:
    """
    Get current user if user ID is provided, otherwise return None
    """
    if not user_id:
        return None
    
    user = db.query(User).filter(User.clerk_user_id == user_id).first()
    if user and user.is_banned == False:
        return user
    return None

def require_admin(user: User = Depends(get_current_user)) -> User:
    """
    Require admin privileges (placeholder for future admin system)
    """
    # For now, we'll implement a simple admin check
    # In production, you might want to add an admin field to the User model
    import os
    admin_user_ids = os.getenv("ADMIN_USER_IDS", "").split(",")
    if user.clerk_user_id not in admin_user_ids:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin privileges required"
        )
    return user 