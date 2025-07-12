"""
Migration to add 'CLOSED' status to swapstatus enum
"""

from sqlalchemy import text
from db.database import engine

def upgrade():
    """Add CLOSED value to swapstatus enum"""
    with engine.connect() as conn:
        # Add CLOSED to the enum
        conn.execute(text("""
            ALTER TYPE swapstatus ADD VALUE 'CLOSED'
        """))
        conn.commit()

def downgrade():
    """Note: PostgreSQL doesn't support removing enum values easily"""
    print("Warning: Cannot easily remove enum values in PostgreSQL")
    print("Manual intervention may be required if you need to remove 'CLOSED'")

if __name__ == "__main__":
    print("Adding 'CLOSED' status to swapstatus enum...")
    try:
        upgrade()
        print("Migration completed successfully!")
    except Exception as e:
        print(f"Migration failed: {e}")
        print("The enum value might already exist. This is not a critical error.") 