from datetime import date, datetime
from types import SimpleNamespace
from uuid import uuid4

from fastapi import FastAPI
from fastapi.testclient import TestClient

from routes import routes_product
from services import services_product


class FluentQuery:
    def __init__(self, rows):
        self.rows = rows

    def options(self, *args):
        return self

    def join(self, *args):
        return self

    def filter(self, *args):
        return self

    def order_by(self, *args):
        return self

    def all(self):
        return self.rows

    def first(self):
        return self.rows[0] if self.rows else None


def _inventory_item(index):
    return {
        "id": str(uuid4()),
        "name": f"Product {index:02d}",
        "vendor_code": f"VND-{index:03d}",
        "price": 150000,
        "purchase_price": 95000,
        "hpp": 100000,
        "cost": 100000,
        "margin": 50000,
        "margin_percentage": 33.33,
        "total_stock": 50,
        "min_stock": 10,
        "stock_status": "safe",
        "is_consignment": False,
    }


def test_service_paginates_26_products_into_25_and_1(monkeypatch):
    products = [SimpleNamespace(index=index) for index in range(26)]
    db = SimpleNamespace(query=lambda model: FluentQuery(products), get_bind=lambda: object())
    monkeypatch.setattr(
        services_product,
        "inspect",
        lambda bind: SimpleNamespace(has_table=lambda table: False),
    )
    monkeypatch.setattr(
        services_product,
        "_build_inventory_item",
        lambda db, product, consignment_available=None: _inventory_item(product.index),
    )

    first = services_product.get_inventory_products_paginated(db, page=1, limit=25)
    second = services_product.get_inventory_products_paginated(db, page=2, limit=25)

    assert len(first["data"]) == 25
    assert len(second["data"]) == 1
    assert first["pagination"] == {
        "page": 1,
        "limit": 25,
        "total": 26,
        "total_pages": 2,
        "has_previous": False,
        "has_next": True,
    }
    assert second["pagination"]["has_previous"] is True
    assert second["pagination"]["has_next"] is False


def test_route_has_single_envelope_and_validates_query(monkeypatch):
    app = FastAPI()
    app.include_router(routes_product.router)
    app.dependency_overrides[routes_product.get_db] = lambda: object()
    monkeypatch.setattr(
        routes_product,
        "get_inventory_products_paginated",
        lambda *args, **kwargs: {
            "status": "success",
            "message": "Inventory retrieved successfully",
            "data": [_inventory_item(1)],
            "pagination": {
                "page": 1,
                "limit": 25,
                "total": 1,
                "total_pages": 1,
                "has_previous": False,
                "has_next": False,
            },
        },
    )
    client = TestClient(app)

    response = client.get("/products/inventory/all")
    assert response.status_code == 200
    assert isinstance(response.json()["data"], list)
    assert "pagination" in response.json()
    assert "data" not in response.json()["data"][0]  # no nested envelope
    assert response.json()["data"][0]["vendor_code"] == "VND-001"

    assert client.get("/products/inventory/all?page=0").status_code == 422
    assert client.get("/products/inventory/all?limit=101").status_code == 422
    assert client.get("/products/inventory/all?stock_status=invalid").status_code == 422


def test_latest_purchase_price_compares_valid_sources(monkeypatch):
    receipt = SimpleNamespace(
        receipt_date=date(2026, 1, 1),
        created_at=datetime(2026, 1, 1, 8),
        id=uuid4(),
        unit_price=90000,
    )
    purchase_order = SimpleNamespace(
        date=date(2026, 2, 1),
        created_at=datetime(2026, 2, 1, 8),
    )
    purchase_line = SimpleNamespace(
        id=uuid4(),
        price=95000,
        purchase_order=purchase_order,
    )

    class FakeSession:
        def query(self, model):
            if model.__name__ == "ConsignmentReceipt":
                return FluentQuery([receipt])
            return FluentQuery([purchase_line])

    monkeypatch.setattr(
        services_product,
        "inspect",
        lambda bind: SimpleNamespace(has_table=lambda table: True),
    )
    session = FakeSession()
    session.get_bind = lambda: object()
    assert services_product._get_latest_purchase_price(session, uuid4()) == 95000


def test_latest_purchase_price_skips_unmigrated_consignment_table(monkeypatch):
    purchase_order = SimpleNamespace(
        date=date(2026, 2, 1),
        created_at=datetime(2026, 2, 1, 8),
    )
    purchase_line = SimpleNamespace(
        id=uuid4(),
        price=95000,
        purchase_order=purchase_order,
    )

    class FakeSession:
        def get_bind(self):
            return object()

        def query(self, model):
            assert model.__name__ != "ConsignmentReceipt"
            return FluentQuery([purchase_line])

    monkeypatch.setattr(
        services_product,
        "inspect",
        lambda bind: SimpleNamespace(has_table=lambda table: False),
    )

    assert services_product._get_latest_purchase_price(FakeSession(), uuid4()) == 95000


def test_build_inventory_item_uses_latest_purchase_supplier_instead_of_product_supplier(monkeypatch):
    latest_supplier = SimpleNamespace(supplier_code="VND-PO", nama="Vendor PO")
    product_supplier = SimpleNamespace(supplier_code="VND-PRODUCT", nama="Vendor Product")
    product = SimpleNamespace(
        id=uuid4(),
        name="Product",
        type="product",
        description="desc",
        price=150000,
        cost=100000,
        min_stock=10,
        supplier=product_supplier,
        category=None,
        brand=None,
        satuan=None,
        inventory=[SimpleNamespace(quantity=50)],
        is_consignment=False,
    )

    class FakeColumn:
        def __init__(self, name):
            self.name = name

    product.__table__ = SimpleNamespace(
        columns=[FakeColumn(name) for name in [
            "id", "name", "type", "description", "price", "cost", "min_stock", "is_consignment"
        ]]
    )

    monkeypatch.setattr(
        services_product,
        "_get_latest_purchase_source",
        lambda db, product_id, consignment_available=None: {
            "price": 95000,
            "supplier": latest_supplier,
        },
    )

    item = services_product._build_inventory_item(SimpleNamespace(), product, consignment_available=False)

    assert item["vendor_code"] == "VND-PO"
    assert item["supplier_name"] == "Vendor PO"
    assert item["purchase_price"] == 95000


def test_build_inventory_item_falls_back_to_product_supplier_when_no_purchase_history(monkeypatch):
    product_supplier = SimpleNamespace(supplier_code="VND-PRODUCT", nama="Vendor Product")
    product = SimpleNamespace(
        id=uuid4(),
        name="Product",
        type="product",
        description="desc",
        price=150000,
        cost=100000,
        min_stock=10,
        supplier=product_supplier,
        category=None,
        brand=None,
        satuan=None,
        inventory=[SimpleNamespace(quantity=50)],
        is_consignment=False,
    )

    class FakeColumn:
        def __init__(self, name):
            self.name = name

    product.__table__ = SimpleNamespace(
        columns=[FakeColumn(name) for name in [
            "id", "name", "type", "description", "price", "cost", "min_stock", "is_consignment"
        ]]
    )

    monkeypatch.setattr(
        services_product,
        "_get_latest_purchase_source",
        lambda db, product_id, consignment_available=None: None,
    )

    item = services_product._build_inventory_item(SimpleNamespace(), product, consignment_available=False)

    assert item["vendor_code"] == "VND-PRODUCT"
    assert item["supplier_name"] == "Vendor Product"
