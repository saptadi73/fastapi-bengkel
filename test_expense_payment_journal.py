import sys
import os
import uuid
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from datetime import date
from decimal import Decimal
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models.accounting import Base, Account
from services.services_accounting import create_expense_payment_journal_entry
from schemas.service_accounting import ExpensePaymentJournalEntry

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
    # Potongan Biaya account
    acc3 = Account(id=uuid.uuid4(), code="7000", name="Potongan Biaya", normal_balance="debit", account_type="expense", is_active=True)
    db.add(acc3)
    db.commit()

def test_create_expense_payment_journal_entry():
    # Test data without discount
    data = ExpensePaymentJournalEntry(
        date=date.today(),
        memo="Test expense payment",
        expense_id=None,
        amount=Decimal("100000.00"),
        kas_bank_code="1100",  # Kas
        expense_code="6001",  # Listrik
        discount=Decimal("0.00"),
        potongan_biaya_code=None
    )

    # Create new engine for this test
    engine1 = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine1)
    SessionLocal1 = sessionmaker(autocommit=False, autoflush=False, bind=engine1)
    db1 = SessionLocal1()

    create_test_accounts_full(db1)

    try:
        entry = create_expense_payment_journal_entry(db1, data)
        print("Test passed: Expense payment journal entry created successfully")
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

    # Test with discount
    data_with_discount = ExpensePaymentJournalEntry(
        date=date.today(),
        memo="Test expense payment with discount",
        expense_id=None,
        amount=Decimal("100000.00"),
        kas_bank_code="1100",
        expense_code="6001",
        discount=Decimal("10000.00"),
        potongan_biaya_code="7000"
    )

    # Create new engine for this test
    engine2 = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine2)
    SessionLocal2 = sessionmaker(autocommit=False, autoflush=False, bind=engine2)
    db2 = SessionLocal2()

    create_test_accounts_full(db2)

    try:
        entry2 = create_expense_payment_journal_entry(db2, data_with_discount)
        print("Test passed: Expense payment journal entry with discount created successfully")
        print(f"Entry No: {entry2['entry_no']}")
        total_debit2 = sum(line['debit'] for line in entry2['lines'])
        total_credit2 = sum(line['credit'] for line in entry2['lines'])
        assert total_debit2 == total_credit2, "Journal not balanced"
        print("Balance check passed for with discount")
    except Exception as e:
        print(f"Test failed for with discount: {e}")
        db2.close()
        return False

    db2.close()

    # Test error case: discount > 0 but no potongan_biaya_code
    data_error = ExpensePaymentJournalEntry(
        date=date.today(),
        memo="Test error case",
        expense_id=None,
        amount=Decimal("100000.00"),
        kas_bank_code="1100",
        expense_code="6001",
        discount=Decimal("10000.00"),
        potongan_biaya_code=None
    )

    # Create new engine for this test
    engine3 = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine3)
    SessionLocal3 = sessionmaker(autocommit=False, autoflush=False, bind=engine3)
    db3 = SessionLocal3()

    create_test_accounts_full(db3)

    try:
        entry3 = create_expense_payment_journal_entry(db3, data_error)
        print("Test failed: Should have raised ValueError for missing potongan_biaya_code")
        db3.close()
        return False
    except ValueError as e:
        print(f"Test passed: Correctly raised ValueError: {e}")
    except Exception as e:
        print(f"Test failed: Unexpected error: {e}")
        db3.close()
        return False

    db3.close()
    return True

if __name__ == "__main__":
    success = test_create_expense_payment_journal_entry()
    if success:
        print("All tests passed!")
    else:
        print("Some tests failed!")
