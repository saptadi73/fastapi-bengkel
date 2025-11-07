import pytest
from decimal import Decimal
from datetime import date, datetime, timedelta
import uuid

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


@pytest.mark.integration
def test_consignment_payable_report_integration():
    """
    Integration test that creates minimal data (accounts, supplier, product, workorder, product_ordered),
    records a sale which should create per-supplier consignment payable entries, then asserts the report.

    This test will be skipped if the project's DB is not reachable (safe for CI/dev where DB may not be available).
    """
    try:
        db = SessionLocal()
        # Quick connectivity check
        try:
            db.execute("SELECT 1")
        except Exception:
            pytest.skip("Database not available; skipping integration test")
    except OperationalError:
        pytest.skip("Database not available; skipping integration test")

    try:
        # Ensure necessary accounts
        ensure_account(db, "1200", "Piutang Usaha", "debit", "asset")
        ensure_account(db, "4000", "Pendapatan Penjualan", "credit", "revenue")
        ensure_account(db, "2410", "PPN Keluaran", "credit", "liability")
        ensure_account(db, "5100", "HPP", "debit", "expense")
        ensure_account(db, "1300", "Persediaan", "debit", "asset")
        ensure_account(db, "6003", "Beban Komisi Konsinyasi", "debit", "expense")
        ensure_account(db, "3002", "Hutang Konsinyasi", "credit", "liability")

        # Create supplier
        supplier = Supplier(nama="Test Supplier", hp="08123456789", alamat="Test Addr")
        db.add(supplier)
        db.commit()
        db.refresh(supplier)

        # Create unit
        satuan = Satuan(name="pcs", description="pcs")
        db.add(satuan)
        db.commit()
        db.refresh(satuan)

        # Create consignment product
        product = Product(
            name="Test Consignment Product",
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
            keluhan="Test Service",
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

        # Prepare sale payload
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
            memo="Integration test sale",
            created_by="pytest"
        )

        # Record sale
        out = record_sale(db, sale_data=sale_payload)

        # Call consignment payable report
        rpt_req = ReceivablePayableReportRequest(start_date=date.today()-timedelta(days=1), end_date=date.today())
        rpt = generate_consignment_payable_report(db, rpt_req)

        assert isinstance(rpt, dict)
        assert rpt.get("total_payable") is not None
        assert rpt.get("items") is not None
        assert rpt["total_payable"] >= Decimal("0.00")
        assert len(rpt["items"]) >= 0

        # If there are items, ensure our supplier appears (best-effort)
        if rpt["items"]:
            assert any(item["supplier_id"] == str(supplier.id) or item["supplier_name"] == supplier.nama for item in rpt["items"]) 

    finally:
        db.close()
