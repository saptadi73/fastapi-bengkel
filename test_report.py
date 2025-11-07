import sys
sys.path.append('.')
from models.database import SessionLocal
from services.services_accounting import generate_consignment_payable_report
from schemas.service_accounting import ReceivablePayableReportRequest
from datetime import date, timedelta

db = SessionLocal()
try:
    rpt_req = ReceivablePayableReportRequest(start_date=date.today()-timedelta(days=30), end_date=date.today())
    rpt = generate_consignment_payable_report(db, rpt_req)
    print('Consignment payable report:')
    print(f'Total payable: {rpt["total_payable"]}')
    print('Items:')
    for item in rpt['items']:
        print(f'  Supplier: {item["supplier_name"]}, Payable: {item["total_payable"]}')
except Exception as e:
    print(f'Error: {e}')
finally:
    db.close()
