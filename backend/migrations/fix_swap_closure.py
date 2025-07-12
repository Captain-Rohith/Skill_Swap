"""
Comprehensive migration to fix swap closure functionality
- Adds closure tracking columns to swap_requests table
- Adds CLOSED status to swapstatus enum
"""

from sqlalchemy import text
from db.database import engine

def upgrade():
    """Run all necessary migrations for swap closure"""
    with engine.connect() as conn:
        print("1. Adding closure tracking columns...")
        try:
            # Add from_user_closed column
            conn.execute(text("""
                ALTER TABLE swap_requests 
                ADD COLUMN from_user_closed BOOLEAN DEFAULT FALSE
            """))
            print("   ✓ Added from_user_closed column")
        except Exception as e:
            print(f"   ⚠ from_user_closed column might already exist: {e}")
        
        try:
            # Add to_user_closed column
            conn.execute(text("""
                ALTER TABLE swap_requests 
                ADD COLUMN to_user_closed BOOLEAN DEFAULT FALSE
            """))
            print("   ✓ Added to_user_closed column")
        except Exception as e:
            print(f"   ⚠ to_user_closed column might already exist: {e}")
        
        print("2. Adding CLOSED status to enum...")
        try:
            # Add CLOSED to the enum
            conn.execute(text("""
                ALTER TYPE swapstatus ADD VALUE 'CLOSED'
            """))
            print("   ✓ Added CLOSED to swapstatus enum")
        except Exception as e:
            print(f"   ⚠ CLOSED enum value might already exist: {e}")
        
        conn.commit()
        print("Migration completed successfully!")

def downgrade():
    """Remove the changes (partial - enum values cannot be easily removed)"""
    with engine.connect() as conn:
        try:
            conn.execute(text("ALTER TABLE swap_requests DROP COLUMN IF EXISTS from_user_closed"))
            conn.execute(text("ALTER TABLE swap_requests DROP COLUMN IF EXISTS to_user_closed"))
            print("Removed closure tracking columns")
        except Exception as e:
            print(f"Error removing columns: {e}")
        
        print("Note: Cannot easily remove enum values in PostgreSQL")
        print("Manual intervention required to remove 'CLOSED' from swapstatus enum")
        conn.commit()

if __name__ == "__main__":
    print("Running comprehensive swap closure migration...")
    upgrade() 