
from sqlalchemy.orm import Session
from models.swap import SwapRequest, Feedback, SwapStatus, ChatMessage
from models.user import User
from schemas.swap import SwapRequestCreate, FeedbackCreate, ChatMessageCreate
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
        
        # Create notification for the recipient
        from services.notification_service import NotificationService
        NotificationService.create_swap_request_notification(
            db, swap_data.to_user_id, from_user.name, 
            swap_data.skill_offered, swap_data.skill_wanted, swap_request.id
        )
        
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
            
            # Create notification for the sender
            from services.notification_service import NotificationService
            NotificationService.create_swap_response_notification(
                db, swap.from_user_id, swap.to_user_name, 'accepted', swap.id
            )
        
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
            
            # Create notification for the sender
            from services.notification_service import NotificationService
            NotificationService.create_swap_response_notification(
                db, swap.from_user_id, swap.to_user_name, 'rejected', swap.id
            )
        
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

    @staticmethod
    def close_swap(db: Session, swap_id: str, user_id: str) -> Optional[SwapRequest]:
        """Close a completed swap - increment counter, close when count reaches 2"""
        swap = db.query(SwapRequest).filter(
            SwapRequest.id == swap_id,
            (SwapRequest.from_user_id == user_id) | (SwapRequest.to_user_id == user_id),
            SwapRequest.status == SwapStatus.ACCEPTED
        ).first()
        
        if not swap:
            return None
        
        # Increment the closed count
        swap.closed_count += 1
        
        # If both users have closed (count reaches 2), mark as CLOSED
        if swap.closed_count >= 2:
            swap.status = SwapStatus.CLOSED
        
        db.commit()
        db.refresh(swap)
        return swap

    @staticmethod
    def get_user_ratings(db: Session, user_id: str) -> dict:
        """Get user's average rating and all feedback"""
        feedback = db.query(Feedback).filter(Feedback.to_user_id == user_id).all()
        
        if not feedback:
            return {
                "average_rating": 0.0,
                "total_ratings": 0,
                "feedback": []
            }
        
        # Ensure ratings are integers and handle any type issues
        ratings = []
        for f in feedback:
            try:
                rating = int(f.rating) if f.rating is not None else 0
                ratings.append(rating)
            except (ValueError, TypeError):
                # Skip invalid ratings
                continue
        
        if not ratings:
            return {
                "average_rating": 0.0,
                "total_ratings": 0,
                "feedback": []
            }
        
        total_rating = sum(ratings)
        average_rating = total_rating / len(ratings)
        
        # Convert feedback to serializable format
        feedback_list = []
        for fb in feedback:
            feedback_list.append({
                "id": fb.id,
                "rating": fb.rating,
                "comment": fb.comment,
                "from_user_id": fb.from_user_id,
                "created_at": fb.created_at.isoformat() if fb.created_at else None
            })
        
        return {
            "average_rating": round(average_rating, 1),
            "total_ratings": len(ratings),
            "feedback": feedback_list
        }

    @staticmethod
    def create_chat_message(
        db: Session,
        swap_id: str,
        message_data: ChatMessageCreate,
        from_user_id: str
    ) -> Optional[ChatMessage]:
        """Create a chat message for a swap"""
        # Verify user is part of this swap
        swap = db.query(SwapRequest).filter(SwapRequest.id == swap_id).first()
        if not swap or (swap.from_user_id != from_user_id and swap.to_user_id != from_user_id):
            return None
        
        chat_message = ChatMessage(
            id=str(uuid.uuid4()),
            swap_request_id=swap_id,
            from_user_id=from_user_id,
            message=message_data.message
        )
        
        db.add(chat_message)
        db.commit()
        db.refresh(chat_message)
        return chat_message

    @staticmethod
    def get_chat_messages(db: Session, swap_id: str, user_id: str) -> List[ChatMessage]:
        """Get chat messages for a swap"""
        # Verify user is part of this swap
        swap = db.query(SwapRequest).filter(SwapRequest.id == swap_id).first()
        if not swap or (swap.from_user_id != user_id and swap.to_user_id != user_id):
            return []
        
        return db.query(ChatMessage).filter(
            ChatMessage.swap_request_id == swap_id
        ).order_by(ChatMessage.created_at.asc()).all()

    @staticmethod
    def delete_swap_by_user(db: Session, swap_id: str, user_id: str) -> bool:
        """Delete a swap request (only by owner or if user is part of the swap)"""
        swap = db.query(SwapRequest).filter(
            SwapRequest.id == swap_id,
            (SwapRequest.from_user_id == user_id) | (SwapRequest.to_user_id == user_id)
        ).first()
        
        if swap:
            # Delete related records first (feedback and chat messages)
            db.query(Feedback).filter(Feedback.swap_request_id == swap_id).delete()
            db.query(ChatMessage).filter(ChatMessage.swap_request_id == swap_id).delete()
            
            # Now delete the swap request
            db.delete(swap)
            db.commit()
            return True
        
        return False


