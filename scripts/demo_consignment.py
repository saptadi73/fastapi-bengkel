"""
Demo script: create a sale with a consignment product and show the consignment-payable report.
Run with: python scripts/demo_consignment.py

Note: this script uses the project's DB configured in `models.database.URL_DATABASE` (Postgres).
If your DB isn't running locally, start it or adapt `models.database` to point to a test DB.
"""
from decimal import Decimal
from datetime import datetime, date, timedelta
import uuid
import sys

from sqlalchemy.exc import OperationalError

from models.database import SessionLocal
from models.accounting import Account
from models.supplier import Supplier
from models.workorder import Product, Workorder, ProductOrdered, Satuan

from services.services_accounting import record_sale, generate_consignment_payable_report
from schemas.service_accounting import SaleRecordCreate, ReceivablePayableReportRequest


def ensure_account(db, code: str, name: str, normal_balance: str, account_type: str):
    acc = db.query(Account).filter(Account.code == code).first()
    if acc:
        return acc
    new = Account(
        id=uuid.uuid4(),
        code=code,
        name=name,
        normal_balance=normal_balance,
        account_type=account_type,
        is_active=True
    )
    db.add(new)
    db.commit()
    db.refresh(new)
    return new


def main():
    try:
        db = SessionLocal()
    except OperationalError as e:
        print("Cannot connect to the database. Make sure Postgres is running and the connection string in models/database.py is correct.")
        print(str(e))
        sys.exit(1)

    try:
        # Ensure COA needed by record_sale and consignment logic
        # Defaults in schemas: piutang 1200, penjualan 4000, ppn 2410, hpp 5100, persediaan 1300, commission 6003, cons payable 3002
        ensure_account(db, "1200", "Piutang Usaha", "debit", "asset")
        ensure_account(db, "4000", "Pendapatan Penjualan", "credit", "revenue")
        ensure_account(db, "2410", "PPN Keluaran", "credit", "liability")
        ensure_account(db, "5100", "HPP", "debit", "expense")
        ensure_account(db, "1300", "Persediaan", "debit", "asset")
        ensure_account(db, "6003", "Beban Komisi Konsinyasi", "debit", "expense")
        ensure_account(db, "3002", "Hutang Konsinyasi", "credit", "liability")

        # Create supplier
        supplier = Supplier(nama="Demo Supplier", hp="08123456789", alamat="Jalan Demo")
        db.add(supplier)
        db.commit()
        db.refresh(supplier)

        # Create a satuan (unit)
        satuan = Satuan(name="pcs", description="pcs")
        db.add(satuan)
        db.commit()
        db.refresh(satuan)

        # Create product (consignment)
        product = Product(
            name="Sparepart Konsinyasi",
            price=Decimal("500.00"),
            cost=Decimal("300.00"),
            min_stock=Decimal("0"),
            supplier_id=supplier.id,
            is_consignment=True,
            consignment_commission=Decimal("50.00"),
            satuan_id=satuan.id
        )
        db.add(product)
        db.commit()
        db.refresh(product)

        # Create workorder
        wo = Workorder(
            no_wo=f"WO-{uuid.uuid4().hex[:6]}",
            tanggal_masuk=datetime.utcnow(),
            keluhan="Ganti oli",
            status="open",
            total_biaya=Decimal("500.00"),
            pajak=Decimal("0.00"),
            customer_id=None,
        )
        db.add(wo)
        db.commit()
        db.refresh(wo)

        # Create product_ordered
        po = ProductOrdered(
            quantity=Decimal("2"),
            subtotal=Decimal("1000.00"),
            price=Decimal("500.00"),
            discount=Decimal("0.00"),
            product_id=product.id,
            workorder_id=wo.id,
            satuan_id=satuan.id
        )
        db.add(po)
        db.commit()
        db.refresh(po)

        # Prepare sale record
        sale_payload = SaleRecordCreate(
            entry_no=None,
            tanggal=date.today(),
            customer_id=None,
            total_penjualan=Decimal("1000.00"),
            ppn=Decimal("0.00"),
            potongan=Decimal("0.00"),
            kas_bank_code=None,
            piutang_code="1200",
            penjualan_code="4000",
            ppn_keluaran_code="2410",
            hpp_code="5100",
            persediaan_code="1300",
            hpp=Decimal("600.00"),
            memo="Penjualan demo dengan konsinyasi",
            created_by="demo_script"
        )

        print("Recording sale (this will create sale journal and separate consignment payable entries)...")
        out = record_sale(db, sale_data=sale_payload)
        print("Sale output:")
        print(out)

        # Generate consignment payable report for today
        rpt_req = ReceivablePayableReportRequest(start_date=date.today() - timedelta(days=1), end_date=date.today())
        rpt = generate_consignment_payable_report(db, rpt_req)
        print("\nConsignment payable report:")
        print(rpt)

    finally:
        db.close()


if __name__ == "__main__":
    main()
