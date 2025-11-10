from datetime import date
from services.services_accounting import generate_mechanic_sales_report
from schemas.service_accounting import MechanicSalesReportRequest
from models.database import get_db
from sqlalchemy.orm import Session

# Get a database session
db: Session = next(get_db())

# Create the request for a date range, e.g., 2025-11-01 to 2025-11-30
request = MechanicSalesReportRequest(
    start_date=date(2025, 11, 1),
    end_date=date(2025, 11, 30)
)

try:
    report = generate_mechanic_sales_report(db, request)
    print('Mechanic sales report generated successfully')
    print(f'Total Product Sales: {report.total_product_sales}')
    print(f'Total Service Sales: {report.total_service_sales}')
    print(f'Total Sales: {report.total_sales}')
    print(f'Number of Items: {len(report.items)}')
    for item in report.items:
        print(f'Mechanic: {item.mechanic_name}, Date: {item.date}, Product Sales: {item.total_product_sales}, Service Sales: {item.total_service_sales}, Total: {item.total_sales}')
except Exception as e:
    print(f'Error: {e}')
    import traceback
    traceback.print_exc()
