import sys
import os
import uuid
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from datetime import date
from decimal import Decimal
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models.accounting import Base, Account, JournalEntry, JournalLine
from models.customer import Customer
from models.supplier import Supplier
from schemas.service_accounting import JournalType
from services.services_accounting import generate_receivable_payable_report
from schemas.service_accounting import ReceivablePayableReportRequest

# Create in-memory SQLite database for testing
engine = create_engine("sqlite:///:memory:")
Base.metadata.create_all(engine)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def create_test_data(db):
    # Create test accounts
    piutang_account = Account(id=uuid.uuid4(), code="2001", name="Piutang Usaha", normal_balance="debit", account_type="asset", is_active=True)
    hutang_account = Account(id=uuid.uuid4(), code="3001", name="Hutang Usaha", normal_balance="credit", account_type="liability", is_active=True)
    db.add(piutang_account)
    db.add(hutang_account)

    # Create test customers and suppliers
    customer1 = Customer(id=uuid.uuid4(), nama="Customer A", hp="123456789", alamat="Address A", created_at=date.today(), updated_at=date.today())
    customer2 = Customer(id=uuid.uuid4(), nama="Customer B", hp="987654321", alamat="Address B", created_at=date.today(), updated_at=date.today())
    supplier1 = Supplier(id=uuid.uuid4(), nama="Supplier X", hp="111222333", alamat="Address X", created_at=date.today(), updated_at=date.today())
    db.add(customer1)
    db.add(customer2)
    db.add(supplier1)

    db.commit()

    # Create journal entries for receivables (sales)
    # Sale to customer1: debit piutang 100000
    entry1 = JournalEntry(
        id=uuid.uuid4(),
        entry_no="SAL-20240101-001",
        date=date(2024, 1, 1),
        memo="Sale to Customer A",
        journal_type=JournalType.SALE,
        customer_id=customer1.id,
        created_by="test"
    )
    db.add(entry1)
    db.flush()

    line1_debit = JournalLine(
        id=uuid.uuid4(),
        entry_id=entry1.id,
        account_id=piutang_account.id,
        description="Piutang Penjualan",
        debit=Decimal("100000.00"),
        credit=Decimal("0.00")
    )
    db.add(line1_debit)

    # Sale to customer2: debit piutang 50000
    entry2 = JournalEntry(
        id=uuid.uuid4(),
        entry_no="SAL-20240102-001",
        date=date(2024, 1, 2),
        memo="Sale to Customer B",
        journal_type=JournalType.SALE,
        customer_id=customer2.id,
        created_by="test"
    )
    db.add(entry2)
    db.flush()

    line2_debit = JournalLine(
        id=uuid.uuid4(),
        entry_id=entry2.id,
        account_id=piutang_account.id,
        description="Piutang Penjualan",
        debit=Decimal("50000.00"),
        credit=Decimal("0.00")
    )
    db.add(line2_debit)

    # Create journal entries for payables (purchases)
    # Purchase from supplier1: credit hutang 80000
    entry3 = JournalEntry(
        id=uuid.uuid4(),
        entry_no="PUR-20240103-001",
        date=date(2024, 1, 3),
        memo="Purchase from Supplier X",
        journal_type=JournalType.PURCHASE,
        supplier_id=supplier1.id,
        created_by="test"
    )
    db.add(entry3)
    db.flush()

    line3_credit = JournalLine(
        id=uuid.uuid4(),
        entry_id=entry3.id,
        account_id=hutang_account.id,
        description="Hutang Pembelian",
        debit=Decimal("0.00"),
        credit=Decimal("80000.00")
    )
    db.add(line3_credit)

    db.commit()

    return customer1.id, customer2.id, supplier1.id

def test_generate_receivable_payable_report():
    # Create new engine for this test
    engine1 = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine1)
    SessionLocal1 = sessionmaker(autocommit=False, autoflush=False, bind=engine1)
    db1 = SessionLocal1()

    customer1_id, customer2_id, supplier1_id = create_test_data(db1)

    # Test request
    request = ReceivablePayableReportRequest(
        start_date=date(2024, 1, 1),
        end_date=date(2024, 1, 31)
    )

    try:
        report = generate_receivable_payable_report(db1, request)
        print("Test passed: Receivable payable report generated successfully")
        print(f"Total Receivable: {report.total_receivable}")
        print(f"Total Payable: {report.total_payable}")
        print(f"Net Balance: {report.net_balance}")
        print(f"Number of Items: {len(report.items)}")

        # Check totals
        assert report.total_receivable == Decimal("150000.00"), f"Expected total receivable 150000, got {report.total_receivable}"
        assert report.total_payable == Decimal("80000.00"), f"Expected total payable 80000, got {report.total_payable}"
        assert report.net_balance == Decimal("70000.00"), f"Expected net balance 70000, got {report.net_balance}"

        # Check items
        assert len(report.items) == 3, f"Expected 3 items, got {len(report.items)}"

        # Find items by entity_id
        customer1_item = next((item for item in report.items if item.entity_id == str(customer1_id)), None)
        customer2_item = next((item for item in report.items if item.entity_id == str(customer2_id)), None)
        supplier1_item = next((item for item in report.items if item.entity_id == str(supplier1_id)), None)

        assert customer1_item is not None, "Customer1 item not found"
        assert customer1_item.total_receivable == Decimal("100000.00"), f"Customer1 receivable expected 100000, got {customer1_item.total_receivable}"
        assert customer1_item.balance == Decimal("100000.00"), f"Customer1 balance expected 100000, got {customer1_item.balance}"

        assert customer2_item is not None, "Customer2 item not found"
        assert customer2_item.total_receivable == Decimal("50000.00"), f"Customer2 receivable expected 50000, got {customer2_item.total_receivable}"
        assert customer2_item.balance == Decimal("50000.00"), f"Customer2 balance expected 50000, got {customer2_item.balance}"

        assert supplier1_item is not None, "Supplier1 item not found"
        assert supplier1_item.total_payable == Decimal("80000.00"), f"Supplier1 payable expected 80000, got {supplier1_item.total_payable}"
        assert supplier1_item.balance == Decimal("-80000.00"), f"Supplier1 balance expected -80000, got {supplier1_item.balance}"

        print("All checks passed")
    except Exception as e:
        print(f"Test failed: {e}")
        db1.close()
        return False

    db1.close()
    return True

if __name__ == "__main__":
    success = test_generate_receivable_payable_report()
    if success:
        print("Test passed!")
    else:
        print("Test failed!")
