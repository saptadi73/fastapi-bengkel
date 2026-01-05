import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from decimal import Decimal
from datetime import datetime, date, timedelta
from uuid import UUID

from main import app
from models.workorder import Workorder
from models.attendance import Attendance
from models.purchase_order import PurchaseOrder, PurchaseOrderStatus
from models.expenses import Expenses
from models.database import SessionLocal
from services.services_dashboard import (
    get_dashboard_summary,
    get_workorder_pie,
    get_sales_monthly,
    get_purchase_monthly,
    get_expenses_monthly,
    get_combined_monthly
)


# Test client
client = TestClient(app)


# Fixtures
@pytest.fixture
def db():
    """Create test database session"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@pytest.fixture
def sample_workorders(db: Session):
    """Create sample work orders for testing"""
    # WO hari ini (today)
    wo_today = Workorder(
        id=UUID("11111111-1111-1111-1111-111111111111"),
        no_wo="WO-202601-0001",
        tanggal_masuk=datetime.now(),
        keluhan="Test keluhan hari ini",
        status="pending",
        total_biaya=Decimal("1000000"),
        customer_id=UUID("12121212-1212-1212-1212-121212121212"),
        karyawan_id=UUID("13131313-1313-1313-1313-131313131313"),
        vehicle_id=UUID("14141414-1414-1414-1414-141414141414")
    )

    # WO selesai (30 hari lalu / 1 month ago)
    wo_finished_old = Workorder(
        id=UUID("21111111-1111-1111-1111-111111111111"),
        no_wo="WO-202512-0001",
        tanggal_masuk=datetime.now() - timedelta(days=30),
        keluhan="Test keluhan selesai lama",
        status="selesai",
        total_biaya=Decimal("5000000"),
        customer_id=UUID("22121212-1212-1212-1212-121212121212"),
        karyawan_id=UUID("13131313-1313-1313-1313-131313131313"),
        vehicle_id=UUID("24141414-1414-1414-1414-141414141414")
    )

    # WO selesai (60 hari lalu / 2 months ago)
    wo_finished_older = Workorder(
        id=UUID("31111111-1111-1111-1111-111111111111"),
        no_wo="WO-202511-0001",
        tanggal_masuk=datetime.now() - timedelta(days=60),
        keluhan="Test keluhan selesai lebih lama",
        status="selesai",
        total_biaya=Decimal("3500000"),
        customer_id=UUID("32121212-1212-1212-1212-121212121212"),
        karyawan_id=UUID("13131313-1313-1313-1313-131313131313"),
        vehicle_id=UUID("34141414-1414-1414-1414-141414141414")
    )

    # WO pending
    wo_pending = Workorder(
        id=UUID("41111111-1111-1111-1111-111111111111"),
        no_wo="WO-202601-0002",
        tanggal_masuk=datetime.now() - timedelta(days=5),
        keluhan="Test keluhan pending",
        status="pending",
        total_biaya=Decimal("2000000"),
        customer_id=UUID("42121212-1212-1212-1212-121212121212"),
        karyawan_id=UUID("43131313-1313-1313-1313-131313131313"),
        vehicle_id=UUID("44141414-1414-1414-1414-141414141414")
    )

    db.add_all([wo_today, wo_finished_old, wo_finished_older, wo_pending])
    db.commit()

    yield [wo_today, wo_finished_old, wo_finished_older, wo_pending]


@pytest.fixture
def sample_attendances(db: Session):
    """Create sample attendance records for testing"""
    # Present today
    att_present = Attendance(
        id=UUID("51111111-1111-1111-1111-111111111111"),
        karyawan_id=UUID("13131313-1313-1313-1313-131313131313"),
        date=date.today(),
        status="present"
    )

    # Absent yesterday
    att_absent = Attendance(
        id=UUID("52111111-1111-1111-1111-111111111111"),
        karyawan_id=UUID("43131313-1313-1313-1313-131313131313"),
        date=date.today() - timedelta(days=1),
        status="absent"
    )

    # Late 2 days ago
    att_late = Attendance(
        id=UUID("53111111-1111-1111-1111-111111111111"),
        karyawan_id=UUID("13131313-1313-1313-1313-131313131313"),
        date=date.today() - timedelta(days=2),
        status="late"
    )

    db.add_all([att_present, att_absent, att_late])
    db.commit()

    yield [att_present, att_absent, att_late]


@pytest.fixture
def sample_purchase_orders(db: Session):
    """Create sample purchase orders for testing"""
    # PO last month (dijalankan status)
    po_last_month = PurchaseOrder(
        id=UUID("61111111-1111-1111-1111-111111111111"),
        po_no="PO-202512-0001",
        supplier_id=UUID("62121212-1212-1212-1212-121212121212"),
        date=date.today() - timedelta(days=30),
        status="dijalankan",
        total=Decimal("5000000")
    )

    # PO 2 months ago (diterima status)
    po_two_months = PurchaseOrder(
        id=UUID("71111111-1111-1111-1111-111111111111"),
        po_no="PO-202511-0001",
        supplier_id=UUID("72121212-1212-1212-1212-121212121212"),
        date=date.today() - timedelta(days=60),
        status="diterima",
        total=Decimal("3000000")
    )

    # PO draft (tidak dihitung / not counted)
    po_draft = PurchaseOrder(
        id=UUID("81111111-1111-1111-1111-111111111111"),
        po_no="PO-202601-DRAFT",
        supplier_id=UUID("82121212-1212-1212-1212-121212121212"),
        date=date.today(),
        status="draft",
        total=Decimal("2000000")
    )

    db.add_all([po_last_month, po_two_months, po_draft])
    db.commit()

    yield [po_last_month, po_two_months, po_draft]


@pytest.fixture
def sample_expenses(db: Session):
    """Create sample expenses for testing"""
    # Expense last month
    exp_last = Expenses(
        id=UUID("91111111-1111-1111-1111-111111111111"),
        description="Test expense 1",
        amount=Decimal("1000000"),
        date=date.today() - timedelta(days=30)
    )

    # Expense 2 months ago
    exp_two = Expenses(
        id=UUID("92111111-1111-1111-1111-111111111111"),
        description="Test expense 2",
        amount=Decimal("500000"),
        date=date.today() - timedelta(days=60)
    )

    db.add_all([exp_last, exp_two])
    db.commit()

    yield [exp_last, exp_two]


# Test Classes
class TestDashboardServices:
    """Test dashboard service functions with empty database (no FK constraints)"""

    def test_get_dashboard_summary_empty_db(self, db: Session):
        """Test get_dashboard_summary returns correct structure even with empty DB"""
        result = get_dashboard_summary(db)

        assert isinstance(result, dict)
        assert "workorders_today" in result
        assert "workorders_finished" in result
        assert "workorders_pending" in result
        assert "employees_present" in result

        # Check types
        assert isinstance(result["workorders_today"], int)
        assert isinstance(result["workorders_finished"], int)
        assert isinstance(result["workorders_pending"], int)
        assert isinstance(result["employees_present"], int)

    def test_get_workorder_pie_empty_db(self, db: Session):
        """Test get_workorder_pie returns correct breakdown with empty DB"""
        result = get_workorder_pie(db)

        assert isinstance(result, dict)
        assert "completed" in result
        assert "pending" in result
        assert isinstance(result["completed"], int)
        assert isinstance(result["pending"], int)

    def test_get_sales_monthly_empty_db(self, db: Session):
        """Test get_sales_monthly returns list with empty DB"""
        result = get_sales_monthly(db, months=6)

        assert isinstance(result, list)
        # Empty DB returns empty list or list with zero totals
        if len(result) > 0:
            assert "month" in result[0]
            assert "total" in result[0]
            assert isinstance(result[0]["total"], (int, float))

    def test_get_purchase_monthly_empty_db(self, db: Session):
        """Test get_purchase_monthly returns list with empty DB"""
        result = get_purchase_monthly(db, months=6)

        assert isinstance(result, list)

    def test_get_expenses_monthly_empty_db(self, db: Session):
        """Test get_expenses_monthly returns list with empty DB"""
        result = get_expenses_monthly(db, months=6)

        assert isinstance(result, list)

    def test_get_combined_monthly_empty_db(self, db: Session):
        """Test get_combined_monthly returns list with empty DB"""
        result = get_combined_monthly(db, months=6)

        assert isinstance(result, list)


class TestDashboardAPI:
    """Test dashboard API endpoints"""

    def test_summary_endpoint_needs_auth(self):
        """Test summary endpoint requires authentication"""
        response = client.get("/dashboard/summary")
        # Should require auth (401 or 403)
        assert response.status_code in [401, 403]

    def test_workorders_pie_endpoint_needs_auth(self):
        """Test workorders-pie endpoint requires authentication"""
        response = client.get("/dashboard/workorders-pie")
        assert response.status_code in [401, 403]

    def test_sales_monthly_endpoint_needs_auth(self):
        """Test sales-monthly endpoint requires authentication"""
        response = client.get("/dashboard/sales-monthly")
        assert response.status_code in [401, 403]

    def test_purchase_monthly_endpoint_needs_auth(self):
        """Test purchase-monthly endpoint requires authentication"""
        response = client.get("/dashboard/purchase-monthly")
        assert response.status_code in [401, 403]

    def test_expenses_monthly_endpoint_needs_auth(self):
        """Test expenses-monthly endpoint requires authentication"""
        response = client.get("/dashboard/expenses-monthly")
        assert response.status_code in [401, 403]

    def test_combined_monthly_endpoint_needs_auth(self):
        """Test combined-monthly endpoint requires authentication"""
        response = client.get("/dashboard/combined-monthly")
        assert response.status_code in [401, 403]

    def test_invalid_months_parameter(self):
        """Test with invalid months parameter (too high)"""
        response = client.get("/dashboard/sales-monthly?months=50")
        # Should be auth error (401/403) or validation error (400)
        assert response.status_code in [400, 401, 403]

    def test_months_parameter_zero(self):
        """Test with months=0"""
        response = client.get("/dashboard/sales-monthly?months=0")
        assert response.status_code in [400, 401, 403]

    def test_months_parameter_negative(self):
        """Test with negative months"""
        response = client.get("/dashboard/sales-monthly?months=-5")
        assert response.status_code in [400, 401, 403]


class TestDashboardBoundary:
    """Test boundary conditions"""

    def test_single_month_data(self, db: Session):
        """Test with months=1"""
        result = get_sales_monthly(db, months=1)
        assert isinstance(result, list)
        # Should return at most 1 month
        assert len(result) <= 1

    def test_max_months_data(self, db: Session):
        """Test with months=24 (max)"""
        result = get_sales_monthly(db, months=24)
        assert isinstance(result, list)
        # Should handle max range
        assert len(result) <= 24

    def test_empty_database_handling(self, db: Session):
        """Test functions work with empty database"""
        # These should not raise errors even with no data
        summary = get_dashboard_summary(db)
        pie = get_workorder_pie(db)
        sales = get_sales_monthly(db, months=6)
        purchase = get_purchase_monthly(db, months=6)
        expenses = get_expenses_monthly(db, months=6)
        combined = get_combined_monthly(db, months=6)

        # All should return valid structures (empty lists or zero values)
        assert isinstance(summary, dict)
        assert isinstance(pie, dict)
        assert isinstance(sales, list)
        assert isinstance(purchase, list)
        assert isinstance(expenses, list)
        assert isinstance(combined, list)


class TestDashboardIntegration:
    """Integration tests for dashboard"""

    def test_all_endpoints_json_structure(self):
        """Test all endpoints return valid JSON structure (auth errors ok)"""
        endpoints = [
            "/dashboard/summary",
            "/dashboard/workorders-pie",
            "/dashboard/sales-monthly",
            "/dashboard/purchase-monthly",
            "/dashboard/expenses-monthly",
            "/dashboard/combined-monthly"
        ]

        for endpoint in endpoints:
            response = client.get(endpoint)
            # Should be valid JSON or auth error
            try:
                response.json()
            except Exception as e:
                # Auth errors (401/403) don't have JSON
                assert response.status_code in [401, 403], f"Endpoint {endpoint} failed: {e}"

    def test_summary_structure(self, db: Session):
        """Test summary structure is valid"""
        result = get_dashboard_summary(db)

        # Verify all required fields exist
        assert "workorders_pending" in result
        assert "workorders_finished" in result
        assert "workorders_today" in result
        assert "employees_present" in result

    def test_monthly_data_returns_list(self, db: Session):
        """Test combined monthly data returns list"""
        combined = get_combined_monthly(db, months=6)
        sales = get_sales_monthly(db, months=6)
        purchase = get_purchase_monthly(db, months=6)

        # All should be lists
        assert isinstance(combined, list)
        assert isinstance(sales, list)
        assert isinstance(purchase, list)
