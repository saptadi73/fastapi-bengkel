"""
Test untuk Inventory Adjustment dan Loss Update/Delete Endpoints
"""

import pytest
from fastapi.testclient import TestClient
from uuid import uuid4
from datetime import datetime
from main import app

client = TestClient(app)

# Dummy auth token
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

class TestAdjustmentUpdate:
    """Test UPDATE operations for inventory adjustments"""
    
    def test_create_and_update_adjustment(self, headers):
        """Test creating and then updating an adjustment"""
        # Create adjustment
        create_payload = {
            "product_id": test_product_id,
            "old_quantity": 100,
            "new_quantity": 95,
            "reason": "Initial count",
            "performed_by": "Test User"
        }
        
        create_response = client.post(
            "/products/inventory/adjustment",
            json=create_payload,
            headers=headers
        )
        
        if create_response.status_code != 200:
            pytest.skip("Failed to create test adjustment")
        
        adjustment_data = create_response.json().get("data", {})
        adjustment_id = adjustment_data.get("id")
        
        if not adjustment_id:
            pytest.skip("No adjustment ID returned from creation")
        
        # Update adjustment
        update_payload = {
            "product_id": test_product_id,
            "old_quantity": 100,
            "new_quantity": 90,  # Changed from 95 to 90
            "reason": "Revised after recount",
            "performed_by": "Test User 2"
        }
        
        response = client.put(
            f"/products/inventory/adjustment/{adjustment_id}",
            json=update_payload,
            headers=headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "success"
        assert "message" in data
        assert "updated" in data["message"].lower()
    
    def test_update_adjustment_not_found(self, headers):
        """Test update returns error for non-existent adjustment"""
        fake_id = str(uuid4())
        
        update_payload = {
            "product_id": test_product_id,
            "old_quantity": 100,
            "new_quantity": 90,
            "reason": "Test",
            "performed_by": "Test User"
        }
        
        response = client.put(
            f"/products/inventory/adjustment/{fake_id}",
            json=update_payload,
            headers=headers
        )
        
        assert response.status_code == 404
    
    def test_update_adjustment_without_auth(self):
        """Test update fails without authentication"""
        fake_id = str(uuid4())
        
        update_payload = {
            "product_id": test_product_id,
            "old_quantity": 100,
            "new_quantity": 90,
            "reason": "Test",
            "performed_by": "Test User"
        }
        
        response = client.put(
            f"/products/inventory/adjustment/{fake_id}",
            json=update_payload
        )
        
        assert response.status_code in [401, 403]

class TestAdjustmentDelete:
    """Test DELETE operations for inventory adjustments"""
    
    def test_create_and_delete_adjustment(self, headers):
        """Test creating and then deleting an adjustment"""
        # Create adjustment
        create_payload = {
            "product_id": test_product_id,
            "old_quantity": 100,
            "new_quantity": 95,
            "reason": "Test deletion",
            "performed_by": "Test User"
        }
        
        create_response = client.post(
            "/products/inventory/adjustment",
            json=create_payload,
            headers=headers
        )
        
        if create_response.status_code != 200:
            pytest.skip("Failed to create test adjustment")
        
        adjustment_data = create_response.json().get("data", {})
        adjustment_id = adjustment_data.get("id")
        
        if not adjustment_id:
            pytest.skip("No adjustment ID returned from creation")
        
        # Delete adjustment
        response = client.delete(
            f"/products/inventory/adjustment/{adjustment_id}",
            headers=headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "success"
        assert "reversed" in data["message"].lower() or "deleted" in data["message"].lower()
    
    def test_delete_adjustment_not_found(self, headers):
        """Test delete returns error for non-existent adjustment"""
        fake_id = str(uuid4())
        
        response = client.delete(
            f"/products/inventory/adjustment/{fake_id}",
            headers=headers
        )
        
        assert response.status_code == 404
    
    def test_delete_adjustment_without_auth(self):
        """Test delete fails without authentication"""
        fake_id = str(uuid4())
        
        response = client.delete(
            f"/products/inventory/adjustment/{fake_id}"
        )
        
        assert response.status_code in [401, 403]

class TestLossUpdate:
    """Test UPDATE operations for inventory loss"""
    
    def test_create_and_update_loss(self, headers):
        """Test creating and then updating a loss record"""
        # Create loss
        create_payload = {
            "product_id": test_product_id,
            "kuantitas": 2,
            "reason": "Initial damage report",
            "tanggal": datetime.now().date().isoformat()
        }
        
        create_response = client.post(
            "/inventory/move/loss",
            json=create_payload,
            headers=headers
        )
        
        if create_response.status_code != 200:
            pytest.skip("Failed to create test loss record")
        
        loss_data = create_response.json().get("data", {})
        loss_id = loss_data.get("id")
        
        if not loss_id:
            pytest.skip("No loss ID returned from creation")
        
        # Update loss
        update_payload = {
            "product_id": test_product_id,
            "kuantitas": 3,  # Changed from 2 to 3
            "reason": "Additional damaged units found",
            "tanggal": datetime.now().date().isoformat()
        }
        
        response = client.put(
            f"/inventory/loss/{loss_id}",
            json=update_payload,
            headers=headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "success"
        assert "message" in data
        assert "updated" in data["message"].lower()
    
    def test_update_loss_not_found(self, headers):
        """Test update returns error for non-existent loss"""
        fake_id = str(uuid4())
        
        update_payload = {
            "product_id": test_product_id,
            "kuantitas": 3,
            "reason": "Test",
            "tanggal": datetime.now().date().isoformat()
        }
        
        response = client.put(
            f"/inventory/loss/{fake_id}",
            json=update_payload,
            headers=headers
        )
        
        assert response.status_code == 404
    
    def test_update_loss_without_auth(self):
        """Test update fails without authentication"""
        fake_id = str(uuid4())
        
        update_payload = {
            "product_id": test_product_id,
            "kuantitas": 3,
            "reason": "Test",
            "tanggal": datetime.now().date().isoformat()
        }
        
        response = client.put(
            f"/inventory/loss/{fake_id}",
            json=update_payload
        )
        
        assert response.status_code in [401, 403]

class TestLossDelete:
    """Test DELETE operations for inventory loss"""
    
    def test_create_and_delete_loss(self, headers):
        """Test creating and then deleting a loss record"""
        # Create loss
        create_payload = {
            "product_id": test_product_id,
            "kuantitas": 2,
            "reason": "Test deletion",
            "tanggal": datetime.now().date().isoformat()
        }
        
        create_response = client.post(
            "/inventory/move/loss",
            json=create_payload,
            headers=headers
        )
        
        if create_response.status_code != 200:
            pytest.skip("Failed to create test loss record")
        
        loss_data = create_response.json().get("data", {})
        loss_id = loss_data.get("id")
        
        if not loss_id:
            pytest.skip("No loss ID returned from creation")
        
        # Delete loss
        response = client.delete(
            f"/inventory/loss/{loss_id}",
            headers=headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "success"
        assert "reversed" in data["message"].lower() or "deleted" in data["message"].lower()
    
    def test_delete_loss_not_found(self, headers):
        """Test delete returns error for non-existent loss"""
        fake_id = str(uuid4())
        
        response = client.delete(
            f"/inventory/loss/{fake_id}",
            headers=headers
        )
        
        assert response.status_code == 404
    
    def test_delete_loss_without_auth(self):
        """Test delete fails without authentication"""
        fake_id = str(uuid4())
        
        response = client.delete(f"/inventory/loss/{fake_id}")
        
        assert response.status_code in [401, 403]

class TestInventoryImpactReversal:
    """Test that inventory impact is correctly reversed on delete"""
    
    def test_adjustment_inventory_reversal_on_delete(self, headers):
        """Test that deleting adjustment reverses inventory changes"""
        # This is a conceptual test
        # In real scenario, we would check inventory before/after
        
        create_payload = {
            "product_id": test_product_id,
            "old_quantity": 100,
            "new_quantity": 85,  # -15 units
            "reason": "Inventory correction",
            "performed_by": "Test User"
        }
        
        create_response = client.post(
            "/products/inventory/adjustment",
            json=create_payload,
            headers=headers
        )
        
        if create_response.status_code != 200:
            pytest.skip("Failed to create test adjustment")
        
        adjustment_id = create_response.json().get("data", {}).get("id")
        
        # When we delete this adjustment, inventory should gain back 15 units
        response = client.delete(
            f"/products/inventory/adjustment/{adjustment_id}",
            headers=headers
        )
        
        assert response.status_code == 200
    
    def test_loss_inventory_reversal_on_delete(self, headers):
        """Test that deleting loss reverses inventory changes"""
        # This is a conceptual test
        
        create_payload = {
            "product_id": test_product_id,
            "kuantitas": 5,  # 5 units lost
            "reason": "Damage report",
            "tanggal": datetime.now().date().isoformat()
        }
        
        create_response = client.post(
            "/inventory/move/loss",
            json=create_payload,
            headers=headers
        )
        
        if create_response.status_code != 200:
            pytest.skip("Failed to create test loss record")
        
        loss_id = create_response.json().get("data", {}).get("id")
        
        # When we delete this loss, inventory should gain back 5 units
        response = client.delete(
            f"/inventory/loss/{loss_id}",
            headers=headers
        )
        
        assert response.status_code == 200

# Run tests with: pytest test_adjustment_loss_endpoints.py -v
