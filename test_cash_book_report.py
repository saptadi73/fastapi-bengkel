import sys
import os
import uuid
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from datetime import date
from decimal import Decimal
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models.accounting import Base, Account, JournalEntry, JournalLine
from schemas.service_accounting import JournalType
from services.services_accounting import generate_cash_book_report
from schemas.service_accounting import CashBookReportRequest

# Create in-memory SQLite database for testing
engine = create_engine("sqlite:///:memory:")
Base.metadata.create_all(engine)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def create_test_accounts_and_entries(db):
    # Create test accounts
    kas_account = Account(id=uuid.uuid4(), code="1100", name="Kas", normal_balance="debit", account_type="asset", is_active=True)
    db.add(kas_account)

    revenue_account = Account(id=uuid.uuid4(), code="4100", name="Pendapatan Lain", normal_balance="credit", account_type="revenue", is_active=True)
    db.add(revenue_account)

    expense_account = Account(id=uuid.uuid4(), code="5100", name="Biaya Lain", normal_balance="debit", account_type="expense", is_active=True)
    db.add(expense_account)

    db.commit()

    # Create some journal entries for the kas account
    # Entry 1: Cash in (debit kas)
    entry1 = JournalEntry(
        id=uuid.uuid4(),
        entry_no="GEN-20240101-001",
        date=date(2024, 1, 1),
        memo="Cash in",
        journal_type=JournalType.GENERAL,
        created_by="test"
    )
    db.add(entry1)
    db.flush()

    line1_debit = JournalLine(
        id=uuid.uuid4(),
        entry_id=entry1.id,
        account_id=kas_account.id,
        description="Cash in",
        debit=Decimal("100000.00"),
        credit=Decimal("0.00")
    )
    db.add(line1_debit)

    line1_credit = JournalLine(
        id=uuid.uuid4(),
        entry_id=entry1.id,
        account_id=revenue_account.id,
        description="Cash in",
        debit=Decimal("0.00"),
        credit=Decimal("100000.00")
    )
    db.add(line1_credit)

    # Entry 2: Cash out (credit kas)
    entry2 = JournalEntry(
        id=uuid.uuid4(),
        entry_no="GEN-20240102-001",
        date=date(2024, 1, 2),
        memo="Cash out",
        journal_type=JournalType.GENERAL,
        created_by="test"
    )
    db.add(entry2)
    db.flush()

    line2_debit = JournalLine(
        id=uuid.uuid4(),
        entry_id=entry2.id,
        account_id=expense_account.id,
        description="Cash out",
        debit=Decimal("50000.00"),
        credit=Decimal("0.00")
    )
    db.add(line2_debit)

    line2_credit = JournalLine(
        id=uuid.uuid4(),
        entry_id=entry2.id,
        account_id=kas_account.id,
        description="Cash out",
        debit=Decimal("0.00"),
        credit=Decimal("50000.00")
    )
    db.add(line2_credit)

    # Entry 3: Before start date (should affect opening balance)
    entry3 = JournalEntry(
        id=uuid.uuid4(),
        entry_no="GEN-20231231-001",
        date=date(2023, 12, 31),
        memo="Cash in before period",
        journal_type=JournalType.GENERAL,
        created_by="test"
    )
    db.add(entry3)
    db.flush()

    line3_debit = JournalLine(
        id=uuid.uuid4(),
        entry_id=entry3.id,
        account_id=kas_account.id,
        description="Cash in before",
        debit=Decimal("20000.00"),
        credit=Decimal("0.00")
    )
    db.add(line3_debit)

    line3_credit = JournalLine(
        id=uuid.uuid4(),
        entry_id=entry3.id,
        account_id=revenue_account.id,
        description="Cash in before",
        debit=Decimal("0.00"),
        credit=Decimal("20000.00")
    )
    db.add(line3_credit)

    db.commit()

    return kas_account.id

def test_generate_cash_book_report():
    # Create new engine for this test
    engine1 = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine1)
    SessionLocal1 = sessionmaker(autocommit=False, autoflush=False, bind=engine1)
    db1 = SessionLocal1()

    account_id = create_test_accounts_and_entries(db1)

    # Test request
    request = CashBookReportRequest(
        account_id=account_id,
        start_date=date(2024, 1, 1),
        end_date=date(2024, 1, 31)
    )

    try:
        report = generate_cash_book_report(db1, request)
        print("Test passed: Cash book report generated successfully")
        print(f"Opening Balance: {report.opening_balance}")
        print(f"Number of Entries: {len(report.entries)}")

        # Check opening balance (from entry3)
        assert report.opening_balance == Decimal("20000.00"), f"Expected opening balance 20000, got {report.opening_balance}"

        # Check entries
        assert len(report.entries) == 2, f"Expected 2 entries, got {len(report.entries)}"

        # First entry (cash in)
        entry1 = report.entries[0]
        assert entry1.date == date(2024, 1, 1), f"Expected date 2024-01-01, got {entry1.date}"
        assert entry1.debit == Decimal("100000.00"), f"Expected debit 100000, got {entry1.debit}"
        assert entry1.credit == Decimal("0.00"), f"Expected credit 0, got {entry1.credit}"
        assert entry1.balance == Decimal("120000.00"), f"Expected balance 120000, got {entry1.balance}"

        # Second entry (cash out)
        entry2 = report.entries[1]
        assert entry2.date == date(2024, 1, 2), f"Expected date 2024-01-02, got {entry2.date}"
        assert entry2.debit == Decimal("0.00"), f"Expected debit 0, got {entry2.debit}"
        assert entry2.credit == Decimal("50000.00"), f"Expected credit 50000, got {entry2.credit}"
        assert entry2.balance == Decimal("70000.00"), f"Expected balance 70000, got {entry2.balance}"

        print("All checks passed")
    except Exception as e:
        print(f"Test failed: {e}")
        db1.close()
        return False

    db1.close()
    return True

if __name__ == "__main__":
    success = test_generate_cash_book_report()
    if success:
        print("Test passed!")
    else:
        print("Test failed!")
