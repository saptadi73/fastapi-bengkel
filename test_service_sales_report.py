import sys
import os
import uuid
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from datetime import date, datetime
from decimal import Decimal
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models.accounting import Base
from models.database import Base as Base2
from models.customer import Customer
from models.workorder import Workorder, ServiceOrdered, Service
from services.services_accounting import generate_service_sales_report
from schemas.service_accounting import ServiceSalesReportRequest

# Create in-memory SQLite database for testing
engine = create_engine("sqlite:///:memory:")
Base.metadata.create_all(engine)
Base2.metadata.create_all(engine)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Mock the now() function for SQLite
from sqlalchemy import text
with engine.connect() as conn:
    conn.execute(text("CREATE TEMP VIEW now_view AS SELECT datetime('now') AS now"))
    conn.commit()

def create_test_data(db):
    # Create test customer
    customer = Customer(
        id=uuid.uuid4(),
        nama="Test Customer",
        hp="123456789",
        created_at=datetime.now(),
        updated_at=datetime.now()
    )
    db.add(customer)

    # Create test service
    service = Service(id=uuid.uuid4(), name="Test Service")
    db.add(service)

    # Create test workorder
    workorder = Workorder(
        id=uuid.uuid4(),
        no_wo="WO001",
        tanggal_masuk=datetime.now(),
        keluhan="Test complaint",
        status="open",
        total_biaya=Decimal("100000.00"),
        customer_id=customer.id
    )
    db.add(workorder)

    # Create test service ordered
    service_ordered = ServiceOrdered(
        id=uuid.uuid4(),
        workorder_id=workorder.id,
        service_id=service.id,
        quantity=Decimal("2.00"),
        price=Decimal("50000.00"),
        subtotal=Decimal("100000.00"),
        discount=Decimal("5000.00")
    )
    db.add(service_ordered)

    db.commit()

def test_generate_service_sales_report():
    # Create new engine for this test
    engine1 = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine1)
    Base2.metadata.create_all(engine1)
    SessionLocal1 = sessionmaker(autocommit=False, autoflush=False, bind=engine1)
    db1 = SessionLocal1()

    create_test_data(db1)

    # Test request
    request = ServiceSalesReportRequest(
        start_date=date.today(),
        end_date=date.today()
    )

    try:
        report = generate_service_sales_report(db1, request)
        print("Test passed: Service sales report generated successfully")
        print(f"Total Quantity: {report.total_quantity}")
        print(f"Total Sales: {report.total_sales}")
        print(f"Number of Items: {len(report.items)}")
        assert report.total_quantity == Decimal("2.00"), f"Expected quantity 2.00, got {report.total_quantity}"
        assert report.total_sales == Decimal("100000.00"), f"Expected sales 100000.00, got {report.total_sales}"
        assert len(report.items) == 1, f"Expected 1 item, got {len(report.items)}"
        item = report.items[0]
        assert item.workorder_no == "WO001", f"Expected WO001, got {item.workorder_no}"
        assert item.customer_name == "Test Customer", f"Expected Test Customer, got {item.customer_name}"
        assert item.service_name == "Test Service", f"Expected Test Service, got {item.service_name}"
        assert item.quantity == Decimal("2.00"), f"Expected 2.00, got {item.quantity}"
        assert item.price == Decimal("50000.00"), f"Expected 50000.00, got {item.price}"
        assert item.subtotal == Decimal("100000.00"), f"Expected 100000.00, got {item.subtotal}"
        assert item.discount == Decimal("5000.00"), f"Expected 5000.00, got {item.discount}"
        print("All assertions passed")
    except Exception as e:
        print(f"Test failed: {e}")
        db1.close()
        return False

    db1.close()

    # Test edge case: no data
    engine2 = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine2)
    Base2.metadata.create_all(engine2)
    SessionLocal2 = sessionmaker(autocommit=False, autoflush=False, bind=engine2)
    db2 = SessionLocal2()

    request_empty = ServiceSalesReportRequest(
        start_date=date.today(),
        end_date=date.today()
    )

    try:
        report_empty = generate_service_sales_report(db2, request_empty)
        print("Test passed: Empty report generated successfully")
        assert report_empty.total_quantity == Decimal("0.00"), f"Expected 0.00, got {report_empty.total_quantity}"
        assert report_empty.total_sales == Decimal("0.00"), f"Expected 0.00, got {report_empty.total_sales}"
        assert len(report_empty.items) == 0, f"Expected 0 items, got {len(report_empty.items)}"
        print("Empty report assertions passed")
    except Exception as e:
        print(f"Test failed for empty data: {e}")
        db2.close()
        return False

    db2.close()
    return True

if __name__ == "__main__":
    success = test_generate_service_sales_report()
    if success:
        print("All tests passed!")
    else:
        print("Some tests failed!")
