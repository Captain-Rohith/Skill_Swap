"""
Migration to add closure tracking columns to swap_requests table
"""

from sqlalchemy import text
from db.database import engine

def upgrade():
    """Add the new columns to swap_requests table"""
    with engine.connect() as conn:
        # Add from_user_closed column
        conn.execute(text("""
            ALTER TABLE swap_requests 
            ADD COLUMN from_user_closed BOOLEAN DEFAULT FALSE
        """))
        
        # Add to_user_closed column
        conn.execute(text("""
            ALTER TABLE swap_requests 
            ADD COLUMN to_user_closed BOOLEAN DEFAULT FALSE
        """))
        
        conn.commit()

def downgrade():
    """Remove the columns if needed"""
    with engine.connect() as conn:
        conn.execute(text("ALTER TABLE swap_requests DROP COLUMN IF EXISTS from_user_closed"))
        conn.execute(text("ALTER TABLE swap_requests DROP COLUMN IF EXISTS to_user_closed"))
        conn.commit()

if __name__ == "__main__":
    print("Adding closure tracking columns to swap_requests table...")
    upgrade()
    print("Migration completed successfully!") 