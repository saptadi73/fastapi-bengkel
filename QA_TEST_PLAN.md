# QA Test Plan - New Inventory Endpoints

**Version:** 1.0  
**Date:** January 18, 2026  
**Status:** Ready for Testing

---

## Test Environment Setup

### Prerequisites
- Python 3.10+
- FastAPI running on http://localhost:8000
- Valid JWT token for authentication
- Postman or similar API testing tool

### Database
- PostgreSQL running and connected
- Existing products and suppliers in database for testing

### Test Data IDs
Use these sample UUIDs (replace with actual IDs from your database):
- Product ID: `550e8400-e29b-41d4-a716-446655440000`
- Supplier ID: `650e8400-e29b-41d4-a716-446655440000`
- Admin Username: `admin`
- Admin Password: `admin123`

---

## Test Categories

### 1. Authentication Tests ✅

#### 1.1 Get JWT Token
- **Endpoint:** POST /auth/login
- **Request:** 
  ```json
  {
    "username": "admin",
    "password": "admin123"
  }
  ```
- **Expected:** 200 OK with access_token
- **Test:** ✅ PASS / ❌ FAIL

#### 1.2 Test with Invalid Credentials
- **Endpoint:** POST /auth/login
- **Request:** Invalid username/password
- **Expected:** 401 Unauthorized
- **Test:** ✅ PASS / ❌ FAIL

#### 1.3 Protected Endpoint Without Token
- **Endpoint:** POST /inventory/consignment-receipt/create
- **Headers:** None
- **Expected:** 401 Unauthorized
- **Test:** ✅ PASS / ❌ FAIL

---

## Consignment Receipt Tests (6 endpoints)

### 2.1 Create Consignment Receipt
**Endpoint:** POST /inventory/consignment-receipt/create  
**Auth:** ✅ Required

#### Test 2.1.1: Create with Valid Data
```json
{
  "product_id": "550e8400-e29b-41d4-a716-446655440000",
  "supplier_id": "650e8400-e29b-41d4-a716-446655440000",
  "receipt_number": "CR-TEST-001",
  "receipt_date": "2025-01-18",
  "quantity_received": 50,
  "unit_price": 100000,
  "received_by": "Test User"
}
```
- **Expected:** 200 OK
- **Response Contains:** id, receipt_number, created_at
- **Test:** ✅ PASS / ❌ FAIL

#### Test 2.1.2: Create with Missing Required Field
```json
{
  "product_id": "550e8400-e29b-41d4-a716-446655440000",
  "supplier_id": "650e8400-e29b-41d4-a716-446655440000",
  "receipt_number": "CR-TEST-002"
  // Missing receipt_date, quantity_received, received_by
}
```
- **Expected:** 422 Unprocessable Entity
- **Test:** ✅ PASS / ❌ FAIL

#### Test 2.1.3: Create with Duplicate Receipt Number
```json
{
  "product_id": "550e8400-e29b-41d4-a716-446655440000",
  "supplier_id": "650e8400-e29b-41d4-a716-446655440000",
  "receipt_number": "CR-TEST-001", // Same as Test 2.1.1
  "receipt_date": "2025-01-19",
  "quantity_received": 30,
  "received_by": "Test User"
}
```
- **Expected:** 400 Bad Request (duplicate receipt number)
- **Test:** ✅ PASS / ❌ FAIL

#### Test 2.1.4: Auto-Calculate Total Value
- **Receipt Number:** CR-TEST-CALC-001
- **Quantity:** 50
- **Unit Price:** 100000
- **Expected Total Value:** 5000000
- **Verify:** Response contains total_value = 5000000
- **Test:** ✅ PASS / ❌ FAIL

---

### 2.2 Get Single Consignment Receipt
**Endpoint:** GET /inventory/consignment-receipt/{receipt_id}  
**Auth:** ❌ Not Required

#### Test 2.2.1: Get Existing Receipt
- **Receipt ID:** (from Test 2.1.1)
- **Expected:** 200 OK
- **Response Contains:** receipt_number, receipt_date, quantity_received
- **Test:** ✅ PASS / ❌ FAIL

#### Test 2.2.2: Get Non-Existent Receipt
- **Receipt ID:** 00000000-0000-0000-0000-000000000000
- **Expected:** 404 Not Found
- **Test:** ✅ PASS / ❌ FAIL

---

### 2.3 List All Consignment Receipts
**Endpoint:** GET /inventory/consignment-receipt  
**Auth:** ❌ Not Required

#### Test 2.3.1: List with Default Pagination
- **Query:** ?skip=0&limit=100
- **Expected:** 200 OK
- **Response:** Array of receipts
- **Verify:** Contains receipts from previous tests
- **Test:** ✅ PASS / ❌ FAIL

#### Test 2.3.2: List with Custom Pagination
- **Query:** ?skip=1&limit=10
- **Expected:** 200 OK
- **Verify:** Returns at most 10 records
- **Test:** ✅ PASS / ❌ FAIL

---

### 2.4 List by Supplier
**Endpoint:** GET /inventory/consignment-receipt/supplier/{supplier_id}  
**Auth:** ❌ Not Required

#### Test 2.4.1: Get Receipts for Specific Supplier
- **Supplier ID:** 650e8400-e29b-41d4-a716-446655440000
- **Expected:** 200 OK
- **Verify:** All returned receipts have matching supplier_id
- **Test:** ✅ PASS / ❌ FAIL

#### Test 2.4.2: Get for Non-Existent Supplier
- **Supplier ID:** 00000000-0000-0000-0000-000000000000
- **Expected:** 200 OK (empty array or no results)
- **Test:** ✅ PASS / ❌ FAIL

---

### 2.5 Update Consignment Receipt
**Endpoint:** PUT /inventory/consignment-receipt/{receipt_id}  
**Auth:** ✅ Required

#### Test 2.5.1: Update Quantity
```json
{
  "quantity_received": 55
}
```
- **Receipt ID:** (from Test 2.1.1)
- **Expected:** 200 OK
- **Verify:** quantity_received updated to 55
- **Verify:** updated_at timestamp changed
- **Test:** ✅ PASS / ❌ FAIL

#### Test 2.5.2: Update Unit Price
```json
{
  "unit_price": 105000
}
```
- **Expected:** 200 OK
- **Verify:** unit_price updated to 105000
- **Test:** ✅ PASS / ❌ FAIL

#### Test 2.5.3: Update Non-Existent Receipt
- **Receipt ID:** 00000000-0000-0000-0000-000000000000
- **Expected:** 404 Not Found
- **Test:** ✅ PASS / ❌ FAIL

#### Test 2.5.4: Update Without Auth
- **Headers:** None
- **Expected:** 401 Unauthorized
- **Test:** ✅ PASS / ❌ FAIL

---

### 2.6 Delete Consignment Receipt
**Endpoint:** DELETE /inventory/consignment-receipt/{receipt_id}  
**Auth:** ✅ Required

#### Test 2.6.1: Delete Existing Receipt
- **Receipt ID:** CR-TEST-DEL-001
- **Expected:** 200 OK
- **Verify:** Response indicates successful deletion
- **Test:** ✅ PASS / ❌ FAIL

#### Test 2.6.2: Verify Deletion
- **Get:** Deleted receipt by ID
- **Expected:** 404 Not Found
- **Test:** ✅ PASS / ❌ FAIL

#### Test 2.6.3: Delete Non-Existent Receipt
- **Receipt ID:** 00000000-0000-0000-0000-000000000000
- **Expected:** 404 Not Found
- **Test:** ✅ PASS / ❌ FAIL

#### Test 2.6.4: Delete Without Auth
- **Headers:** None
- **Expected:** 401 Unauthorized
- **Test:** ✅ PASS / ❌ FAIL

---

## Inventory Adjustment Tests (2 endpoints)

### 3.1 Create Adjustment (Reference - Existing Endpoint)
**Endpoint:** POST /products/inventory/adjustment  
**Auth:** ✅ Required

#### Test 3.1.1: Create Valid Adjustment
```json
{
  "product_id": "550e8400-e29b-41d4-a716-446655440000",
  "old_quantity": 100,
  "new_quantity": 95,
  "reason": "Physical count correction",
  "performed_by": "Test User"
}
```
- **Expected:** 200 OK
- **Verify:** id returned (save for update/delete tests)
- **Test:** ✅ PASS / ❌ FAIL

---

### 3.2 Update Adjustment
**Endpoint:** PUT /products/inventory/adjustment/{adjustment_id}  
**Auth:** ✅ Required

#### Test 3.2.1: Update Quantity
```json
{
  "old_quantity": 100,
  "new_quantity": 90,
  "reason": "Revised correction",
  "performed_by": "Test User 2"
}
```
- **Adjustment ID:** (from Test 3.1.1)
- **Expected:** 200 OK
- **Verify:** new_quantity updated to 90
- **Verify:** "updated" in response message
- **Test:** ✅ PASS / ❌ FAIL

#### Test 3.2.2: Update Non-Existent
- **Adjustment ID:** 00000000-0000-0000-0000-000000000000
- **Expected:** 404 Not Found
- **Test:** ✅ PASS / ❌ FAIL

#### Test 3.2.3: Update Without Auth
- **Headers:** None
- **Expected:** 401 Unauthorized
- **Test:** ✅ PASS / ❌ FAIL

---

### 3.3 Delete Adjustment
**Endpoint:** DELETE /products/inventory/adjustment/{adjustment_id}  
**Auth:** ✅ Required

#### Test 3.3.1: Delete Valid Adjustment
- **Adjustment ID:** (from Test 3.1.1)
- **Expected:** 200 OK
- **Verify:** "reversed" or "deleted" in message
- **Verify:** Inventory impact reversed
- **Test:** ✅ PASS / ❌ FAIL

#### Test 3.3.2: Verify Adjustment Deleted
- **Adjustment ID:** (from Test 3.3.1)
- **Method:** Try to get it
- **Expected:** 404 Not Found
- **Test:** ✅ PASS / ❌ FAIL

#### Test 3.3.3: Delete Non-Existent
- **Adjustment ID:** 00000000-0000-0000-0000-000000000000
- **Expected:** 404 Not Found
- **Test:** ✅ PASS / ❌ FAIL

---

## Inventory Loss Tests (2 endpoints)

### 4.1 Create Loss (Reference - Existing Endpoint)
**Endpoint:** POST /inventory/move/loss  
**Auth:** ✅ Required

#### Test 4.1.1: Create Valid Loss
```json
{
  "product_id": "550e8400-e29b-41d4-a716-446655440000",
  "kuantitas": 2,
  "reason": "Damaged during inspection",
  "tanggal": "2025-01-18"
}
```
- **Expected:** 200 OK
- **Verify:** id returned (save for update/delete tests)
- **Test:** ✅ PASS / ❌ FAIL

---

### 4.2 Update Loss
**Endpoint:** PUT /inventory/loss/{loss_id}  
**Auth:** ✅ Required

#### Test 4.2.1: Update Quantity
```json
{
  "product_id": "550e8400-e29b-41d4-a716-446655440000",
  "kuantitas": 3,
  "reason": "Additional damaged units found",
  "tanggal": "2025-01-18"
}
```
- **Loss ID:** (from Test 4.1.1)
- **Expected:** 200 OK
- **Verify:** kuantitas updated to 3
- **Verify:** "updated" in message
- **Verify:** Inventory adjusted (1 additional unit removed)
- **Test:** ✅ PASS / ❌ FAIL

#### Test 4.2.2: Update Non-Existent
- **Loss ID:** 00000000-0000-0000-0000-000000000000
- **Expected:** 404 Not Found
- **Test:** ✅ PASS / ❌ FAIL

#### Test 4.2.3: Update Without Auth
- **Headers:** None
- **Expected:** 401 Unauthorized
- **Test:** ✅ PASS / ❌ FAIL

---

### 4.3 Delete Loss
**Endpoint:** DELETE /inventory/loss/{loss_id}  
**Auth:** ✅ Required

#### Test 4.3.1: Delete Valid Loss
- **Loss ID:** (from Test 4.1.1)
- **Expected:** 200 OK
- **Verify:** "reversed" in message
- **Verify:** Inventory impact reversed (lost units added back)
- **Test:** ✅ PASS / ❌ FAIL

#### Test 4.3.2: Verify Loss Deleted
- **Loss ID:** (from Test 4.3.1)
- **Method:** Try to get it
- **Expected:** 404 Not Found
- **Test:** ✅ PASS / ❌ FAIL

#### Test 4.3.3: Delete Non-Existent
- **Loss ID:** 00000000-0000-0000-0000-000000000000
- **Expected:** 404 Not Found
- **Test:** ✅ PASS / ❌ FAIL

---

## Integration Tests

### 5.1 End-to-End Consignment Receipt Flow
**Scenario:** Create → Read → Update → Delete

1. **Create** (Test 2.1.1) ✅ PASS / ❌ FAIL
2. **Read** (Test 2.2.1) ✅ PASS / ❌ FAIL
3. **List** (Test 2.3.1) ✅ PASS / ❌ FAIL
4. **Update** (Test 2.5.1) ✅ PASS / ❌ FAIL
5. **Delete** (Test 2.6.1) ✅ PASS / ❌ FAIL

### 5.2 Inventory Reversal Verification
**Scenario:** Create adjustment → Delete → Verify inventory restored

1. **Create Adjustment** (Test 3.1.1) ✅ PASS / ❌ FAIL
2. **Check Inventory** - Note current value
3. **Delete Adjustment** (Test 3.3.1) ✅ PASS / ❌ FAIL
4. **Check Inventory** - Verify it was reversed
5. **Result:** ✅ PASS / ❌ FAIL

### 5.3 Loss Update Impact Verification
**Scenario:** Create loss → Update → Verify inventory impact

1. **Create Loss** (Test 4.1.1) ✅ PASS / ❌ FAIL
2. **Check Inventory** - Note reduction
3. **Update Loss** (Test 4.2.1) ✅ PASS / ❌ FAIL
4. **Check Inventory** - Verify additional reduction
5. **Result:** ✅ PASS / ❌ FAIL

---

## Performance Tests

### 6.1 Response Time
| Operation | Expected | Actual | Status |
|-----------|----------|--------|--------|
| Create Receipt | <100ms | | ✅/❌ |
| Get Receipt | <50ms | | ✅/❌ |
| List Receipts | <200ms | | ✅/❌ |
| Update Receipt | <100ms | | ✅/❌ |
| Delete Receipt | <100ms | | ✅/❌ |

### 6.2 Load Test
- **Concurrent Users:** 10
- **Duration:** 1 minute
- **Expected:** No errors
- **Result:** ✅ PASS / ❌ FAIL

---

## Security Tests

### 7.1 Authentication
- [ ] Missing token returns 401
- [ ] Invalid token returns 401
- [ ] Expired token returns 401
- [ ] Valid token allows access

### 7.2 Authorization
- [ ] GET endpoints allow public access
- [ ] POST/PUT/DELETE require authentication
- [ ] Users can only access their own data

### 7.3 Input Validation
- [ ] SQL injection attempts blocked
- [ ] XSS attempts blocked
- [ ] Required fields validated
- [ ] Data type validation working

---

## Data Integrity Tests

### 8.1 Unique Constraints
- [ ] Duplicate receipt_number rejected
- [ ] UUID integrity maintained
- [ ] Foreign key constraints enforced

### 8.2 Audit Trail
- [ ] created_at timestamp set on create
- [ ] updated_at timestamp updated on modify
- [ ] performed_by/received_by tracked
- [ ] Change history maintained

---

## Bug Report Template

### Format
```
**Test ID:** [e.g., 2.1.1]
**Title:** Brief description
**Expected:** What should happen
**Actual:** What actually happened
**Severity:** Critical/High/Medium/Low
**Steps to Reproduce:**
1. ...
2. ...
3. ...
**Attachment:** Screenshot/Log
```

---

## Test Execution Summary

### Passed Tests
- Total: __ / __
- Percentage: __%

### Failed Tests
- Total: __ / __
- Percentage: __%

### Test Date: ________

### Tested By: ________

### Status: ✅ PASS / ⚠️ PASS WITH ISSUES / ❌ FAIL

---

## Sign-Off

- [ ] All tests executed
- [ ] All critical issues resolved
- [ ] Documentation verified
- [ ] Ready for deployment

**QA Lead Signature:** ________________  
**Date:** ________________

---

**Ready for Testing! 🧪**
