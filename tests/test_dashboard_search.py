from datetime import date, datetime
from decimal import Decimal
from types import SimpleNamespace
from uuid import uuid4

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from models.customer import Customer, Vehicle
from models.expenses import Expenses, ExpenseStatus, ExpenseType
from models.purchase_order import PurchaseOrder, PurchaseOrderStatus
from models.supplier import Supplier
from models.workorder import Workorder
from routes import routes_dashboard
from services import services_product
from services.services_dashboard import search_dashboard_records


@pytest.fixture
def db():
    engine = create_engine("sqlite://")
    tables = [Customer.__table__, Vehicle.__table__, Supplier.__table__,
              Workorder.__table__, PurchaseOrder.__table__, Expenses.__table__]
    for table in tables:
        table.create(engine)
    with Session(engine) as session:
        customer_id, vehicle_id, supplier_id = uuid4(), uuid4(), uuid4()
        session.execute(Customer.__table__.insert().values(
            id=customer_id, nama="Budi Santoso", hp="+62 (812) 345-678",
            alamat="Jakarta", created_at=date.today(), updated_at=date.today(),
        ))
        session.execute(Vehicle.__table__.insert().values(
            id=vehicle_id, customer_id=customer_id, no_pol="B 1234 ABC",
        ))
        session.execute(Supplier.__table__.insert().values(
            id=supplier_id, nama="Vendor Makmur", perusahaan="PT Onderdil",
            toko="Toko Suku Cadang", hp="08123", alamat="Jakarta",
            created_at=date.today(), updated_at=date.today(),
        ))
        for index in range(7):
            session.execute(Workorder.__table__.insert().values(
                id=uuid4(), no_wo=f"WO-{index:03d}",
                tanggal_masuk=datetime(2026, 10, index + 1),
                keluhan="Servis", status="draft", total_biaya=100,
                customer_id=customer_id, vehicle_id=vehicle_id,
            ))
        session.execute(Workorder.__table__.insert().values(
            id=uuid4(), no_wo="WO-ORPHAN", tanggal_masuk=datetime(2026, 10, 8),
            keluhan="Servis", status="draft", total_biaya=100,
        ))
        session.execute(PurchaseOrder.__table__.insert().values(
            id=uuid4(), po_no="PO-123", supplier_id=supplier_id,
            date=date(2026, 10, 1), total=250000, status=PurchaseOrderStatus.draft,
            created_at=datetime.now(), updated_at=datetime.now(),
        ))
        session.execute(Expenses.__table__.insert().values(
            id=uuid4(), name="Tagihan Bulanan", description="Pembayaran PLN",
            expense_type=ExpenseType.listrik, status=ExpenseStatus.open,
            amount=150000, date=date(2026, 10, 1),
            created_at=datetime.now(), updated_at=datetime.now(),
        ))
        session.commit()
        yield session
    engine.dispose()


@pytest.mark.parametrize("term", ["bUDI", "B1234ABC", "1234", "812345678", "WO-"])
def test_workorder_search_all_requested_fields(db, term):
    result = search_dashboard_records(db, "workorders", term)
    assert len(result["items"]) == 5
    assert result["items"][0]["no_wo"] == ("WO-ORPHAN" if term == "WO-" else "WO-006")
    assert result["pagination"]["total"] == (8 if term == "WO-" else 7)
    if term != "WO-":
        assert result["items"][0]["customer_name"] == "Budi Santoso"
        assert result["items"][0]["hp"] == "+62 (812) 345-678"
        assert result["items"][0]["no_pol"] == "B 1234 ABC"


def test_pagination_and_literal_wildcards(db):
    second = search_dashboard_records(db, "workorders", "budi", page=2, limit=5)
    assert len(second["items"]) == 2
    assert second["pagination"] == {
        "page": 2, "limit": 5, "total": 7, "total_pages": 2,
        "has_previous": True, "has_next": False,
    }
    first = search_dashboard_records(db, "workorders", "budi")
    assert not ({item["id"] for item in first["items"]} &
                {item["id"] for item in second["items"]})
    for term in ("%", "_", "tidak ada"):
        result = search_dashboard_records(db, "workorders", term)
        assert result["items"] == []
        assert result["pagination"]["total"] == 0


@pytest.mark.parametrize("term", ["MAKMUR", "po-123", "onderdil", "suku cadang"])
def test_purchase_search(db, term):
    result = search_dashboard_records(db, "purchase-orders", term)
    assert result["pagination"]["total"] == 1
    assert result["items"][0]["vendor_name"] == "Vendor Makmur"
    assert result["items"][0]["po_no"] == "PO-123"


@pytest.mark.parametrize("term", ["tagihan", "pln", "listrik"])
def test_expense_search(db, term):
    result = search_dashboard_records(db, "expenses", term)
    assert result["pagination"]["total"] == 1
    assert result["items"][0]["amount"] == 150000


def test_expense_type_search_accepts_display_value_and_database_enum_name(db):
    db.execute(Expenses.__table__.update().values(expense_type=ExpenseType.lain_lain))
    for term in ("lain-lain", "lain_lain"):
        result = search_dashboard_records(db, "expenses", term)
        assert result["pagination"]["total"] == 1


def test_search_route_validates_and_serializes(monkeypatch):
    app = FastAPI()
    app.include_router(routes_dashboard.router)
    app.dependency_overrides[routes_dashboard.get_db] = lambda: object()
    app.dependency_overrides[routes_dashboard.jwt_required] = lambda: None
    calls = []

    def search(db, kind, q, page, limit):
        calls.append((kind, q, page, limit))
        return {
            "items": [{"id": uuid4(), "date": date(2026, 10, 1),
                       "status": ExpenseStatus.open}],
            "pagination": {"page": page, "limit": limit, "total": 1, "total_pages": 1,
                           "has_previous": False, "has_next": False},
        }

    monkeypatch.setattr(routes_dashboard, "search_dashboard_records", search)
    with TestClient(app) as client:
        response = client.get("/dashboard/search/expenses?q=PLN&page=2&limit=10")
        assert response.status_code == 200
        body = response.json()
        assert body["status"] == "success"
        assert body["data"]["items"][0]["date"] == "2026-10-01"
        assert body["data"]["items"][0]["status"] == "open"
        assert calls == [("expenses", "PLN", 2, 10)]
        for suffix in ("", "?q=", "?q=%20%20", "?q=x&page=0",
                       "?q=x&limit=101", "?q=" + "x" * 201):
            assert client.get("/dashboard/search/expenses" + suffix).status_code == 422
        assert client.get("/dashboard/search/invalid?q=x").status_code == 422


def test_search_routes_keep_jwt_dependency():
    route = next(route for route in routes_dashboard.router.routes
                 if route.path == "/dashboard/search/{kind}")
    assert any(dependency.call is routes_dashboard.jwt_required
               for dependency in route.dependant.dependencies)


@pytest.mark.parametrize(
    "stock,minimum,expected",
    [(0, 5, "reorder"), (5, 5, "reorder"), (6, 5, "safe"),
     (0, 0, "reorder"), (-1, 0, "reorder")],
)
def test_low_stock_uses_existing_inventory_threshold(monkeypatch, stock, minimum, expected):
    product = SimpleNamespace(
        id=uuid4(), category=None, brand=None, satuan=None, supplier=None,
        inventory=[SimpleNamespace(quantity=Decimal(stock))],
        price=Decimal(100), cost=Decimal(50), min_stock=Decimal(minimum),
    )
    monkeypatch.setattr(services_product, "to_dict", lambda product: {"id": product.id})
    monkeypatch.setattr(services_product, "_get_latest_purchase_source", lambda *args: None)
    item = services_product._build_inventory_item(object(), product, False)
    assert item["stock_status"] == expected
    assert item["total_stock"] == stock
    assert item["min_stock"] == minimum
