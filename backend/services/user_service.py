
from sqlalchemy.orm import Session
from models.user import User
from schemas.user import UserCreate, UserUpdate
from typing import List, Optional
import uuid

class UserService:
    @staticmethod
    def create_user(db: Session, user_data: UserCreate, clerk_id: str) -> User:
        """Create a new user linked to Clerk ID"""
        db_user = User(
            id=clerk_id,
            **user_data.dict()
        )
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
        return db_user

    @staticmethod
    def get_user_by_id(db: Session, user_id: str) -> Optional[User]:
        """Get user by ID"""
        return db.query(User).filter(User.id == user_id).first()

    @staticmethod
    def update_user(db: Session, user_id: str, user_data: UserUpdate) -> Optional[User]:
        """Update user profile"""
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            return None
        
        update_data = user_data.dict(exclude_unset=True)
        print(f"Updating user {user_id} with data: {update_data}")
        
        for field, value in update_data.items():
            print(f"Setting {field} = {value}")
            setattr(user, field, value)
        
        db.commit()
        db.refresh(user)
        print(f"After update - skills_offered: {user.skills_offered}, skills_wanted: {user.skills_wanted}")
        return user

    @staticmethod
    def search_users_by_skill(db: Session, skill: str) -> List[User]:
        """Search public users by offered or wanted skills"""
        return db.query(User).filter(
            User.is_public == True,
            User.is_active == True,
            User.is_banned == False,
            (User.skills_offered.contains([skill]) | User.skills_wanted.contains([skill]))
        ).all()

    @staticmethod
    def get_all_public_users(db: Session, exclude_user_id: Optional[str] = None) -> List[User]:
        """Get all public, active, non-banned users"""
        query = db.query(User).filter(
            User.is_public == True,
            User.is_active == True,
            User.is_banned == False
        )
        
        if exclude_user_id:
            query = query.filter(User.id != exclude_user_id)
            
        return query.all()

    @staticmethod
    def get_all_users(db: Session) -> List[User]:
        """Get all users (admin only)"""
        return db.query(User).all()

    @staticmethod
    def ban_user(db: Session, user_id: str) -> Optional[User]:
        """Ban a user (admin only)"""
        user = db.query(User).filter(User.id == user_id).first()
        if user:
            user.is_banned = True
            db.commit()
            db.refresh(user)
        return user

    @staticmethod
    def sync_user_from_clerk(db: Session, clerk_user_data: dict, clerk_id: str) -> User:
        """Create or update user from Clerk data"""
        existing_user = UserService.get_user_by_id(db, clerk_id)
        
        # Extract name from Clerk data
        first_name = clerk_user_data.get('first_name', '')
        last_name = clerk_user_data.get('last_name', '')
        full_name = clerk_user_data.get('full_name', '')
        
        # Determine the name to use
        if first_name and last_name:
            name = f"{first_name} {last_name}"
        elif first_name:
            name = first_name
        elif full_name:
            name = full_name
        else:
            name = clerk_user_data.get('username', 'User')
        
        email = ''
        if clerk_user_data.get('email_addresses'):
            email = clerk_user_data['email_addresses'][0].get('email_address', '')
        
        if existing_user:
            # Update existing user with latest Clerk data
            existing_user.name = name
            existing_user.email = email
            db.commit()
            db.refresh(existing_user)
            return existing_user
        else:
            # Create new user
            user_data = UserCreate(
                name=name,
                email=email,
                location='',
                skills_offered=[],
                skills_wanted=[],
                availability='',
                is_public=True
            )
            return UserService.create_user(db, user_data, clerk_id)
