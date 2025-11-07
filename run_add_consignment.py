from models.database import get_db
from sqlalchemy import text

db = next(get_db())
try:
    db.execute(text("""
    DO $$ BEGIN
        ALTER TYPE journaltype ADD VALUE 'consignment';
    EXCEPTION
        WHEN duplicate_object THEN null;
    END $$;
    """))
    db.commit()
    print("Consignment added to enum successfully")
except Exception as e:
    print(f"Error: {e}")
    db.rollback()
