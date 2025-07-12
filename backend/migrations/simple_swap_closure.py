"""
Simple migration for swap closure using counter approach
"""

from sqlalchemy import text
from db.database import engine

def upgrade():
    """Add closed_count column and clean up old columns"""
    with engine.connect() as conn:
        print("1. Adding closed_count column...")
        try:
            conn.execute(text("""
                ALTER TABLE swap_requests 
                ADD COLUMN closed_count INTEGER DEFAULT 0
            """))
            print("   ✓ Added closed_count column")
        except Exception as e:
            print(f"   ⚠ closed_count column might already exist: {e}")
        
        print("2. Cleaning up old closure columns...")
        try:
            conn.execute(text("ALTER TABLE swap_requests DROP COLUMN IF EXISTS from_user_closed"))
            print("   ✓ Removed from_user_closed column")
        except Exception as e:
            print(f"   ⚠ Error removing from_user_closed: {e}")
        
        try:
            conn.execute(text("ALTER TABLE swap_requests DROP COLUMN IF EXISTS to_user_closed"))
            print("   ✓ Removed to_user_closed column")
        except Exception as e:
            print(f"   ⚠ Error removing to_user_closed: {e}")
        
        print("3. Adding CLOSED status to enum...")
        try:
            conn.execute(text("""
                ALTER TYPE swapstatus ADD VALUE 'CLOSED'
            """))
            print("   ✓ Added CLOSED to swapstatus enum")
        except Exception as e:
            print(f"   ⚠ CLOSED enum value might already exist: {e}")
        
        conn.commit()
        print("Migration completed successfully!")

if __name__ == "__main__":
    print("Running simple swap closure migration...")
    upgrade() 