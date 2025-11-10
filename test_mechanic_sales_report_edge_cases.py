from datetime import date
from services.services_accounting import generate_mechanic_sales_report
from schemas.service_accounting import MechanicSalesReportRequest
from models.database import get_db
from sqlalchemy.orm import Session

# Get a database session
db: Session = next(get_db())

# Test 1: Single day (2025-11-09)
print("Test 1: Single day 2025-11-09")
request1 = MechanicSalesReportRequest(
    start_date=date(2025, 11, 9),
    end_date=date(2025, 11, 9)
)
try:
    report1 = generate_mechanic_sales_report(db, request1)
    print(f'Total Product Sales: {report1.total_product_sales}')
    print(f'Total Service Sales: {report1.total_service_sales}')
    print(f'Total Sales: {report1.total_sales}')
    print(f'Number of Items: {len(report1.items)}')
    for item in report1.items:
        print(f'Mechanic: {item.mechanic_name}, Date: {item.date}, Total: {item.total_sales}')
except Exception as e:
    print(f'Error: {e}')

print("\n" + "="*50 + "\n")

# Test 2: Date range with no data (future date)
print("Test 2: Future date range 2026-01-01 to 2026-01-31")
request2 = MechanicSalesReportRequest(
    start_date=date(2026, 1, 1),
    end_date=date(2026, 1, 31)
)
try:
    report2 = generate_mechanic_sales_report(db, request2)
    print(f'Total Product Sales: {report2.total_product_sales}')
    print(f'Total Service Sales: {report2.total_service_sales}')
    print(f'Total Sales: {report2.total_sales}')
    print(f'Number of Items: {len(report2.items)}')
except Exception as e:
    print(f'Error: {e}')

print("\n" + "="*50 + "\n")

# Test 3: Wider date range (2025-11-01 to 2025-12-31)
print("Test 3: Wider date range 2025-11-01 to 2025-12-31")
request3 = MechanicSalesReportRequest(
    start_date=date(2025, 11, 1),
    end_date=date(2025, 12, 31)
)
try:
    report3 = generate_mechanic_sales_report(db, request3)
    print(f'Total Product Sales: {report3.total_product_sales}')
    print(f'Total Service Sales: {report3.total_service_sales}')
    print(f'Total Sales: {report3.total_sales}')
    print(f'Number of Items: {len(report3.items)}')
    # Show only first 5 items if many
    for item in report3.items[:5]:
        print(f'Mechanic: {item.mechanic_name}, Date: {item.date}, Total: {item.total_sales}')
    if len(report3.items) > 5:
        print(f'... and {len(report3.items) - 5} more items')
except Exception as e:
    print(f'Error: {e}')
