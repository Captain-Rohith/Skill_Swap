#!/usr/bin/env python3
"""
Test script to verify the Skill Swap backend setup
"""

import os
import sys
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def test_imports():
    """Test that all modules can be imported"""
    print("Testing imports...")
    
    try:
        from database import engine, get_db, SessionLocal
        print("✓ Database module imported successfully")
    except Exception as e:
        print(f"✗ Failed to import database module: {e}")
        return False
    
    try:
        from models import User, Skill, UserSkill, SwapRequest, Rating
        print("✓ Models imported successfully")
    except Exception as e:
        print(f"✗ Failed to import models: {e}")
        return False
    
    try:
        from schemas import UserCreate, SkillCreate, SwapRequestCreate
        print("✓ Schemas imported successfully")
    except Exception as e:
        print(f"✗ Failed to import schemas: {e}")
        return False
    
    try:
        from utils.auth import get_current_user
        print("✓ Auth utilities imported successfully")
    except Exception as e:
        print(f"✗ Failed to import auth utilities: {e}")
        return False
    
    return True

def test_database_connection():
    """Test database connection"""
    print("\nTesting database connection...")
    
    try:
        from database import engine
        
        # Test connection
        from sqlalchemy import text
        with engine.connect() as connection:
            result = connection.execute(text("SELECT 1"))
            result.fetchone()
            print("✓ Database connection successful")
            return True
    except Exception as e:
        print(f"✗ Database connection failed: {e}")
        return False

def test_database_tables():
    """Test that database tables can be created"""
    print("\nTesting database table creation...")
    
    try:
        from database import engine
        from models import Base
        
        # Create tables
        Base.metadata.create_all(bind=engine)
        print("✓ Database tables created successfully")
        return True
    except Exception as e:
        print(f"✗ Failed to create database tables: {e}")
        return False

def test_environment_variables():
    """Test that required environment variables are set"""
    print("\nTesting environment variables...")
    
    required_vars = [
        "DATABASE_URL"
    ]
    
    missing_vars = []
    for var in required_vars:
        if not os.getenv(var):
            missing_vars.append(var)
    
    if missing_vars:
        print(f"✗ Missing environment variables: {', '.join(missing_vars)}")
        print("Please create a .env file with the required variables")
        return False
    else:
        print("✓ All required environment variables are set")
        return True

def main():
    """Run all tests"""
    print("Skill Swap Backend Setup Test")
    print("=" * 40)
    
    tests = [
        test_imports,
        test_environment_variables,
        test_database_connection,
        test_database_tables
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        if test():
            passed += 1
    
    print("\n" + "=" * 40)
    print(f"Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! Your backend is ready to run.")
        print("\nNext steps:")
        print("1. Run: python main.py")
        print("2. Visit: http://localhost:8000/docs")
    else:
        print("❌ Some tests failed. Please check the errors above.")
        sys.exit(1)

if __name__ == "__main__":
    main()
