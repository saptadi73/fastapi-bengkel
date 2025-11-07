from models.database import get_db
from sqlalchemy import text

db = next(get_db())
try:
    db.execute(text("""
    DO $$ BEGIN
        CREATE TYPE journaltype AS ENUM (
            'purchase',
            'sale',
            'ar_receipt',
            'ap_payment',
            'consignment',
            'expense',
            'general'
        );
    EXCEPTION
        WHEN duplicate_object THEN null;
    END $$;
    """))
    db.commit()
    print("Enum created successfully")
except Exception as e:
    print(f"Error: {e}")
    db.rollback()
