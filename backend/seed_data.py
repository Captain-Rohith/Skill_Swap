from sqlalchemy.orm import Session
from database import SessionLocal, engine
from models import User, Skill, UserSkill, SwapRequest, Rating, SkillType, SwapStatus
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def seed_database():
    """Seed the database with initial data"""
    db = SessionLocal()
    
    try:
        # Check if data already exists
        if db.query(User).count() > 0:
            logger.info("Database already seeded. Skipping...")
            return
        
        logger.info("Seeding database...")
        
        # Create skills
        skills_data = [
            {"name": "Python Programming", "category": "Programming"},
            {"name": "JavaScript", "category": "Programming"},
            {"name": "Web Design", "category": "Design"},
            {"name": "Graphic Design", "category": "Design"},
            {"name": "Cooking", "category": "Lifestyle"},
            {"name": "Guitar", "category": "Music"},
            {"name": "Piano", "category": "Music"},
            {"name": "Spanish", "category": "Language"},
            {"name": "French", "category": "Language"},
            {"name": "Photography", "category": "Art"},
            {"name": "Drawing", "category": "Art"},
            {"name": "Yoga", "category": "Fitness"},
            {"name": "Weight Training", "category": "Fitness"},
            {"name": "Data Analysis", "category": "Analytics"},
            {"name": "Machine Learning", "category": "Analytics"}
        ]
        
        skills = []
        for skill_data in skills_data:
            skill = Skill(**skill_data)
            db.add(skill)
            skills.append(skill)
        
        db.commit()
        logger.info(f"Created {len(skills)} skills")
        
        # Create users
        users_data = [
            {
                "name": "Alice Johnson",
                "email": "alice@example.com",
                "location": "New York, NY",
                "availability": "weekends, evenings",
                "is_public": True
            },
            {
                "name": "Bob Smith",
                "email": "bob@example.com",
                "location": "San Francisco, CA",
                "availability": "weekdays",
                "is_public": True
            },
            {
                "name": "Carol Davis",
                "email": "carol@example.com",
                "location": "Austin, TX",
                "availability": "flexible",
                "is_public": True
            },
            {
                "name": "David Wilson",
                "email": "david@example.com",
                "location": "Seattle, WA",
                "availability": "weekends",
                "is_public": True
            },
            {
                "name": "Eva Brown",
                "email": "eva@example.com",
                "location": "Chicago, IL",
                "availability": "evenings",
                "is_public": True
            }
        ]
        
        users = []
        for user_data in users_data:
            user = User(**user_data)
            db.add(user)
            users.append(user)
        
        db.commit()
        logger.info(f"Created {len(users)} users")
        
        # Create user skills
        user_skills_data = [
            # Alice's skills
            {"user_id": 1, "skill_id": 1, "skill_type": SkillType.OFFERED, "proficiency_level": "Advanced"},
            {"user_id": 1, "skill_id": 3, "skill_type": SkillType.OFFERED, "proficiency_level": "Intermediate"},
            {"user_id": 1, "skill_id": 5, "skill_type": SkillType.WANTED, "proficiency_level": "Beginner"},
            {"user_id": 1, "skill_id": 7, "skill_type": SkillType.WANTED, "proficiency_level": "Beginner"},
            
            # Bob's skills
            {"user_id": 2, "skill_id": 2, "skill_type": SkillType.OFFERED, "proficiency_level": "Advanced"},
            {"user_id": 2, "skill_id": 14, "skill_type": SkillType.OFFERED, "proficiency_level": "Intermediate"},
            {"user_id": 2, "skill_id": 8, "skill_type": SkillType.WANTED, "proficiency_level": "Beginner"},
            {"user_id": 2, "skill_id": 12, "skill_type": SkillType.WANTED, "proficiency_level": "Beginner"},
            
            # Carol's skills
            {"user_id": 3, "skill_id": 4, "skill_type": SkillType.OFFERED, "proficiency_level": "Advanced"},
            {"user_id": 3, "skill_id": 10, "skill_type": SkillType.OFFERED, "proficiency_level": "Intermediate"},
            {"user_id": 3, "skill_id": 1, "skill_type": SkillType.WANTED, "proficiency_level": "Beginner"},
            {"user_id": 3, "skill_id": 15, "skill_type": SkillType.WANTED, "proficiency_level": "Beginner"},
            
            # David's skills
            {"user_id": 4, "skill_id": 6, "skill_type": SkillType.OFFERED, "proficiency_level": "Advanced"},
            {"user_id": 4, "skill_id": 8, "skill_type": SkillType.OFFERED, "proficiency_level": "Intermediate"},
            {"user_id": 4, "skill_id": 9, "skill_type": SkillType.WANTED, "proficiency_level": "Beginner"},
            {"user_id": 4, "skill_id": 13, "skill_type": SkillType.WANTED, "proficiency_level": "Beginner"},
            
            # Eva's skills
            {"user_id": 5, "skill_id": 5, "skill_type": SkillType.OFFERED, "proficiency_level": "Advanced"},
            {"user_id": 5, "skill_id": 12, "skill_type": SkillType.OFFERED, "proficiency_level": "Intermediate"},
            {"user_id": 5, "skill_id": 2, "skill_type": SkillType.WANTED, "proficiency_level": "Beginner"},
            {"user_id": 5, "skill_id": 11, "skill_type": SkillType.WANTED, "proficiency_level": "Beginner"}
        ]
        
        for user_skill_data in user_skills_data:
            user_skill = UserSkill(**user_skill_data)
            db.add(user_skill)
        
        db.commit()
        logger.info(f"Created {len(user_skills_data)} user skills")
        
        # Create some sample swap requests
        swap_requests_data = [
            {
                "requester_id": 1,
                "requested_user_id": 2,
                "offered_skill_id": 1,  # Python Programming
                "requested_skill_id": 2,  # JavaScript
                "status": SwapStatus.PENDING,
                "message": "I'd love to learn JavaScript! I can teach you Python in return."
            },
            {
                "requester_id": 3,
                "requested_user_id": 1,
                "offered_skill_id": 4,  # Graphic Design
                "requested_skill_id": 3,  # Web Design
                "status": SwapStatus.ACCEPTED,
                "message": "I can help you with graphic design if you teach me web design!"
            },
            {
                "requester_id": 4,
                "requested_user_id": 5,
                "offered_skill_id": 6,  # Guitar
                "requested_skill_id": 5,  # Cooking
                "status": SwapStatus.COMPLETED,
                "message": "Guitar lessons for cooking lessons? Sounds like a great deal!"
            }
        ]
        
        for swap_data in swap_requests_data:
            swap = SwapRequest(**swap_data)
            db.add(swap)
        
        db.commit()
        logger.info(f"Created {len(swap_requests_data)} swap requests")
        
        # Create some sample ratings for completed swaps
        ratings_data = [
            {
                "swap_request_id": 3,
                "rater_id": 4,
                "rated_user_id": 5,
                "rating": 5,
                "feedback": "Eva is an amazing cook! Learned so much about Italian cuisine."
            },
            {
                "swap_request_id": 3,
                "rater_id": 5,
                "rated_user_id": 4,
                "rating": 5,
                "feedback": "David is a fantastic guitar teacher. Very patient and knowledgeable."
            }
        ]
        
        for rating_data in ratings_data:
            rating = Rating(**rating_data)
            db.add(rating)
        
        db.commit()
        logger.info(f"Created {len(ratings_data)} ratings")
        
        logger.info("Database seeding completed successfully!")
        
    except Exception as e:
        logger.error(f"Error seeding database: {e}")
        db.rollback()
        raise
    finally:
        db.close()

if __name__ == "__main__":
    seed_database()
