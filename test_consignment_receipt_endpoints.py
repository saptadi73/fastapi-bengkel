"""
Test untuk Consignment Receipt Endpoints
"""

import pytest
from fastapi.testclient import TestClient
from uuid import uuid4
from datetime import datetime, date
from main import app

client = TestClient(app)

# Dummy auth token (ganti dengan token valid dari login)
VALID_TOKEN = None

def get_valid_token():
    """Get valid JWT token from login"""
    login_response = client.post("/auth/login", json={
        "username": "admin",
        "password": "admin123"
    })
    if login_response.status_code == 200:
        return login_response.json()["data"]["access_token"]
    return None

@pytest.fixture(scope="module")
def auth_token():
    global VALID_TOKEN
    if VALID_TOKEN is None:
        VALID_TOKEN = get_valid_token()
    return VALID_TOKEN

@pytest.fixture
def headers(auth_token):
    return {
        "Authorization": f"Bearer {auth_token}"
    }

# Test data
test_product_id = "550e8400-e29b-41d4-a716-446655440000"
test_supplier_id = "650e8400-e29b-41d4-a716-446655440000"

class TestConsignmentReceiptCreate:
    """Test CREATE operations"""
    
    def test_create_consignment_receipt_success(self, headers):
        """Test successful consignment receipt creation"""
        payload = {
            "product_id": test_product_id,
            "supplier_id": test_supplier_id,
            "receipt_number": f"CR-{datetime.now().timestamp()}",
            "receipt_date": date.today().isoformat(),
            "quantity_received": 50.0,
            "unit_price": 100000.0,
            "received_by": "Test User"
        }
        
        response = client.post(
            "/inventory/consignment-receipt/create",
            json=payload,
            headers=headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "success"
        assert "id" in data["data"]
        
        return data["data"]["id"]
    
    def test_create_consignment_receipt_missing_required_field(self, headers):
        """Test creation fails without required fields"""
        payload = {
            "product_id": test_product_id,
            "supplier_id": test_supplier_id,
            # Missing receipt_number
            "receipt_date": date.today().isoformat(),
            "quantity_received": 50.0,
            "received_by": "Test User"
        }
        
        response = client.post(
            "/inventory/consignment-receipt/create",
            json=payload,
            headers=headers
        )
        
        assert response.status_code in [400, 422]
    
    def test_create_consignment_receipt_without_auth(self):
        """Test creation fails without authentication"""
        payload = {
            "product_id": test_product_id,
            "supplier_id": test_supplier_id,
            "receipt_number": "CR-TEST-001",
            "receipt_date": date.today().isoformat(),
            "quantity_received": 50.0,
            "received_by": "Test User"
        }
        
        response = client.post(
            "/inventory/consignment-receipt/create",
            json=payload
        )
        
        assert response.status_code in [401, 403]

class TestConsignmentReceiptRead:
    """Test READ operations"""
    
    def test_get_consignment_receipt_by_id(self, headers):
        """Test fetch single receipt by ID"""
        # First create a receipt
        payload = {
            "product_id": test_product_id,
            "supplier_id": test_supplier_id,
            "receipt_number": f"CR-READ-{datetime.now().timestamp()}",
            "receipt_date": date.today().isoformat(),
            "quantity_received": 30.0,
            "unit_price": 150000.0,
            "received_by": "Test User"
        }
        
        create_response = client.post(
            "/inventory/consignment-receipt/create",
            json=payload,
            headers=headers
        )
        
        if create_response.status_code != 200:
            pytest.skip("Failed to create test data")
        
        receipt_id = create_response.json()["data"]["id"]
        
        # Then fetch it
        response = client.get(f"/inventory/consignment-receipt/{receipt_id}")
        
        assert response.status_code == 200
        data = response.json()
        assert data["data"]["id"] == receipt_id
        assert data["data"]["quantity_received"] == 30.0
    
    def test_get_consignment_receipt_not_found(self):
        """Test fetch returns 404 for non-existent ID"""
        fake_id = str(uuid4())
        
        response = client.get(f"/inventory/consignment-receipt/{fake_id}")
        
        assert response.status_code == 404
    
    def test_list_all_consignment_receipts(self):
        """Test list all receipts with pagination"""
        response = client.get("/inventory/consignment-receipt?skip=0&limit=10")
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "success"
        assert isinstance(data["data"], list)
    
    def test_list_receipts_by_supplier(self):
        """Test list receipts filtered by supplier"""
        response = client.get(
            f"/inventory/consignment-receipt/supplier/{test_supplier_id}?skip=0&limit=10"
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "success"
        assert isinstance(data["data"], list)

class TestConsignmentReceiptUpdate:
    """Test UPDATE operations"""
    
    def test_update_consignment_receipt_success(self, headers):
        """Test successful receipt update"""
        # Create receipt
        create_payload = {
            "product_id": test_product_id,
            "supplier_id": test_supplier_id,
            "receipt_number": f"CR-UPDATE-{datetime.now().timestamp()}",
            "receipt_date": date.today().isoformat(),
            "quantity_received": 50.0,
            "unit_price": 100000.0,
            "received_by": "Test User"
        }
        
        create_response = client.post(
            "/inventory/consignment-receipt/create",
            json=create_payload,
            headers=headers
        )
        
        if create_response.status_code != 200:
            pytest.skip("Failed to create test data")
        
        receipt_id = create_response.json()["data"]["id"]
        
        # Update receipt
        update_payload = {
            "quantity_received": 55.0,
            "unit_price": 105000.0,
            "notes": "Updated after recount"
        }
        
        response = client.put(
            f"/inventory/consignment-receipt/{receipt_id}",
            json=update_payload,
            headers=headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "success"
        assert data["data"]["quantity_received"] == 55.0
    
    def test_update_consignment_receipt_not_found(self, headers):
        """Test update returns 404 for non-existent ID"""
        fake_id = str(uuid4())
        
        response = client.put(
            f"/inventory/consignment-receipt/{fake_id}",
            json={"quantity_received": 60.0},
            headers=headers
        )
        
        assert response.status_code == 404
    
    def test_update_consignment_receipt_without_auth(self):
        """Test update fails without authentication"""
        fake_id = str(uuid4())
        
        response = client.put(
            f"/inventory/consignment-receipt/{fake_id}",
            json={"quantity_received": 60.0}
        )
        
        assert response.status_code in [401, 403]

class TestConsignmentReceiptDelete:
    """Test DELETE operations"""
    
    def test_delete_consignment_receipt_success(self, headers):
        """Test successful receipt deletion"""
        # Create receipt
        create_payload = {
            "product_id": test_product_id,
            "supplier_id": test_supplier_id,
            "receipt_number": f"CR-DELETE-{datetime.now().timestamp()}",
            "receipt_date": date.today().isoformat(),
            "quantity_received": 25.0,
            "received_by": "Test User"
        }
        
        create_response = client.post(
            "/inventory/consignment-receipt/create",
            json=create_payload,
            headers=headers
        )
        
        if create_response.status_code != 200:
            pytest.skip("Failed to create test data")
        
        receipt_id = create_response.json()["data"]["id"]
        
        # Delete receipt
        response = client.delete(
            f"/inventory/consignment-receipt/{receipt_id}",
            headers=headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "success"
        
        # Verify deletion by attempting to fetch
        fetch_response = client.get(f"/inventory/consignment-receipt/{receipt_id}")
        assert fetch_response.status_code == 404
    
    def test_delete_consignment_receipt_not_found(self, headers):
        """Test delete returns 404 for non-existent ID"""
        fake_id = str(uuid4())
        
        response = client.delete(
            f"/inventory/consignment-receipt/{fake_id}",
            headers=headers
        )
        
        assert response.status_code == 404
    
    def test_delete_consignment_receipt_without_auth(self):
        """Test delete fails without authentication"""
        fake_id = str(uuid4())
        
        response = client.delete(f"/inventory/consignment-receipt/{fake_id}")
        
        assert response.status_code in [401, 403]

# Run tests with: pytest test_consignment_receipt.py -v
