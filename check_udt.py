from models.database import get_db
from sqlalchemy import text

db = next(get_db())
try:
    result = db.execute(text("""
    SELECT typname, typcategory
    FROM pg_type
    WHERE typname = 'journal_type'
    """))
    row = result.fetchone()
    if row:
        print(f"Type Name: {row[0]}, Category: {row[1]}")
    else:
        print("Type not found")

    # Check enum values for journal_type
    result2 = db.execute(text("SELECT unnest(enum_range(NULL::journal_type)) AS values"))
    values = [row[0] for row in result2.fetchall()]
    print("Enum values for journal_type:", values)
except Exception as e:
    print(f"Error: {e}")
