"""
Critical Path Testing for Average Costing Implementation
Tests the main functionality of average costing method
"""
import requests
import json
from datetime import datetime, date
from decimal import Decimal

# Base URL for API
BASE_URL = "http://localhost:8000"

# Test results tracker
test_results = []

def log_test(test_name, passed, message=""):
    """Log test result"""
    status = "✅ PASS" if passed else "❌ FAIL"
    test_results.append({
        "test": test_name,
        "passed": passed,
        "message": message
    })
    print(f"{status}: {test_name}")
    if message:
        print(f"   {message}")

def print_summary():
    """Print test summary"""
    print("\n" + "=" * 70)
    print("TEST SUMMARY")
    print("=" * 70)
    passed = sum(1 for r in test_results if r['passed'])
    total = len(test_results)
    print(f"Total Tests: {total}")
    print(f"Passed: {passed}")
    print(f"Failed: {total - passed}")
    print(f"Success Rate: {(passed/total*100):.1f}%")
    print("=" * 70)
    
    if total - passed > 0:
        print("\n❌ Failed Tests:")
        for r in test_results:
            if not r['passed']:
                print(f"  - {r['test']}: {r['message']}")

def test_1_get_products():
    """Test 1: Get all products to find test product"""
    print("\n📝 Test 1: Get all products")
    try:
        response = requests.get(f"{BASE_URL}/products/all")
        if response.status_code == 200:
            data = response.json()
            if data.get('success') and data.get('data'):
                products = data['data']
                print(f"   Found {len(products)} products")
                
                # Find a non-consignment product for testing
                test_product = None
                for p in products:
                    if not p.get('is_consignment', False):
                        test_product = p
                        break
                
                if test_product:
                    log_test("Get Products", True, f"Found test product: {test_product['name']}")
                    return test_product
                else:
                    log_test("Get Products", False, "No non-consignment product found for testing")
                    return None
            else:
                log_test("Get Products", False, "No products in response")
                return None
        else:
            log_test("Get Products", False, f"HTTP {response.status_code}")
            return None
    except Exception as e:
        log_test("Get Products", False, str(e))
        return None

def test_2_get_suppliers():
    """Test 2: Get suppliers for PO creation"""
    print("\n📝 Test 2: Get suppliers")
    try:
        response = requests.get(f"{BASE_URL}/suppliers/all")
        if response.status_code == 200:
            data = response.json()
            if data.get('success') and data.get('data'):
                suppliers = data['data']
                if suppliers:
                    log_test("Get Suppliers", True, f"Found {len(suppliers)} suppliers")
                    return suppliers[0]
                else:
                    log_test("Get Suppliers", False, "No suppliers found")
                    return None
            else:
                log_test("Get Suppliers", False, "No suppliers in response")
                return None
        else:
            log_test("Get Suppliers", False, f"HTTP {response.status_code}")
            return None
    except Exception as e:
        log_test("Get Suppliers", False, str(e))
        return None

def test_3_check_initial_cost(product_id):
    """Test 3: Check initial product cost"""
    print(f"\n📝 Test 3: Check initial cost for product {product_id}")
    try:
        response = requests.get(f"{BASE_URL}/products/{product_id}")
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                product = data['data']
                initial_cost = product.get('cost')
                print(f"   Initial cost: {initial_cost}")
                log_test("Check Initial Cost", True, f"Initial cost: {initial_cost}")
                return initial_cost
            else:
                log_test("Check Initial Cost", False, "Product not found")
                return None
        else:
            log_test("Check Initial Cost", False, f"HTTP {response.status_code}")
            return None
    except Exception as e:
        log_test("Check Initial Cost", False, str(e))
        return None

def test_4_check_inventory(product_id):
    """Test 4: Check initial inventory"""
    print(f"\n📝 Test 4: Check initial inventory for product {product_id}")
    try:
        response = requests.get(f"{BASE_URL}/products/inventory/{product_id}")
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                inventory = data['data']
                quantity = inventory.get('total_stock', 0)
                print(f"   Initial quantity: {quantity}")
                log_test("Check Initial Inventory", True, f"Initial quantity: {quantity}")
                return quantity
            else:
                log_test("Check Initial Inventory", False, "Inventory not found")
                return 0
        else:
            log_test("Check Initial Inventory", False, f"HTTP {response.status_code}")
            return 0
    except Exception as e:
        log_test("Check Initial Inventory", False, str(e))
        return 0

def test_5_get_cost_history(product_id):
    """Test 5: Get cost history (should be empty initially)"""
    print(f"\n📝 Test 5: Get initial cost history for product {product_id}")
    try:
        response = requests.get(f"{BASE_URL}/products/{product_id}/cost-history")
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                history = data['data']
                print(f"   Found {len(history)} cost history records")
                log_test("Get Cost History", True, f"Initial history count: {len(history)}")
                return len(history)
            else:
                log_test("Get Cost History", False, "Failed to get cost history")
                return None
        else:
            log_test("Get Cost History", False, f"HTTP {response.status_code}")
            return None
    except Exception as e:
        log_test("Get Cost History", False, str(e))
        return None

def test_6_get_cost_summary(product_id):
    """Test 6: Get cost summary"""
    print(f"\n📝 Test 6: Get cost summary for product {product_id}")
    try:
        response = requests.get(f"{BASE_URL}/products/{product_id}/cost-summary")
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                summary = data['data']
                print(f"   Current cost: {summary.get('current_cost')}")
                print(f"   Current quantity: {summary.get('current_quantity')}")
                print(f"   Total cost changes: {summary.get('total_cost_changes')}")
                log_test("Get Cost Summary", True, "Cost summary retrieved successfully")
                return summary
            else:
                log_test("Get Cost Summary", False, "Failed to get cost summary")
                return None
        else:
            log_test("Get Cost Summary", False, f"HTTP {response.status_code}")
            return None
    except Exception as e:
        log_test("Get Cost Summary", False, str(e))
        return None

def main():
    """Run all critical path tests"""
    print("=" * 70)
    print("AVERAGE COSTING - CRITICAL PATH TESTING")
    print("=" * 70)
    print(f"Testing against: {BASE_URL}")
    print(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Test 1: Get products
    test_product = test_1_get_products()
    if not test_product:
        print("\n❌ Cannot continue testing without a test product")
        print_summary()
        return
    
    product_id = test_product['id']
    product_name = test_product['name']
    
    print(f"\n🎯 Using test product: {product_name} (ID: {product_id})")
    
    # Test 2: Get suppliers
    test_supplier = test_2_get_suppliers()
    if not test_supplier:
        print("\n⚠️  Warning: No supplier found, some tests may be limited")
    
    # Test 3: Check initial cost
    initial_cost = test_3_check_initial_cost(product_id)
    
    # Test 4: Check initial inventory
    initial_quantity = test_4_check_inventory(product_id)
    
    # Test 5: Get cost history
    initial_history_count = test_5_get_cost_history(product_id)
    
    # Test 6: Get cost summary
    cost_summary = test_6_get_cost_summary(product_id)
    
    # Print summary
    print_summary()
    
    print("\n" + "=" * 70)
    print("NEXT STEPS FOR MANUAL TESTING")
    print("=" * 70)
    print("\n📝 To complete testing, please:")
    print(f"1. Create a Purchase Order for product: {product_name}")
    print(f"   - Product ID: {product_id}")
    print(f"   - Current Cost: {initial_cost}")
    print(f"   - Current Quantity: {initial_quantity}")
    print("\n2. Change PO status to 'diterima'")
    print("\n3. Verify:")
    print(f"   - Check updated cost: GET {BASE_URL}/products/{product_id}")
    print(f"   - Check cost history: GET {BASE_URL}/products/{product_id}/cost-history")
    print(f"   - Check cost summary: GET {BASE_URL}/products/{product_id}/cost-summary")
    print("\n4. Expected behavior:")
    print("   - Cost should be calculated using average costing formula")
    print("   - Cost history should have a new record")
    print("   - Inventory quantity should increase")
    
    print("\n" + "=" * 70)

if __name__ == "__main__":
    main()
