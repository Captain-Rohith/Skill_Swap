from typing import Any, Dict, List, Optional
from fastapi import HTTPException
from sqlalchemy.orm import Session
from models import User, Skill, UserSkill, SwapRequest, Rating
from schemas import APIResponse

def create_api_response(
    success: bool = True,
    data: Optional[Any] = None,
    message: str = "Success",
    errors: List[str] = []
) -> Dict[str, Any]:
    """Create a standardized API response"""
    return {
        "success": success,
        "data": data,
        "message": message,
        "errors": errors
    }

def get_user_by_id(db: Session, user_id: int) -> User:
    """Get user by ID with error handling"""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user

def get_skill_by_id(db: Session, skill_id: int) -> Skill:
    """Get skill by ID with error handling"""
    skill = db.query(Skill).filter(Skill.id == skill_id).first()
    if not skill:
        raise HTTPException(status_code=404, detail="Skill not found")
    return skill

def get_swap_request_by_id(db: Session, swap_id: int) -> SwapRequest:
    """Get swap request by ID with error handling"""
    swap = db.query(SwapRequest).filter(SwapRequest.id == swap_id).first()
    if not swap:
        raise HTTPException(status_code=404, detail="Swap request not found")
    return swap

def get_user_skill_by_id(db: Session, user_skill_id: int) -> UserSkill:
    """Get user skill by ID with error handling"""
    user_skill = db.query(UserSkill).filter(UserSkill.id == user_skill_id).first()
    if not user_skill:
        raise HTTPException(status_code=404, detail="User skill not found")
    return user_skill

def check_user_permission(user_id: int, target_user_id: int) -> bool:
    """Check if user has permission to access/modify target user's data"""
    return user_id == target_user_id

def validate_swap_request(
    db: Session,
    requester_id: int,
    requested_user_id: int,
    offered_skill_id: int,
    requested_skill_id: int
) -> None:
    """Validate swap request parameters"""
    # Check if users exist
    requester = get_user_by_id(db, requester_id)
    requested_user = get_user_by_id(db, requested_user_id)
    
    # Check if users are not banned
    if requester.is_banned == True:
        raise HTTPException(status_code=400, detail="Requester is banned")
    if requested_user.is_banned == True:
        raise HTTPException(status_code=400, detail="Requested user is banned")
    
    # Check if users are not the same
    if requester_id == requested_user_id:
        raise HTTPException(status_code=400, detail="Cannot request swap with yourself")
    
    # Check if skills exist
    offered_skill = get_skill_by_id(db, offered_skill_id)
    requested_skill = get_skill_by_id(db, requested_skill_id)
    
    # Check if requester has the offered skill
    requester_has_offered = db.query(UserSkill).filter(
        UserSkill.user_id == requester_id,
        UserSkill.skill_id == offered_skill_id,
        UserSkill.skill_type == "offered"
    ).first()
    
    if not requester_has_offered:
        raise HTTPException(status_code=400, detail="You don't have the offered skill")
    
    # Check if requested user has the requested skill
    requested_user_has_skill = db.query(UserSkill).filter(
        UserSkill.user_id == requested_user_id,
        UserSkill.skill_id == requested_skill_id,
        UserSkill.skill_type == "offered"
    ).first()
    
    if not requested_user_has_skill:
        raise HTTPException(status_code=400, detail="Requested user doesn't have the requested skill")

def calculate_user_rating(db: Session, user_id: int) -> float:
    """Calculate average rating for a user"""
    ratings = db.query(Rating).filter(Rating.rated_user_id == user_id).all()
    if not ratings:
        return 0.0
    
    total_rating = sum(rating.rating for rating in ratings)
    return float(total_rating) / len(ratings)

def get_platform_stats(db: Session) -> Dict[str, Any]:
    """Get platform statistics"""
    total_users = db.query(User).count()
    total_skills = db.query(Skill).count()
    total_swaps = db.query(SwapRequest).count()
    completed_swaps = db.query(SwapRequest).filter(SwapRequest.status == "completed").count()
    pending_swaps = db.query(SwapRequest).filter(SwapRequest.status == "pending").count()
    
    # Calculate average rating
    all_ratings = db.query(Rating).all()
    average_rating = 0.0
    if all_ratings:
        total_rating = sum(rating.rating for rating in all_ratings)
        average_rating = float(total_rating) / len(all_ratings)
    
    return {
        "total_users": total_users,
        "total_skills": total_skills,
        "total_swaps": total_swaps,
        "completed_swaps": completed_swaps,
        "pending_swaps": pending_swaps,
        "average_rating": average_rating
    }
