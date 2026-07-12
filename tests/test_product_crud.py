from decimal import Decimal
from types import SimpleNamespace
from uuid import uuid4

import pytest
from pydantic import ValidationError
from fastapi import FastAPI

from schemas.service_product import UpdateProduct
from services import services_product
from routes.routes_product import router


class FakeQuery:
    def __init__(self, row=None):
        self.row = row

    def filter(self, *args):
        return self

    def first(self):
        return self.row


class FakeSession:
    def __init__(self, product, reference=None):
        self.product = product
        self.reference = reference
        self.committed = False
        self.deleted = None

    def query(self, model):
        if getattr(model, "__name__", "") == "Product":
            return FakeQuery(self.product)
        return FakeQuery(self.reference)

    def commit(self):
        self.committed = True

    def refresh(self, obj):
        pass

    def delete(self, obj):
        self.deleted = obj

    def get_bind(self):
        return object()


def test_update_product_requires_at_least_one_field():
    with pytest.raises(ValidationError):
        UpdateProduct()


def test_update_product_changes_only_supplied_fields(monkeypatch):
    product = SimpleNamespace(id=uuid4(), name="Old", price=Decimal("100"), cost=Decimal("60"))
    db = FakeSession(product)
    monkeypatch.setattr(
        services_product,
        "get_product_by_id",
        lambda db, product_id: {"id": product_id, "name": product.name, "price": product.price},
    )

    result = services_product.update_product(
        db,
        product.id,
        UpdateProduct(name="New", price=Decimal("120")),
    )

    assert product.name == "New"
    assert product.price == Decimal("120")
    assert product.cost == Decimal("60")
    assert db.committed is True
    assert result["name"] == "New"


def test_delete_product_rejects_referenced_product(monkeypatch):
    product = SimpleNamespace(id=uuid4())
    db = FakeSession(product, reference=SimpleNamespace(id=uuid4()))
    monkeypatch.setattr(
        services_product,
        "inspect",
        lambda bind: SimpleNamespace(has_table=lambda table: False),
    )

    with pytest.raises(services_product.ProductInUseError):
        services_product.delete_product(db, product.id)

    assert db.deleted is None


def test_delete_unused_product(monkeypatch):
    product = SimpleNamespace(id=uuid4())
    db = FakeSession(product)
    monkeypatch.setattr(
        services_product,
        "inspect",
        lambda bind: SimpleNamespace(has_table=lambda table: False),
    )

    services_product.delete_product(db, product.id)

    assert db.deleted is product
    assert db.committed is True


def test_delete_openapi_declares_documented_responses():
    app = FastAPI()
    app.include_router(router)
    responses = app.openapi()["paths"]["/products/{product_id}"]["delete"]["responses"]

    assert {"200", "404", "409", "422", "500"} <= responses.keys()
    for status in ("404", "409", "500"):
        schema = responses[status]["content"]["application/json"]["schema"]
        assert schema["$ref"].endswith("/ApiErrorResponse")
