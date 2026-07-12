from fastapi import FastAPI
from fastapi.testclient import TestClient
from pydantic import ValidationError

from routes import routes_customer, routes_supplier
from schemas.service_customer import CreateCustomer, CreateCustomerWithVehicles
from schemas.service_supplier import CreateSupplier


def test_supplier_schema_requires_nama_alamat_hp_and_normalizes_optional_fields():
    payload = CreateSupplier(
        nama=" Supplier A ",
        hp=" 08123 ",
        alamat=" Jalan Mawar ",
        email="",
        supplier_code="",
    )

    assert payload.nama == "Supplier A"
    assert payload.hp == "08123"
    assert payload.alamat == "Jalan Mawar"
    assert payload.email is None
    assert payload.supplier_code is None

    for invalid_payload in (
        {"nama": "Supplier A", "hp": "08123"},
        {"nama": "Supplier A", "hp": "08123", "alamat": "   "},
        {"nama": "", "hp": "08123", "alamat": "Jalan"},
    ):
        try:
            CreateSupplier(**invalid_payload)
            assert False, "Expected validation error"
        except ValidationError:
            pass


def test_customer_schema_requires_nama_alamat_hp_and_normalizes_optional_fields():
    payload = CreateCustomer(
        nama=" Customer A ",
        hp=" 08123 ",
        alamat=" Jalan Melati ",
        email="",
    )

    assert payload.nama == "Customer A"
    assert payload.hp == "08123"
    assert payload.alamat == "Jalan Melati"
    assert payload.email is None

    for invalid_payload in (
        {"nama": "Customer A", "hp": "08123"},
        {"nama": "Customer A", "hp": "08123", "alamat": ""},
        {"nama": "Customer A", "hp": "   ", "alamat": "Jalan"},
    ):
        try:
            CreateCustomer(**invalid_payload)
            assert False, "Expected validation error"
        except ValidationError:
            pass


def test_customer_with_vehicle_schema_accepts_minimal_required_customer_fields():
    payload = CreateCustomerWithVehicles(
        nama="Customer A",
        hp="08123",
        alamat="Jalan Melati",
        email="",
        model="",
    )

    assert payload.email is None
    assert payload.model is None


def test_create_supplier_route_accepts_minimal_payload(monkeypatch):
    app = FastAPI()
    app.include_router(routes_supplier.router)
    app.dependency_overrides[routes_supplier.get_db] = lambda: object()
    app.dependency_overrides[routes_supplier.jwt_required] = lambda: None

    monkeypatch.setattr(
        routes_supplier,
        "create_supplier",
        lambda db, supplier_data: {
            "nama": supplier_data.nama,
            "hp": supplier_data.hp,
            "alamat": supplier_data.alamat,
            "email": supplier_data.email,
        },
    )

    client = TestClient(app)
    response = client.post(
        "/suppliers/create",
        json={"nama": "Supplier A", "hp": "08123", "alamat": "Jalan Mawar"},
    )

    assert response.status_code == 200
    assert response.json()["data"]["nama"] == "Supplier A"
    assert response.json()["data"]["alamat"] == "Jalan Mawar"


def test_create_customer_routes_accept_minimal_payload(monkeypatch):
    app = FastAPI()
    app.include_router(routes_customer.router)
    app.dependency_overrides[routes_customer.get_db] = lambda: object()
    app.dependency_overrides[routes_customer.jwt_required] = lambda: None

    monkeypatch.setattr(
        routes_customer,
        "createCustomerOnly",
        lambda db, customer_data: {
            "nama": customer_data.nama,
            "hp": customer_data.hp,
            "alamat": customer_data.alamat,
            "email": customer_data.email,
        },
    )
    monkeypatch.setattr(
        routes_customer,
        "create_customer_with_vehicles",
        lambda db, customer_data: {
            "customer": {
                "nama": customer_data.nama,
                "hp": customer_data.hp,
                "alamat": customer_data.alamat,
            },
            "vehicle": {
                "model": customer_data.model,
            },
        },
    )

    client = TestClient(app)

    customer_only_response = client.post(
        "/customers/customer-only",
        json={"nama": "Customer A", "hp": "08123", "alamat": "Jalan Melati"},
    )
    with_vehicle_response = client.post(
        "/customers/with-vehicle",
        json={"nama": "Customer B", "hp": "08124", "alamat": "Jalan Kenanga"},
    )

    assert customer_only_response.status_code == 200
    assert customer_only_response.json()["data"]["alamat"] == "Jalan Melati"
    assert with_vehicle_response.status_code == 200
    assert with_vehicle_response.json()["data"]["customer"]["nama"] == "Customer B"
