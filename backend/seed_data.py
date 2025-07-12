#!/usr/bin/env python3
"""
Seed script to populate the database with sample data
"""

import os
from dotenv import load_dotenv
from database import SessionLocal, engine
from models import Base, User, Skill, UserSkill, SwapRequest, Rating, SkillType, SwapStatus

# Load environment variables
load_dotenv()

def create_sample_skills(db):
    """Create sample skills"""
    print("Creating sample skills...")
    
    skills_data = [
        {"name": "Python Programming", "category": "Programming"},
        {"name": "JavaScript", "category": "Programming"},
        {"name": "Web Design", "category": "Design"},
        {"name": "Graphic Design", "category": "Design"},
        {"name": "Cooking", "category": "Lifestyle"},
        {"name": "Photography", "category": "Arts"},
        {"name": "Guitar", "category": "Music"},
        {"name": "Spanish", "category": "Language"},
        {"name": "French", "category": "Language"},
        {"name": "Yoga", "category": "Fitness"},
        {"name": "Running", "category": "Fitness"},
        {"name": "Chess", "category": "Games"},
        {"name": "Math Tutoring", "category": "Education"},
        {"name": "English Tutoring", "category": "Education"},
        {"name": "Car Maintenance", "category": "Automotive"},
        {"name": "Gardening", "category": "Lifestyle"},
        {"name": "Knitting", "category": "Crafts"},
        {"name": "Drawing", "category": "Arts"},
        {"name": "Public Speaking", "category": "Communication"},
        {"name": "Project Management", "category": "Business"}
    ]
    
    for skill_data in skills_data:
        existing_skill = db.query(Skill).filter(Skill.name == skill_data["name"]).first()
        if not existing_skill:
            skill = Skill(**skill_data)
            db.add(skill)
            print(f"  ✓ Created skill: {skill_data['name']}")
        else:
            print(f"  - Skill already exists: {skill_data['name']}")
    
    db.commit()
    print("Sample skills created successfully!")

def create_sample_users(db):
    """Create sample users"""
    print("\nCreating sample users...")
    
    users_data = [
        {
            "clerk_user_id": "user_001",
            "name": "Alice Johnson",
            "email": "alice@example.com",
            "location": "New York, NY",
            "availability": "Weekends, evenings",
            "is_public": True
        },
        {
            "clerk_user_id": "user_002",
            "name": "Bob Smith",
            "email": "bob@example.com",
            "location": "Los Angeles, CA",
            "availability": "Weekdays after 6 PM",
            "is_public": True
        },
        {
            "clerk_user_id": "user_003",
            "name": "Carol Davis",
            "email": "carol@example.com",
            "location": "Chicago, IL",
            "availability": "Flexible",
            "is_public": True
        },
        {
            "clerk_user_id": "user_004",
            "name": "David Wilson",
            "email": "david@example.com",
            "location": "Miami, FL",
            "availability": "Mornings, weekends",
            "is_public": True
        },
        {
            "clerk_user_id": "user_005",
            "name": "Eva Brown",
            "email": "eva@example.com",
            "location": "Seattle, WA",
            "availability": "Evenings only",
            "is_public": True
        }
    ]
    
    for user_data in users_data:
        existing_user = db.query(User).filter(User.clerk_user_id == user_data["clerk_user_id"]).first()
        if not existing_user:
            user = User(**user_data)
            db.add(user)
            print(f"  ✓ Created user: {user_data['name']}")
        else:
            print(f"  - User already exists: {user_data['name']}")
    
    db.commit()
    print("Sample users created successfully!")

def create_sample_user_skills(db):
    """Create sample user skills"""
    print("\nCreating sample user skills...")
    
    # Get all users and skills
    users = db.query(User).all()
    skills = db.query(Skill).all()
    
    if not users or not skills:
        print("  - No users or skills found. Please create them first.")
        return
    
    # Sample user skills data
    user_skills_data = [
        # Alice's skills
        {"user_id": "user_001", "skill_name": "Python Programming", "skill_type": SkillType.OFFERED, "proficiency_level": "Advanced"},
        {"user_id": "user_001", "skill_name": "Web Design", "skill_type": SkillType.OFFERED, "proficiency_level": "Intermediate"},
        {"user_id": "user_001", "skill_name": "Spanish", "skill_type": SkillType.WANTED, "proficiency_level": "Beginner"},
        
        # Bob's skills
        {"user_id": "user_002", "skill_name": "JavaScript", "skill_type": SkillType.OFFERED, "proficiency_level": "Advanced"},
        {"user_id": "user_002", "skill_name": "Photography", "skill_type": SkillType.OFFERED, "proficiency_level": "Intermediate"},
        {"user_id": "user_002", "skill_name": "Cooking", "skill_type": SkillType.WANTED, "proficiency_level": "Beginner"},
        
        # Carol's skills
        {"user_id": "user_003", "skill_name": "Cooking", "skill_type": SkillType.OFFERED, "proficiency_level": "Advanced"},
        {"user_id": "user_003", "skill_name": "Yoga", "skill_type": SkillType.OFFERED, "proficiency_level": "Intermediate"},
        {"user_id": "user_003", "skill_name": "Python Programming", "skill_type": SkillType.WANTED, "proficiency_level": "Beginner"},
        
        # David's skills
        {"user_id": "user_004", "skill_name": "Spanish", "skill_type": SkillType.OFFERED, "proficiency_level": "Native"},
        {"user_id": "user_004", "skill_name": "Car Maintenance", "skill_type": SkillType.OFFERED, "proficiency_level": "Advanced"},
        {"user_id": "user_004", "skill_name": "Guitar", "skill_type": SkillType.WANTED, "proficiency_level": "Beginner"},
        
        # Eva's skills
        {"user_id": "user_005", "skill_name": "Guitar", "skill_type": SkillType.OFFERED, "proficiency_level": "Advanced"},
        {"user_id": "user_005", "skill_name": "Drawing", "skill_type": SkillType.OFFERED, "proficiency_level": "Intermediate"},
        {"user_id": "user_005", "skill_name": "French", "skill_type": SkillType.WANTED, "proficiency_level": "Beginner"}
    ]
    
    for skill_data in user_skills_data:
        # Find user and skill
        user = db.query(User).filter(User.clerk_user_id == skill_data["user_id"]).first()
        skill = db.query(Skill).filter(Skill.name == skill_data["skill_name"]).first()
        
        if user and skill:
            # Check if user skill already exists
            existing_user_skill = db.query(UserSkill).filter(
                UserSkill.user_id == user.clerk_user_id,
                UserSkill.skill_id == skill.id,
                UserSkill.skill_type == skill_data["skill_type"]
            ).first()
            
            if not existing_user_skill:
                user_skill = UserSkill(
                    user_id=user.clerk_user_id,
                    skill_id=skill.id,
                    skill_type=skill_data["skill_type"],
                    proficiency_level=skill_data["proficiency_level"]
                )
                db.add(user_skill)
                print(f"  ✓ Added {skill_data['skill_name']} ({skill_data['skill_type']}) to {user.name}")
            else:
                print(f"  - User skill already exists: {skill_data['skill_name']} for {user.name}")
    
    db.commit()
    print("Sample user skills created successfully!")

def create_sample_swap_requests(db):
    """Create sample swap requests"""
    print("\nCreating sample swap requests...")
    
    # Get some users and their skills
    alice = db.query(User).filter(User.clerk_user_id == "user_001").first()
    bob = db.query(User).filter(User.clerk_user_id == "user_002").first()
    carol = db.query(User).filter(User.clerk_user_id == "user_003").first()
    
    if not all([alice, bob, carol]):
        print("  - Not enough users found. Please create users first.")
        return
    
    # Get skills
    python_skill = db.query(Skill).filter(Skill.name == "Python Programming").first()
    js_skill = db.query(Skill).filter(Skill.name == "JavaScript").first()
    cooking_skill = db.query(Skill).filter(Skill.name == "Cooking").first()
    
    if not all([python_skill, js_skill, cooking_skill]):
        print("  - Not enough skills found. Please create skills first.")
        return
    
    # Create sample swap requests
    swap_requests_data = [
        {
            "requester_id": alice.clerk_user_id,
            "requested_user_id": bob.clerk_user_id,
            "offered_skill_id": python_skill.id,
            "requested_skill_id": js_skill.id,
            "status": SwapStatus.PENDING,
            "message": "I'd love to learn JavaScript! I can teach you Python in return."
        },
        {
            "requester_id": bob.clerk_user_id,
            "requested_user_id": carol.clerk_user_id,
            "offered_skill_id": js_skill.id,
            "requested_skill_id": cooking_skill.id,
            "status": SwapStatus.ACCEPTED,
            "message": "I'm interested in learning to cook. Can you teach me some basics?"
        }
    ]
    
    for swap_data in swap_requests_data:
        # Check if swap already exists
        existing_swap = db.query(SwapRequest).filter(
            SwapRequest.requester_id == swap_data["requester_id"],
            SwapRequest.requested_user_id == swap_data["requested_user_id"],
            SwapRequest.offered_skill_id == swap_data["offered_skill_id"],
            SwapRequest.requested_skill_id == swap_data["requested_skill_id"]
        ).first()
        
        if not existing_swap:
            swap_request = SwapRequest(**swap_data)
            db.add(swap_request)
            print(f"  ✓ Created swap request: {swap_data['requester_id']} -> {swap_data['requested_user_id']}")
        else:
            print(f"  - Swap request already exists")
    
    db.commit()
    print("Sample swap requests created successfully!")

def main():
    """Main seeding function"""
    print("Skill Swap Database Seeding")
    print("=" * 40)
    
    # Create database tables
    Base.metadata.create_all(bind=engine)
    
    # Create database session
    db = SessionLocal()
    
    try:
        # Seed data in order
        create_sample_skills(db)
        create_sample_users(db)
        create_sample_user_skills(db)
        create_sample_swap_requests(db)
        
        print("\n" + "=" * 40)
        print("🎉 Database seeding completed successfully!")
        print("\nSample data created:")
        print("- 20 skills across different categories")
        print("- 5 sample users")
        print("- 15 user skill associations")
        print("- 2 sample swap requests")
        
    except Exception as e:
        print(f"\n❌ Error during seeding: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    main()
