import sys
import os
import uuid
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from datetime import date
from decimal import Decimal
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models.accounting import Base, Account
from services.services_accounting import cash_in, cash_out
from schemas.service_accounting import CashInCreate, CashOutCreate

# Create in-memory SQLite database for testing
engine = create_engine("sqlite:///:memory:")
Base.metadata.create_all(engine)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def create_test_accounts_full(db):
    # Create test accounts directly
    # Kas/Bank account
    acc1 = Account(id=uuid.uuid4(), code="1100", name="Kas", normal_balance="debit", account_type="asset", is_active=True)
    db.add(acc1)
    # Specified account for credit (e.g., Pendapatan Lain)
    acc2 = Account(id=uuid.uuid4(), code="4100", name="Pendapatan Lain", normal_balance="credit", account_type="revenue", is_active=True)
    db.add(acc2)
    # Specified account for debit (e.g., Biaya Lain)
    acc3 = Account(id=uuid.uuid4(), code="5100", name="Biaya Lain", normal_balance="debit", account_type="expense", is_active=True)
    db.add(acc3)
    db.commit()

def test_cash_in():
    # Test data for cash_in
    data = CashInCreate(
        entry_no="GEN-20240101-001",
        tanggal=date.today(),
        memo="Test cash in",
        kas_bank_code="1100",
        credit_account_code="4100",
        amount=Decimal("100000.00"),
        created_by="test_user"
    )

    # Create new engine for this test
    engine1 = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine1)
    SessionLocal1 = sessionmaker(autocommit=False, autoflush=False, bind=engine1)
    db1 = SessionLocal1()

    create_test_accounts_full(db1)

    try:
        entry = cash_in(db1, cash_in_data=data)
        print("Test passed: Cash in journal entry created successfully")
        print(f"Entry No: {entry['entry_no']}")
        print(f"Total Lines: {len(entry['lines'])}")
        total_debit = sum(line['debit'] for line in entry['lines'])
        total_credit = sum(line['credit'] for line in entry['lines'])
        print(f"Total Debit: {total_debit}, Total Credit: {total_credit}")
        assert total_debit == total_credit, "Journal not balanced"
        assert total_debit == Decimal("100000.00"), "Debit amount incorrect"
        assert total_credit == Decimal("100000.00"), "Credit amount incorrect"
        print("Balance and amount checks passed")
    except Exception as e:
        print(f"Test failed: {e}")
        db1.close()
        return False

    db1.close()
    return True

def test_cash_out():
    # Test data for cash_out
    data = CashOutCreate(
        entry_no="GEN-20240101-002",
        tanggal=date.today(),
        memo="Test cash out",
        debit_account_code="5100",
        kas_bank_code="1100",
        amount=Decimal("50000.00"),
        created_by="test_user"
    )

    # Create new engine for this test
    engine2 = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine2)
    SessionLocal2 = sessionmaker(autocommit=False, autoflush=False, bind=engine2)
    db2 = SessionLocal2()

    create_test_accounts_full(db2)

    try:
        entry = cash_out(db2, cash_out_data=data)
        print("Test passed: Cash out journal entry created successfully")
        print(f"Entry No: {entry['entry_no']}")
        print(f"Total Lines: {len(entry['lines'])}")
        total_debit = sum(line['debit'] for line in entry['lines'])
        total_credit = sum(line['credit'] for line in entry['lines'])
        print(f"Total Debit: {total_debit}, Total Credit: {total_credit}")
        assert total_debit == total_credit, "Journal not balanced"
        assert total_debit == Decimal("50000.00"), "Debit amount incorrect"
        assert total_credit == Decimal("50000.00"), "Credit amount incorrect"
        print("Balance and amount checks passed")
    except Exception as e:
        print(f"Test failed: {e}")
        db2.close()
        return False

    db2.close()
    return True

if __name__ == "__main__":
    success1 = test_cash_in()
    success2 = test_cash_out()
    if success1 and success2:
        print("All tests passed!")
    else:
        print("Some tests failed!")
