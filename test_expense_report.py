import sys
import os
import uuid
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from datetime import date, datetime
from decimal import Decimal
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models.expenses import Base, Expenses, ExpenseType, ExpenseStatus
from services.services_accounting import generate_expense_report
from schemas.service_accounting import ExpenseReportRequest

# Create in-memory SQLite database for testing
engine = create_engine("sqlite:///:memory:")
Base.metadata.create_all(engine)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def create_test_expenses(db):
    # Create test expenses
    exp1 = Expenses(
        id=uuid.uuid4(),
        name="Electricity Bill",
        date=date(2023, 10, 1),
        amount=Decimal("100.00"),
        expense_type=ExpenseType.listrik,
        status=ExpenseStatus.dibayarkan,
        description="Electricity bill",
        created_at=datetime.now(),
        updated_at=datetime.now()
    )
    exp2 = Expenses(
        id=uuid.uuid4(),
        name="Water Bill",
        date=date(2023, 10, 5),
        amount=Decimal("200.00"),
        expense_type=ExpenseType.air,
        status=ExpenseStatus.dibayarkan,
        description="Water bill",
        created_at=datetime.now(),
        updated_at=datetime.now()
    )
    exp3 = Expenses(
        id=uuid.uuid4(),
        name="Another Electricity Bill",
        date=date(2023, 10, 10),
        amount=Decimal("150.00"),
        expense_type=ExpenseType.listrik,
        status=ExpenseStatus.dibayarkan,
        description="Another electricity bill",
        created_at=datetime.now(),
        updated_at=datetime.now()
    )

    db.add_all([exp1, exp2, exp3])
    db.commit()

def test_generate_expense_report_basic():
    # Create new engine for this test
    engine1 = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine1)
    SessionLocal1 = sessionmaker(autocommit=False, autoflush=False, bind=engine1)
    db1 = SessionLocal1()

    create_test_expenses(db1)

    # Generate report
    request = ExpenseReportRequest(
        start_date=date(2023, 10, 1),
        end_date=date(2023, 10, 31)
    )
    report = generate_expense_report(db1, request)

    # Assertions
    from schemas.service_accounting import ExpenseReport
    assert isinstance(report, ExpenseReport)
    assert report.total_expenses == Decimal("450.00")
    assert report.total_count == 3
    assert len(report.items) == 2  # Two expense types

    # Check items
    expense_types = {item.expense_type: item for item in report.items}
    assert "listrik" in expense_types
    assert "air" in expense_types

    listrik_item = expense_types["listrik"]
    assert listrik_item.total_amount == Decimal("250.00")
    assert listrik_item.count == 2

    air_item = expense_types["air"]
    assert air_item.total_amount == Decimal("200.00")
    assert air_item.count == 1

    db1.close()


def test_generate_expense_report_with_filters():
    # Create new engine for this test
    engine1 = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine1)
    SessionLocal1 = sessionmaker(autocommit=False, autoflush=False, bind=engine1)
    db1 = SessionLocal1()

    # Create test expenses
    exp1 = Expenses(
        id=uuid.uuid4(),
        name="Electricity Bill",
        date=date(2023, 10, 1),
        amount=Decimal("100.00"),
        expense_type=ExpenseType.listrik,
        status=ExpenseStatus.dibayarkan,
        description="Electricity bill",
        created_at=datetime.now(),
        updated_at=datetime.now()
    )
    exp2 = Expenses(
        id=uuid.uuid4(),
        name="Water Bill",
        date=date(2023, 10, 5),
        amount=Decimal("200.00"),
        expense_type=ExpenseType.air,
        status=ExpenseStatus.open,
        description="Water bill",
        created_at=datetime.now(),
        updated_at=datetime.now()
    )
    exp3 = Expenses(
        id=uuid.uuid4(),
        name="Another Electricity Bill",
        date=date(2023, 10, 10),
        amount=Decimal("150.00"),
        expense_type=ExpenseType.listrik,
        status=ExpenseStatus.dibayarkan,
        description="Another electricity bill",
        created_at=datetime.now(),
        updated_at=datetime.now()
    )

    db1.add_all([exp1, exp2, exp3])
    db1.commit()

    # Generate report with filters
    request = ExpenseReportRequest(
        start_date=date(2023, 10, 1),
        end_date=date(2023, 10, 31),
        expense_type="listrik",
        status="dibayarkan"
    )
    report = generate_expense_report(db1, request)

    # Assertions
    assert report.total_expenses == Decimal("250.00")
    assert report.total_count == 2
    assert len(report.items) == 1

    item = report.items[0]
    assert item.expense_type == "listrik"
    assert item.total_amount == Decimal("250.00")
    assert item.count == 2

    db1.close()


def test_generate_expense_report_no_expenses():
    # Create new engine for this test
    engine1 = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine1)
    SessionLocal1 = sessionmaker(autocommit=False, autoflush=False, bind=engine1)
    db1 = SessionLocal1()

    request = ExpenseReportRequest(
        start_date=date(2023, 10, 1),
        end_date=date(2023, 10, 31)
    )
    report = generate_expense_report(db1, request)

    assert report.total_expenses == Decimal("0.00")
    assert report.total_count == 0
    assert len(report.items) == 0

    db1.close()


def test_generate_expense_report_date_range():
    # Create new engine for this test
    engine1 = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine1)
    SessionLocal1 = sessionmaker(autocommit=False, autoflush=False, bind=engine1)
    db1 = SessionLocal1()

    # Create test expenses
    exp1 = Expenses(
        id=uuid.uuid4(),
        name="Before Range Bill",
        date=date(2023, 9, 30),
        amount=Decimal("100.00"),
        expense_type=ExpenseType.listrik,
        status=ExpenseStatus.dibayarkan,
        description="Before range",
        created_at=datetime.now(),
        updated_at=datetime.now()
    )
    exp2 = Expenses(
        id=uuid.uuid4(),
        name="In Range Bill",
        date=date(2023, 10, 1),
        amount=Decimal("200.00"),
        expense_type=ExpenseType.air,
        status=ExpenseStatus.dibayarkan,
        description="In range",
        created_at=datetime.now(),
        updated_at=datetime.now()
    )
    exp3 = Expenses(
        id=uuid.uuid4(),
        name="After Range Bill",
        date=date(2023, 11, 1),
        amount=Decimal("150.00"),
        expense_type=ExpenseType.listrik,
        status=ExpenseStatus.dibayarkan,
        description="After range",
        created_at=datetime.now(),
        updated_at=datetime.now()
    )

    db1.add_all([exp1, exp2, exp3])
    db1.commit()

    # Generate report
    request = ExpenseReportRequest(
        start_date=date(2023, 10, 1),
        end_date=date(2023, 10, 31)
    )
    report = generate_expense_report(db1, request)

    assert report.total_expenses == Decimal("200.00")
    assert report.total_count == 1
    assert len(report.items) == 1

    item = report.items[0]
    assert item.expense_type == "air"
    assert item.total_amount == Decimal("200.00")
    assert item.count == 1

    db1.close()


if __name__ == "__main__":
    test_generate_expense_report_basic()
    test_generate_expense_report_with_filters()
    test_generate_expense_report_no_expenses()
    test_generate_expense_report_date_range()
    print("All tests passed!")
