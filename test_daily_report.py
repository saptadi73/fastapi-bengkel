from datetime import date
from services.services_accounting import generate_daily_report
from schemas.service_accounting import DailyReportRequest
from models.database import get_db
from sqlalchemy.orm import Session

# Get a database session
db: Session = next(get_db())

# Create the request for 2025-11-09
request = DailyReportRequest(date=date(2025, 11, 9))

try:
    report = generate_daily_report(db, request)
    print('Report generated successfully')
    print(f'Date: {report.date}')
    print(f'Cash Books Count: {len(report.cash_books)}')
    if report.cash_books:
        print(f'First Cash Book Opening Balance: {report.cash_books[0].opening_balance}')
        print(f'First Cash Book Entries: {len(report.cash_books[0].entries)}')
    print(f'Product Sales Total: {report.product_sales.total_sales}')
    print(f'Service Sales Total: {report.service_sales.total_sales}')
    print(f'Profit Loss Net Profit: {report.profit_loss.net_profit}')
    print(f'Work Orders Total: {report.work_orders.total_workorders}')
except Exception as e:
    print(f'Error: {e}')
    import traceback
    traceback.print_exc()
