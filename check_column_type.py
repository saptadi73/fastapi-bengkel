from models.database import get_db
from sqlalchemy import text

db = next(get_db())
try:
    result = db.execute(text("""
    SELECT column_name, data_type, udt_name
    FROM information_schema.columns
    WHERE table_name = 'journal_entries' AND column_name = 'journal_type'
    """))
    row = result.fetchone()
    if row:
        print(f"Column: {row[0]}, Data Type: {row[1]}, UDT Name: {row[2]}")
    else:
        print("Column not found")
except Exception as e:
    print(f"Error: {e}")
