from models.database import get_db
from sqlalchemy import text

db = next(get_db())
try:
    # First, check if journal_entries table exists
    result = db.execute(text("SELECT EXISTS (SELECT 1 FROM information_schema.tables WHERE table_name = 'journal_entries')"))
    exists = result.fetchone()[0]
    if not exists:
        print("journal_entries table does not exist. Please run the accounting migration first.")
        db.close()
        exit(1)

    # Check current enum for journal_type column
    result = db.execute(text("""
    SELECT udt_name
    FROM information_schema.columns
    WHERE table_name = 'journal_entries' AND column_name = 'journal_type'
    """))
    udt_name = result.fetchone()[0]
    print(f"Current UDT for journal_type column: {udt_name}")

    if udt_name == 'journal_type':
        # Drop default first
        db.execute(text("ALTER TABLE journal_entries ALTER COLUMN journal_type DROP DEFAULT"))
        # Change to journaltype using explicit cast
        db.execute(text("ALTER TABLE journal_entries ALTER COLUMN journal_type TYPE journaltype USING journal_type::text::journaltype"))
        # Set new default
        db.execute(text("ALTER TABLE journal_entries ALTER COLUMN journal_type SET DEFAULT 'general'::journaltype"))
        db.commit()
        print("Column journal_type changed to use journaltype enum.")
    else:
        print("Column already uses journaltype.")

except Exception as e:
    print(f"Error: {e}")
    db.rollback()
