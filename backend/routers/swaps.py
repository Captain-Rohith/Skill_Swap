
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from db.database import get_db
from utils.auth_utils import get_current_user_id
from services.swap_service import SwapService
from schemas.swap import SwapRequestCreate, SwapRequestResponse, FeedbackCreate, FeedbackResponse

router = APIRouter(prefix="/swaps", tags=["swaps"])

@router.post("/request", response_model=SwapRequestResponse)
def create_swap_request(
    swap_data: SwapRequestCreate,
    current_user_id: str = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """Create a new swap request"""
    try:
        swap = SwapService.create_swap_request(db, swap_data, current_user_id)
        return swap
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

@router.get("/", response_model=List[SwapRequestResponse])
def get_user_swaps(
    current_user_id: str = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """Get all swaps for current user"""
    swaps = SwapService.get_user_swaps(db, current_user_id)
    return swaps

@router.patch("/{swap_id}/accept", response_model=SwapRequestResponse)
def accept_swap(
    swap_id: str,
    current_user_id: str = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """Accept a swap request"""
    swap = SwapService.accept_swap(db, swap_id, current_user_id)
    if not swap:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Swap request not found or not authorized"
        )
    return swap

@router.patch("/{swap_id}/reject", response_model=SwapRequestResponse)
def reject_swap(
    swap_id: str,
    current_user_id: str = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """Reject a swap request"""
    swap = SwapService.reject_swap(db, swap_id, current_user_id)
    if not swap:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Swap request not found or not authorized"
        )
    return swap

@router.delete("/{swap_id}")
def delete_swap(
    swap_id: str,
    current_user_id: str = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """Delete a swap request (only by owner)"""
    success = SwapService.delete_swap(db, swap_id, current_user_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Swap request not found or not authorized"
        )
    return {"message": "Swap request deleted successfully"}

@router.post("/{swap_id}/feedback", response_model=FeedbackResponse)
def create_feedback(
    swap_id: str,
    feedback_data: FeedbackCreate,
    current_user_id: str = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """Submit feedback for a swap"""
    feedback = SwapService.create_feedback(db, swap_id, feedback_data, current_user_id)
    if not feedback:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot create feedback for this swap"
        )
    return feedback

@router.get("/{swap_id}/feedback", response_model=List[FeedbackResponse])
def get_swap_feedback(
    swap_id: str,
    current_user_id: str = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """Get feedback for a swap"""
    # Verify user is part of this swap
    swap = SwapService.get_swap_by_id(db, swap_id)
    if not swap or (swap.from_user_id != current_user_id and swap.to_user_id != current_user_id):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Swap not found or not authorized"
        )
    
    feedback = SwapService.get_swap_feedback(db, swap_id)
    return feedback
