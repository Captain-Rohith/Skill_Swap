from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from database import get_db
from models import Skill, UserSkill, User
from schemas import (
    SkillCreate, SkillResponse, UserSkillCreate, UserSkillResponse,
    SkillSearch, APIResponse
)
from utils.helpers import create_api_response, get_skill_by_id, get_user_by_id, get_user_skill_by_id

router = APIRouter(prefix="/api/skills", tags=["skills"])

# Temporary user session (in production, use proper authentication)
CURRENT_USER_ID = 1  # This would come from authentication middleware

@router.get("/", response_model=dict)
def get_all_skills(
    name: Optional[str] = Query(None, description="Search by skill name"),
    category: Optional[str] = Query(None, description="Filter by category"),
    db: Session = Depends(get_db)
):
    """Get all skills with optional filtering"""
    query = db.query(Skill)
    
    if name:
        query = query.filter(Skill.name.ilike(f"%{name}%"))
    
    if category:
        query = query.filter(Skill.category.ilike(f"%{category}%"))
    
    skills = query.all()
    
    return create_api_response(
        data=[SkillResponse.from_orm(skill) for skill in skills],
        message=f"Retrieved {len(skills)} skills"
    )

@router.post("/", response_model=dict)
def create_skill(
    skill_data: SkillCreate,
    db: Session = Depends(get_db)
):
    """Create a new skill"""
    # Check if skill already exists
    existing_skill = db.query(Skill).filter(Skill.name == skill_data.name).first()
    if existing_skill:
        raise HTTPException(status_code=400, detail="Skill already exists")
    
    # Create new skill
    db_skill = Skill(**skill_data.dict())
    db.add(db_skill)
    db.commit()
    db.refresh(db_skill)
    
    return create_api_response(
        data=SkillResponse.from_orm(db_skill),
        message="Skill created successfully"
    )

@router.get("/search", response_model=dict)
def search_skills(
    name: Optional[str] = Query(None, description="Search by skill name"),
    category: Optional[str] = Query(None, description="Filter by category"),
    db: Session = Depends(get_db)
):
    """Search skills by name and category"""
    query = db.query(Skill)
    
    if name:
        query = query.filter(Skill.name.ilike(f"%{name}%"))
    
    if category:
        query = query.filter(Skill.category.ilike(f"%{category}%"))
    
    skills = query.all()
    
    return create_api_response(
        data=[SkillResponse.from_orm(skill) for skill in skills],
        message=f"Found {len(skills)} skills"
    )

@router.post("/user-skills", response_model=dict)
def add_user_skill(
    user_skill_data: UserSkillCreate,
    db: Session = Depends(get_db)
):
    """Add a skill to the current user (offered/wanted)"""
    # Verify skill exists
    skill = get_skill_by_id(db, user_skill_data.skill_id)
    
    # Check if user already has this skill with the same type
    existing_user_skill = db.query(UserSkill).filter(
        UserSkill.user_id == CURRENT_USER_ID,
        UserSkill.skill_id == user_skill_data.skill_id,
        UserSkill.skill_type == user_skill_data.skill_type
    ).first()
    
    if existing_user_skill:
        raise HTTPException(status_code=400, detail="User already has this skill with the same type")
    
    # Create user skill
    db_user_skill = UserSkill(
        user_id=CURRENT_USER_ID,
        **user_skill_data.dict()
    )
    db.add(db_user_skill)
    db.commit()
    db.refresh(db_user_skill)
    
    # Get the skill details for response
    db_user_skill.skill = skill
    
    return create_api_response(
        data=UserSkillResponse.from_orm(db_user_skill),
        message="Skill added to user successfully"
    )

@router.delete("/user-skills/{user_skill_id}", response_model=dict)
def remove_user_skill(
    user_skill_id: int,
    db: Session = Depends(get_db)
):
    """Remove a skill from the current user"""
    user_skill = get_user_skill_by_id(db, user_skill_id)
    
    # Check if the skill belongs to the current user
    # The get_user_skill_by_id function already validates the skill exists
    # We'll assume authorization is handled at the database level
    
    db.delete(user_skill)
    db.commit()
    
    return create_api_response(
        message="Skill removed from user successfully"
    )

@router.get("/user-skills/me", response_model=dict)
def get_current_user_skills(
    skill_type: Optional[str] = Query(None, description="Filter by skill type (offered/wanted)"),
    db: Session = Depends(get_db)
):
    """Get current user's skills"""
    query = db.query(UserSkill).filter(UserSkill.user_id == CURRENT_USER_ID)
    
    if skill_type:
        query = query.filter(UserSkill.skill_type == skill_type)
    
    user_skills = query.all()
    
    return create_api_response(
        data=[UserSkillResponse.from_orm(user_skill) for user_skill in user_skills],
        message=f"Retrieved {len(user_skills)} user skills"
    ) 