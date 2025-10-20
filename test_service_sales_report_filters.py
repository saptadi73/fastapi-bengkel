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

def create_test_data(db):
    # Create test customers
    customer1 = Customer(
        id=uuid.uuid4(),
        nama="Customer A",
        hp="123456789",
        created_at=datetime.now(),
        updated_at=datetime.now()
    )
    customer2 = Customer(
        id=uuid.uuid4(),
        nama="Customer B",
        hp="987654321",
        created_at=datetime.now(),
        updated_at=datetime.now()
    )
    db.add(customer1)
    db.add(customer2)

    # Create test services
    service1 = Service(id=uuid.uuid4(), name="Service A")
    service2 = Service(id=uuid.uuid4(), name="Service B")
    db.add(service1)
    db.add(service2)

    # Create test workorders
    workorder1 = Workorder(
        id=uuid.uuid4(),
        no_wo="WO001",
        tanggal_masuk=datetime.now(),
        keluhan="Complaint 1",
        status="open",
        total_biaya=Decimal("100000.00"),
        customer_id=customer1.id
    )
    workorder2 = Workorder(
        id=uuid.uuid4(),
        no_wo="WO002",
        tanggal_masuk=datetime.now(),
        keluhan="Complaint 2",
        status="open",
        total_biaya=Decimal("200000.00"),
        customer_id=customer2.id
    )
    db.add(workorder1)
    db.add(workorder2)

    # Create test service ordered
    service_ordered1 = ServiceOrdered(
        id=uuid.uuid4(),
        workorder_id=workorder1.id,
        service_id=service1.id,
        quantity=Decimal("2.00"),
        price=Decimal("50000.00"),
        subtotal=Decimal("100000.00"),
        discount=Decimal("0.00")
    )
    service_ordered2 = ServiceOrdered(
        id=uuid.uuid4(),
        workorder_id=workorder2.id,
        service_id=service2.id,
        quantity=Decimal("1.00"),
        price=Decimal("200000.00"),
        subtotal=Decimal("200000.00"),
        discount=Decimal("0.00")
    )
    service_ordered3 = ServiceOrdered(
        id=uuid.uuid4(),
        workorder_id=workorder1.id,
        service_id=service2.id,
        quantity=Decimal("1.00"),
        price=Decimal("50000.00"),
        subtotal=Decimal("50000.00"),
        discount=Decimal("0.00")
    )
    db.add(service_ordered1)
    db.add(service_ordered2)
    db.add(service_ordered3)

    db.commit()
    return customer1.id, customer2.id, service1.id, service2.id

def test_generate_service_sales_report_with_filters():
    # Create new engine for this test
    engine1 = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine1)
    Base2.metadata.create_all(engine1)
    SessionLocal1 = sessionmaker(autocommit=False, autoflush=False, bind=engine1)
    db1 = SessionLocal1()

    customer1_id, customer2_id, service1_id, service2_id = create_test_data(db1)

    # Test 1: No filters - should return all
    request_all = ServiceSalesReportRequest(
        start_date=date.today(),
        end_date=date.today()
    )

    try:
        report_all = generate_service_sales_report(db1, request_all)
        print("Test 1 passed: All services report generated successfully")
        assert report_all.total_quantity == Decimal("4.00"), f"Expected quantity 4.00, got {report_all.total_quantity}"
        assert report_all.total_sales == Decimal("350000.00"), f"Expected sales 350000.00, got {report_all.total_sales}"
        assert len(report_all.items) == 3, f"Expected 3 items, got {len(report_all.items)}"
        print("All services assertions passed")
    except Exception as e:
        print(f"Test 1 failed: {e}")
        db1.close()
        return False

    # Test 2: Filter by service_id (service1)
    request_service1 = ServiceSalesReportRequest(
        start_date=date.today(),
        end_date=date.today(),
        service_id=service1_id
    )

    try:
        report_service1 = generate_service_sales_report(db1, request_service1)
        print("Test 2 passed: Service1 filtered report generated successfully")
        assert report_service1.total_quantity == Decimal("2.00"), f"Expected quantity 2.00, got {report_service1.total_quantity}"
        assert report_service1.total_sales == Decimal("100000.00"), f"Expected sales 100000.00, got {report_service1.total_sales}"
        assert len(report_service1.items) == 1, f"Expected 1 item, got {len(report_service1.items)}"
        assert report_service1.items[0].service_name == "Service A", f"Expected Service A, got {report_service1.items[0].service_name}"
        print("Service1 filter assertions passed")
    except Exception as e:
        print(f"Test 2 failed: {e}")
        db1.close()
        return False

    # Test 3: Filter by customer_id (customer1)
    request_customer1 = ServiceSalesReportRequest(
        start_date=date.today(),
        end_date=date.today(),
        customer_id=customer1_id
    )

    try:
        report_customer1 = generate_service_sales_report(db1, request_customer1)
        print("Test 3 passed: Customer1 filtered report generated successfully")
        assert report_customer1.total_quantity == Decimal("3.00"), f"Expected quantity 3.00, got {report_customer1.total_quantity}"
        assert report_customer1.total_sales == Decimal("150000.00"), f"Expected sales 150000.00, got {report_customer1.total_sales}"
        assert len(report_customer1.items) == 2, f"Expected 2 items, got {len(report_customer1.items)}"
        assert all(item.customer_name == "Customer A" for item in report_customer1.items), "All items should be for Customer A"
        print("Customer1 filter assertions passed")
    except Exception as e:
        print(f"Test 3 failed: {e}")
        db1.close()
        return False

    # Test 4: Filter by both service_id and customer_id
    request_both = ServiceSalesReportRequest(
        start_date=date.today(),
        end_date=date.today(),
        service_id=service2_id,
        customer_id=customer1_id
    )

    try:
        report_both = generate_service_sales_report(db1, request_both)
        print("Test 4 passed: Both filters report generated successfully")
        assert report_both.total_quantity == Decimal("1.00"), f"Expected quantity 1.00, got {report_both.total_quantity}"
        assert report_both.total_sales == Decimal("50000.00"), f"Expected sales 50000.00, got {report_both.total_sales}"
        assert len(report_both.items) == 1, f"Expected 1 item, got {len(report_both.items)}"
        assert report_both.items[0].service_name == "Service B", f"Expected Service B, got {report_both.items[0].service_name}"
        assert report_both.items[0].customer_name == "Customer A", f"Expected Customer A, got {report_both.items[0].customer_name}"
        print("Both filters assertions passed")
    except Exception as e:
        print(f"Test 4 failed: {e}")
        db1.close()
        return False

    # Test 5: Filter by non-existent service_id
    non_existent_service_id = uuid.uuid4()
    request_non_existent = ServiceSalesReportRequest(
        start_date=date.today(),
        end_date=date.today(),
        service_id=non_existent_service_id
    )

    try:
        report_non_existent = generate_service_sales_report(db1, request_non_existent)
        print("Test 5 passed: Non-existent service filter report generated successfully")
        assert report_non_existent.total_quantity == Decimal("0.00"), f"Expected quantity 0.00, got {report_non_existent.total_quantity}"
        assert report_non_existent.total_sales == Decimal("0.00"), f"Expected sales 0.00, got {report_non_existent.total_sales}"
        assert len(report_non_existent.items) == 0, f"Expected 0 items, got {len(report_non_existent.items)}"
        print("Non-existent service filter assertions passed")
    except Exception as e:
        print(f"Test 5 failed: {e}")
        db1.close()
        return False

    db1.close()
    return True

if __name__ == "__main__":
    success = test_generate_service_sales_report_with_filters()
    if success:
        print("All filter tests passed!")
    else:
        print("Some filter tests failed!")
