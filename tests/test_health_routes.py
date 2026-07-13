from fastapi import FastAPI
from fastapi.testclient import TestClient

from routes import routes_health


def test_health_endpoint_reports_app_and_database_status(monkeypatch):
    app = FastAPI()
    app.include_router(routes_health.router)
    app.dependency_overrides[routes_health.get_db] = lambda: object()

    monkeypatch.setattr(
        routes_health,
        "check_database_connection",
        lambda db: {
            "connected": True,
            "dialect": "postgresql",
            "database": "bengkel",
        },
    )

    client = TestClient(app)
    response = client.get("/health")

    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "success"
    assert body["data"]["app"] == "ok"
    assert body["data"]["database"]["connected"] is True
    assert body["data"]["database"]["dialect"] == "postgresql"


def test_db_check_endpoint_reports_database_status(monkeypatch):
    app = FastAPI()
    app.include_router(routes_health.router)
    app.dependency_overrides[routes_health.get_db] = lambda: object()

    monkeypatch.setattr(
        routes_health,
        "check_database_connection",
        lambda db: {
            "connected": True,
            "dialect": "postgresql",
            "database": "bengkel",
        },
    )

    client = TestClient(app)
    response = client.get("/db-check")

    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "success"
    assert body["data"]["connected"] is True
    assert body["data"]["database"] == "bengkel"


def test_health_and_db_check_return_503_when_database_is_unavailable(monkeypatch):
    app = FastAPI()
    app.include_router(routes_health.router)
    app.dependency_overrides[routes_health.get_db] = lambda: object()

    def raise_connection_error(db):
        raise RuntimeError("database offline")

    monkeypatch.setattr(routes_health, "check_database_connection", raise_connection_error)

    client = TestClient(app)

    health_response = client.get("/health")
    db_response = client.get("/db-check")

    assert health_response.status_code == 503
    assert health_response.json()["data"]["database"]["connected"] is False
    assert "database offline" in health_response.json()["message"]

    assert db_response.status_code == 503
    assert db_response.json()["data"]["connected"] is False
    assert "database offline" in db_response.json()["message"]
