from models.database import get_db
from models.accounting import JournalEntry, JournalType
from sqlalchemy import text
import uuid
from datetime import date

db = next(get_db())
try:
    # Test inserting a journal entry with consignment type
    entry = JournalEntry(
        id=uuid.uuid4(),
        entry_no='TEST-CONS-001',
        date=date.today(),
        memo='Test consignment entry',
        journal_type=JournalType.consignment,
        created_by='test'
    )
    db.add(entry)
    db.commit()
    print("Consignment journal entry inserted successfully!")
except Exception as e:
    print(f"Error inserting consignment entry: {e}")
    db.rollback()
