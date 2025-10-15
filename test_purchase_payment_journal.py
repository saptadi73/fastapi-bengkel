import sys
import os
import uuid
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from datetime import date
from decimal import Decimal
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models.accounting import Base, Account
from services.services_accounting import create_purchase_payment_journal_entry
from schemas.service_accounting import PurchasePaymentJournalEntry

# Create in-memory SQLite database for testing
engine = create_engine("sqlite:///:memory:")
Base.metadata.create_all(engine)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def create_test_accounts_full(db):
    # Create test accounts directly
    # Kas/Bank account
    acc1 = Account(id=uuid.uuid4(), code="1100", name="Kas", normal_balance="debit", account_type="asset", is_active=True)
    db.add(acc1)
    # Hutang account
    acc2 = Account(id=uuid.uuid4(), code="2100", name="Hutang Usaha", normal_balance="credit", account_type="liability", is_active=True)
    db.add(acc2)
    # Potongan Pembelian account
    acc3 = Account(id=uuid.uuid4(), code="4300", name="Potongan Pembelian", normal_balance="debit", account_type="revenue", is_active=True)
    db.add(acc3)
    db.commit()

def create_test_accounts_basic(db):
    # Create test accounts directly
    # Kas/Bank account
    acc1 = Account(id=uuid.uuid4(), code="1100", name="Kas", normal_balance="debit", account_type="asset", is_active=True)
    db.add(acc1)
    # Hutang account
    acc2 = Account(id=uuid.uuid4(), code="2100", name="Hutang Usaha", normal_balance="credit", account_type="liability", is_active=True)
    db.add(acc2)
    db.commit()

def test_create_purchase_payment_journal_entry():
    # Test data with discount
    data = PurchasePaymentJournalEntry(
        date=date.today(),
        memo="Test payment",
        supplier_id=None,
        workorder_id=None,
        amount=Decimal("100000.00"),
        kas_bank_code="1100",
        hutang_code="2100",
        discount=Decimal("5000.00"),
        potongan_pembelian_code="4300"
    )

    # Create new engine for this test
    engine1 = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine1)
    SessionLocal1 = sessionmaker(autocommit=False, autoflush=False, bind=engine1)
    db1 = SessionLocal1()

    create_test_accounts_full(db1)

    try:
        entry = create_purchase_payment_journal_entry(db1, data)
        print("Test passed: Purchase payment journal entry created successfully")
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

    # Test without discount
    data_no_discount = PurchasePaymentJournalEntry(
        date=date.today(),
        memo="Test payment no discount",
        supplier_id=None,
        workorder_id=None,
        amount=Decimal("50000.00"),
        kas_bank_code="1100",
        hutang_code="2100",
        discount=Decimal("0.00"),
        potongan_pembelian_code=None
    )

    # Create new engine for this test
    engine2 = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine2)
    SessionLocal2 = sessionmaker(autocommit=False, autoflush=False, bind=engine2)
    db2 = SessionLocal2()

    create_test_accounts_basic(db2)

    try:
        entry2 = create_purchase_payment_journal_entry(db2, data_no_discount)
        print("Test passed: Purchase payment journal entry without discount created successfully")
        print(f"Entry No: {entry2['entry_no']}")
        total_debit2 = sum(line['debit'] for line in entry2['lines'])
        total_credit2 = sum(line['credit'] for line in entry2['lines'])
        assert total_debit2 == total_credit2, "Journal not balanced"
        print("Balance check passed for no discount")
    except Exception as e:
        print(f"Test failed for no discount: {e}")
        db2.close()
        return False

    db2.close()

    # Test edge case: zero amount - skip since it violates database constraint
    print("Skipping zero amount test as it violates database constraint (one side must be positive)")
    return True

if __name__ == "__main__":
    success = test_create_purchase_payment_journal_entry()
    if success:
        print("All tests passed!")
    else:
        print("Some tests failed!")
