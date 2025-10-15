import sys
import os
import uuid
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from datetime import date
from decimal import Decimal
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models.accounting import Base, Account
from services.services_accounting import create_expense_journal_entry
from schemas.service_accounting import ExpenseJournalEntry

# Create in-memory SQLite database for testing
engine = create_engine("sqlite:///:memory:")
Base.metadata.create_all(engine)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def create_test_accounts_full(db):
    # Create test accounts directly
    # Kas account
    acc1 = Account(id=uuid.uuid4(), code="1100", name="Kas", normal_balance="debit", account_type="asset", is_active=True)
    db.add(acc1)
    # Expense account for listrik
    acc2 = Account(id=uuid.uuid4(), code="6001", name="Biaya Listrik", normal_balance="debit", account_type="expense", is_active=True)
    db.add(acc2)
    # PPN Masukan account
    acc3 = Account(id=uuid.uuid4(), code="1510", name="PPN Masukan", normal_balance="debit", account_type="asset", is_active=True)
    db.add(acc3)
    db.commit()

def test_create_expense_journal_entry():
    # Test data
    expense_id = uuid.uuid4()
    data = ExpenseJournalEntry(
        date=date.today(),
        memo="Test expense payment",
        expense_id=expense_id,
        amount=Decimal("100000.00"),
        kas_bank_code="1100",  # Kas
        expense_code="6001",  # Listrik
        pajak=Decimal("0.00"),
        ppn_masukan_code=None
    )

    # Create new engine for this test
    engine1 = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine1)
    SessionLocal1 = sessionmaker(autocommit=False, autoflush=False, bind=engine1)
    db1 = SessionLocal1()

    create_test_accounts_full(db1)

    try:
        entry = create_expense_journal_entry(db1, data)
        print("Test passed: Expense journal entry created successfully")
        print(f"Entry No: {entry['entry_no']}")
        print(f"Total Lines: {len(entry['lines'])}")
        total_debit = sum(line['debit'] for line in entry['lines'])
        total_credit = sum(line['credit'] for line in entry['lines'])
        print(f"Total Debit: {total_debit}, Total Credit: {total_credit}")
        assert total_debit == total_credit, "Journal not balanced"
        print("Balance check passed")
    except Exception as e:
        print(f"Test failed: {e}")
        db1.close()
        return False

    db1.close()

    # Test with tax
    expense_id2 = uuid.uuid4()
    data_with_tax = ExpenseJournalEntry(
        date=date.today(),
        memo="Test expense with tax",
        expense_id=expense_id2,
        amount=Decimal("100000.00"),
        kas_bank_code="1100",
        expense_code="6001",
        pajak=Decimal("10000.00"),
        ppn_masukan_code="1510"
    )

    # Create new engine for this test
    engine2 = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine2)
    SessionLocal2 = sessionmaker(autocommit=False, autoflush=False, bind=engine2)
    db2 = SessionLocal2()

    create_test_accounts_full(db2)

    try:
        entry2 = create_expense_journal_entry(db2, data_with_tax)
        print("Test passed: Expense journal entry with tax created successfully")
        print(f"Entry No: {entry2['entry_no']}")
        total_debit2 = sum(line['debit'] for line in entry2['lines'])
        total_credit2 = sum(line['credit'] for line in entry2['lines'])
        assert total_debit2 == total_credit2, "Journal not balanced"
        print("Balance check passed for with tax")
    except Exception as e:
        print(f"Test failed for with tax: {e}")
        db2.close()
        return False

    db2.close()
    return True

if __name__ == "__main__":
    success = test_create_expense_journal_entry()
    if success:
        print("All tests passed!")
    else:
        print("Some tests failed!")
