
from sqlalchemy.orm import Session
from models.swap import SwapRequest, Feedback, SwapStatus
from models.user import User
from schemas.swap import SwapRequestCreate, FeedbackCreate
from typing import List, Optional
import uuid

class SwapService:
    @staticmethod
    def create_swap_request(
        db: Session, 
        swap_data: SwapRequestCreate, 
        from_user_id: str
    ) -> SwapRequest:
        """Create a new swap request"""
        # Get user names
        from_user = db.query(User).filter(User.id == from_user_id).first()
        to_user = db.query(User).filter(User.id == swap_data.to_user_id).first()
        
        if not from_user or not to_user:
            raise ValueError("User not found")
        
        swap_request = SwapRequest(
            id=str(uuid.uuid4()),
            from_user_id=from_user_id,
            to_user_id=swap_data.to_user_id,
            from_user_name=from_user.name,
            to_user_name=to_user.name,
            skill_offered=swap_data.skill_offered,
            skill_wanted=swap_data.skill_wanted,
            message=swap_data.message,
            status=SwapStatus.PENDING
        )
        
        db.add(swap_request)
        db.commit()
        db.refresh(swap_request)
        return swap_request

    @staticmethod
    def get_user_swaps(db: Session, user_id: str) -> List[SwapRequest]:
        """Get all swaps for a user (sent and received)"""
        return db.query(SwapRequest).filter(
            (SwapRequest.from_user_id == user_id) | 
            (SwapRequest.to_user_id == user_id)
        ).all()

    @staticmethod
    def get_all_swaps(db: Session) -> List[SwapRequest]:
        """Get all swap requests (admin only)"""
        return db.query(SwapRequest).all()

    @staticmethod
    def get_swap_by_id(db: Session, swap_id: str) -> Optional[SwapRequest]:
        """Get swap request by ID"""
        return db.query(SwapRequest).filter(SwapRequest.id == swap_id).first()

    @staticmethod
    def accept_swap(db: Session, swap_id: str, user_id: str) -> Optional[SwapRequest]:
        """Accept a swap request"""
        swap = db.query(SwapRequest).filter(
            SwapRequest.id == swap_id,
            SwapRequest.to_user_id == user_id
        ).first()
        
        if swap and swap.status == SwapStatus.PENDING:
            swap.status = SwapStatus.ACCEPTED
            db.commit()
            db.refresh(swap)
        
        return swap

    @staticmethod
    def reject_swap(db: Session, swap_id: str, user_id: str) -> Optional[SwapRequest]:
        """Reject a swap request"""
        swap = db.query(SwapRequest).filter(
            SwapRequest.id == swap_id,
            SwapRequest.to_user_id == user_id
        ).first()
        
        if swap and swap.status == SwapStatus.PENDING:
            swap.status = SwapStatus.REJECTED
            db.commit()
            db.refresh(swap)
        
        return swap

    @staticmethod
    def delete_swap(db: Session, swap_id: str, user_id: str) -> bool:
        """Delete a swap request (only by owner)"""
        swap = db.query(SwapRequest).filter(
            SwapRequest.id == swap_id,
            SwapRequest.from_user_id == user_id
        ).first()
        
        if swap:
            db.delete(swap)
            db.commit()
            return True
        
        return False

    @staticmethod
    def create_feedback(
        db: Session,
        swap_id: str,
        feedback_data: FeedbackCreate,
        from_user_id: str
    ) -> Optional[Feedback]:
        """Create feedback for a completed swap"""
        swap = db.query(SwapRequest).filter(SwapRequest.id == swap_id).first()
        if not swap or swap.status != SwapStatus.ACCEPTED:
            return None
        
        # Determine to_user_id based on who is giving feedback
        to_user_id = swap.to_user_id if from_user_id == swap.from_user_id else swap.from_user_id
        
        feedback = Feedback(
            id=str(uuid.uuid4()),
            swap_request_id=swap_id,
            from_user_id=from_user_id,
            to_user_id=to_user_id,
            rating=feedback_data.rating,
            comment=feedback_data.comment
        )
        
        db.add(feedback)
        db.commit()
        db.refresh(feedback)
        return feedback

    @staticmethod
    def get_swap_feedback(db: Session, swap_id: str) -> List[Feedback]:
        """Get all feedback for a swap"""
        return db.query(Feedback).filter(Feedback.swap_request_id == swap_id).all()
