from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import or_, and_
from typing import List, Optional
from database import get_db
from models import User, UserSkill, Skill, SkillType
from schemas import (
    SkillCreate, SkillResponse, UserSkillCreate, UserSkillResponse,
    SkillSearchParams, SkillListResponse, UserSkillListResponse,
    SingleSkillResponse, SingleUserSkillResponse, BaseResponse
)
from utils.auth import get_current_user, require_admin

router = APIRouter(prefix="/api/skills", tags=["skills"])

@router.get("/", response_model=SkillListResponse)
async def get_all_skills(
    name: Optional[str] = Query(None, description="Filter by skill name"),
    category: Optional[str] = Query(None, description="Filter by category"),
    limit: int = Query(50, ge=1, le=100, description="Number of results to return"),
    offset: int = Query(0, ge=0, description="Number of results to skip"),
    db: Session = Depends(get_db)
):
    """Get all skills with optional filtering"""
    try:
        query = db.query(Skill)
        
        if name:
            query = query.filter(Skill.name.ilike(f"%{name}%"))
        
        if category:
            query = query.filter(Skill.category.ilike(f"%{category}%"))
        
        total = query.count()
        skills = query.offset(offset).limit(limit).all()
        
        return SkillListResponse(
            data=skills,
            message=f"Found {len(skills)} skills"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve skills"
        )

@router.post("/", response_model=SingleSkillResponse, status_code=status.HTTP_201_CREATED)
async def create_skill(
    skill_data: SkillCreate,
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """Create a new skill (admin only)"""
    try:
        # Check if skill already exists
        existing_skill = db.query(Skill).filter(Skill.name == skill_data.name).first()
        if existing_skill:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Skill already exists"
            )
        
        # Create new skill
        db_skill = Skill(**skill_data.dict())
        db.add(db_skill)
        db.commit()
        db.refresh(db_skill)
        
        return SingleSkillResponse(
            data=db_skill,
            message="Skill created successfully"
        )
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create skill"
        )

@router.get("/search", response_model=SkillListResponse)
async def search_skills(
    name: Optional[str] = Query(None, description="Search by skill name"),
    category: Optional[str] = Query(None, description="Filter by category"),
    limit: int = Query(50, ge=1, le=100, description="Number of results to return"),
    offset: int = Query(0, ge=0, description="Number of results to skip"),
    db: Session = Depends(get_db)
):
    """Search skills by name and category"""
    try:
        query = db.query(Skill)
        
        if name:
            query = query.filter(Skill.name.ilike(f"%{name}%"))
        
        if category:
            query = query.filter(Skill.category.ilike(f"%{category}%"))
        
        total = query.count()
        skills = query.offset(offset).limit(limit).all()
        
        return SkillListResponse(
            data=skills,
            message=f"Found {len(skills)} skills"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to search skills"
        )

@router.post("/user-skills", response_model=SingleUserSkillResponse, status_code=status.HTTP_201_CREATED)
async def add_user_skill(
    user_skill_data: UserSkillCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Add a skill to current user (offered or wanted)"""
    try:
        # Check if skill exists
        skill = db.query(Skill).filter(Skill.id == user_skill_data.skill_id).first()
        if not skill:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Skill not found"
            )
        
        # Check if user already has this skill with the same type
        existing_user_skill = db.query(UserSkill).filter(
            UserSkill.user_id == current_user.clerk_user_id,
            UserSkill.skill_id == user_skill_data.skill_id,
            UserSkill.skill_type == user_skill_data.skill_type
        ).first()
        
        if existing_user_skill:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="User already has this skill with the specified type"
            )
        
        # Create user skill
        db_user_skill = UserSkill(
            user_id=current_user.clerk_user_id,
            **user_skill_data.dict()
        )
        db.add(db_user_skill)
        db.commit()
        db.refresh(db_user_skill)
        
        return SingleUserSkillResponse(
            data=db_user_skill,
            message="Skill added to user successfully"
        )
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to add skill to user"
        )

@router.delete("/user-skills/{user_skill_id}", response_model=BaseResponse)
async def remove_user_skill(
    user_skill_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Remove a skill from current user"""
    try:
        # Find the user skill
        user_skill = db.query(UserSkill).filter(
            UserSkill.id == user_skill_id,
            UserSkill.user_id == current_user.clerk_user_id
        ).first()
        
        if not user_skill:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User skill not found"
            )
        
        # Delete the user skill
        db.delete(user_skill)
        db.commit()
        
        return BaseResponse(
            message="Skill removed from user successfully"
        )
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to remove skill from user"
        )

@router.get("/user-skills/me", response_model=UserSkillListResponse)
async def get_current_user_skills(
    skill_type: Optional[SkillType] = Query(None, description="Filter by skill type"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get current user's skills"""
    try:
        query = db.query(UserSkill).filter(UserSkill.user_id == current_user.clerk_user_id)
        
        if skill_type:
            query = query.filter(UserSkill.skill_type == skill_type)
        
        user_skills = query.all()
        
        return UserSkillListResponse(
            data=user_skills,
            message=f"Found {len(user_skills)} skills"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve user skills"
        ) 