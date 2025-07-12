from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import or_, and_
from typing import List, Optional
from database import get_db
from models import User, UserSkill, Skill, SwapRequest, Rating, SwapStatus, SkillType
from schemas import (
    SwapRequestCreate, SwapRequestResponse, RatingCreate, RatingResponse,
    SwapRequestFilterParams, SwapRequestListResponse, SingleSwapRequestResponse,
    SingleRatingResponse, BaseResponse
)
from utils.auth import get_current_user

router = APIRouter(prefix="/api/swaps", tags=["swaps"])

@router.post("/", response_model=SingleSwapRequestResponse, status_code=status.HTTP_201_CREATED)
async def create_swap_request(
    swap_data: SwapRequestCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create a new swap request"""
    try:
        # Validate that requested user exists and is not banned
        requested_user = db.query(User).filter(
            User.clerk_user_id == swap_data.requested_user_id,
            User.is_banned == False
        ).first()
        if not requested_user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Requested user not found or is banned"
            )
        
        # Validate that requester has the offered skill
        offered_skill_check = db.query(UserSkill).filter(
            UserSkill.user_id == current_user.clerk_user_id,
            UserSkill.skill_id == swap_data.offered_skill_id,
            UserSkill.skill_type == SkillType.OFFERED
        ).first()
        if not offered_skill_check:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="You don't have the offered skill or it's not marked as offered"
            )
        
        # Validate that requested user has the requested skill
        requested_skill_check = db.query(UserSkill).filter(
            UserSkill.user_id == swap_data.requested_user_id,
            UserSkill.skill_id == swap_data.requested_skill_id,
            UserSkill.skill_type == SkillType.OFFERED
        ).first()
        if not requested_skill_check:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Requested user doesn't have the requested skill or it's not marked as offered"
            )
        
        # Check if there's already a pending swap between these users for these skills
        existing_swap = db.query(SwapRequest).filter(
            SwapRequest.requester_id == current_user.clerk_user_id,
            SwapRequest.requested_user_id == swap_data.requested_user_id,
            SwapRequest.offered_skill_id == swap_data.offered_skill_id,
            SwapRequest.requested_skill_id == swap_data.requested_skill_id,
            SwapRequest.status == SwapStatus.PENDING
        ).first()
        if existing_swap:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="A pending swap request already exists for these skills"
            )
        
        # Create swap request
        db_swap = SwapRequest(
            requester_id=current_user.clerk_user_id,
            **swap_data.dict()
        )
        db.add(db_swap)
        db.commit()
        db.refresh(db_swap)
        
        return SingleSwapRequestResponse(
            data=db_swap,
            message="Swap request created successfully"
        )
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create swap request"
        )

@router.get("/", response_model=SwapRequestListResponse)
async def get_swap_requests(
    status: Optional[SwapStatus] = Query(None, description="Filter by status"),
    limit: int = Query(20, ge=1, le=100, description="Number of results to return"),
    offset: int = Query(0, ge=0, description="Number of results to skip"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get user's swap requests (sent and received)"""
    try:
        query = db.query(SwapRequest).filter(
            or_(
                SwapRequest.requester_id == current_user.clerk_user_id,
                SwapRequest.requested_user_id == current_user.clerk_user_id
            )
        )
        
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

@router.put("/{swap_id}/accept", response_model=SingleSwapRequestResponse)
async def accept_swap_request(
    swap_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Accept a swap request"""
    try:
        # Find the swap request
        swap = db.query(SwapRequest).filter(
            SwapRequest.id == swap_id,
            SwapRequest.requested_user_id == current_user.clerk_user_id,
            SwapRequest.status == SwapStatus.PENDING
        ).first()
        
        if not swap:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Swap request not found or cannot be accepted"
            )
        
        # Update status to accepted
        swap.status = SwapStatus.ACCEPTED
        db.commit()
        db.refresh(swap)
        
        return SingleSwapRequestResponse(
            data=swap,
            message="Swap request accepted successfully"
        )
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to accept swap request"
        )

@router.put("/{swap_id}/reject", response_model=SingleSwapRequestResponse)
async def reject_swap_request(
    swap_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Reject a swap request"""
    try:
        # Find the swap request
        swap = db.query(SwapRequest).filter(
            SwapRequest.id == swap_id,
            SwapRequest.requested_user_id == current_user.clerk_user_id,
            SwapRequest.status == SwapStatus.PENDING
        ).first()
        
        if not swap:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Swap request not found or cannot be rejected"
            )
        
        # Update status to rejected
        swap.status = SwapStatus.REJECTED
        db.commit()
        db.refresh(swap)
        
        return SingleSwapRequestResponse(
            data=swap,
            message="Swap request rejected successfully"
        )
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to reject swap request"
        )

@router.put("/{swap_id}/complete", response_model=SingleSwapRequestResponse)
async def complete_swap_request(
    swap_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Mark a swap as completed"""
    try:
        # Find the swap request
        swap = db.query(SwapRequest).filter(
            SwapRequest.id == swap_id,
            or_(
                SwapRequest.requester_id == current_user.clerk_user_id,
                SwapRequest.requested_user_id == current_user.clerk_user_id
            ),
            SwapRequest.status == SwapStatus.ACCEPTED
        ).first()
        
        if not swap:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Swap request not found or cannot be completed"
            )
        
        # Update status to completed
        swap.status = SwapStatus.COMPLETED
        db.commit()
        db.refresh(swap)
        
        return SingleSwapRequestResponse(
            data=swap,
            message="Swap marked as completed successfully"
        )
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to complete swap request"
        )

@router.delete("/{swap_id}", response_model=BaseResponse)
async def cancel_swap_request(
    swap_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Cancel/delete a swap request"""
    try:
        # Find the swap request
        swap = db.query(SwapRequest).filter(
            SwapRequest.id == swap_id,
            SwapRequest.requester_id == current_user.clerk_user_id,
            SwapRequest.status == SwapStatus.PENDING
        ).first()
        
        if not swap:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Swap request not found or cannot be cancelled"
            )
        
        # Delete the swap request
        db.delete(swap)
        db.commit()
        
        return BaseResponse(
            message="Swap request cancelled successfully"
        )
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to cancel swap request"
        )

@router.post("/{swap_id}/rate", response_model=SingleRatingResponse, status_code=status.HTTP_201_CREATED)
async def rate_completed_swap(
    swap_id: int,
    rating_data: RatingCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Rate a completed swap"""
    try:
        # Find the completed swap request
        swap = db.query(SwapRequest).filter(
            SwapRequest.id == swap_id,
            SwapRequest.status == SwapStatus.COMPLETED
        ).first()
        
        if not swap:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Completed swap request not found"
            )
        
        # Verify current user is part of the swap
        if current_user.clerk_user_id not in [swap.requester_id, swap.requested_user_id]:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You can only rate swaps you participated in"
            )
        
        # Verify the rated user is the other participant
        other_user_id = swap.requested_user_id if current_user.clerk_user_id == swap.requester_id else swap.requester_id
        if rating_data.rated_user_id != other_user_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="You can only rate the other participant in the swap"
            )
        
        # Check if user already rated this swap
        existing_rating = db.query(Rating).filter(
            Rating.swap_request_id == swap_id,
            Rating.rater_id == current_user.clerk_user_id
        ).first()
        
        if existing_rating:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="You have already rated this swap"
            )
        
        # Create rating
        db_rating = Rating(
            swap_request_id=swap_id,
            rater_id=current_user.clerk_user_id,
            **rating_data.dict()
        )
        db.add(db_rating)
        db.commit()
        db.refresh(db_rating)
        
        return SingleRatingResponse(
            data=db_rating,
            message="Rating submitted successfully"
        )
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to submit rating"
        ) 