from models.database import get_db
from sqlalchemy import text

db = next(get_db())
try:
    result = db.execute(text("SELECT unnest(enum_range(NULL::journaltype)) AS values"))
    values = [row[0] for row in result.fetchall()]
    print("Current enum values:", values)
    if 'consignment' in values:
        print("Consignment is present in the enum.")
    else:
        print("Consignment is NOT present in the enum.")
except Exception as e:
    print(f"Error: {e}")
