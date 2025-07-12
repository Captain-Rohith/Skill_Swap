from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import func, and_
from typing import List, Optional
from database import get_db
from models import User, SwapRequest, Rating, SwapStatus
from schemas import (
    AdminUserResponse, AdminSwapRequestResponse, PlatformStats,
    BroadcastMessage, UserListResponse, SwapRequestListResponse,
    PlatformStatsResponse, BaseResponse
)
from utils.auth import require_admin

router = APIRouter(prefix="/api/admin", tags=["admin"])

@router.get("/users", response_model=UserListResponse)
async def get_all_users(
    limit: int = Query(20, ge=1, le=100, description="Number of results to return"),
    offset: int = Query(0, ge=0, description="Number of results to skip"),
    is_banned: Optional[bool] = Query(None, description="Filter by ban status"),
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """Get all users with pagination (admin only)"""
    try:
        query = db.query(User)
        
        if is_banned is not None:
            query = query.filter(User.is_banned == is_banned)
        
        total = query.count()
        users = query.offset(offset).limit(limit).all()
        
        return UserListResponse(
            data=users,
            message=f"Found {len(users)} users"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve users"
        )

@router.put("/users/{user_id}/ban", response_model=BaseResponse)
async def ban_unban_user(
    user_id: str,
    ban: bool = Query(True, description="True to ban, False to unban"),
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """Ban or unban a user (admin only)"""
    try:
        # Prevent admin from banning themselves
        if user_id == current_user.clerk_user_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cannot ban yourself"
            )
        
        # Find the user
        user = db.query(User).filter(User.clerk_user_id == user_id).first()
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        # Update ban status
        user.is_banned = ban
        db.commit()
        
        action = "banned" if ban else "unbanned"
        return BaseResponse(
            message=f"User {action} successfully"
        )
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update user ban status"
        )

@router.get("/swaps", response_model=SwapRequestListResponse)
async def get_all_swaps(
    status: Optional[SwapStatus] = Query(None, description="Filter by status"),
    limit: int = Query(20, ge=1, le=100, description="Number of results to return"),
    offset: int = Query(0, ge=0, description="Number of results to skip"),
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """Get all swap requests with filters (admin only)"""
    try:
        query = db.query(SwapRequest)
        
        if status:
            query = query.filter(SwapRequest.status == status)
        
        total = query.count()
        swaps = query.offset(offset).limit(limit).all()
        
        return SwapRequestListResponse(
            data=swaps,
            message=f"Found {len(swaps)} swap requests"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve swap requests"
        )

@router.get("/reports", response_model=PlatformStatsResponse)
async def get_platform_statistics(
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """Get platform statistics (admin only)"""
    try:
        # Get total users
        total_users = db.query(User).count()
        
        # Get total skills
        total_skills = db.query(func.count()).select_from(User).join(User.user_skills).distinct().scalar()
        
        # Get total swaps
        total_swaps = db.query(SwapRequest).count()
        
        # Get completed swaps
        completed_swaps = db.query(SwapRequest).filter(SwapRequest.status == SwapStatus.COMPLETED).count()
        
        # Get pending swaps
        pending_swaps = db.query(SwapRequest).filter(SwapRequest.status == SwapStatus.PENDING).count()
        
        # Get average rating
        avg_rating_result = db.query(func.avg(Rating.rating)).scalar()
        average_rating = float(avg_rating_result) if avg_rating_result else 0.0
        
        stats = PlatformStats(
            total_users=total_users,
            total_skills=total_skills,
            total_swaps=total_swaps,
            completed_swaps=completed_swaps,
            pending_swaps=pending_swaps,
            average_rating=average_rating
        )
        
        return PlatformStatsResponse(
            data=stats,
            message="Platform statistics retrieved successfully"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve platform statistics"
        )

@router.post("/broadcast", response_model=BaseResponse)
async def send_broadcast_message(
    message_data: BroadcastMessage,
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """Send a platform-wide message (admin only)"""
    try:
        # This is a placeholder for the broadcast functionality
        # In a real implementation, you might:
        # - Store the message in a database
        # - Send push notifications
        # - Send emails
        # - Use WebSocket to broadcast to online users
        
        # For now, we'll just log the message
        print(f"BROADCAST MESSAGE from {current_user.name}:")
        print(f"Title: {message_data.title}")
        print(f"Message: {message_data.message}")
        
        return BaseResponse(
            message="Broadcast message sent successfully"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to send broadcast message"
        ) 