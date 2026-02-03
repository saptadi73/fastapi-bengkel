# Quick Start Guide - New Inventory Endpoints

**Version:** 1.0  
**Updated:** January 18, 2026

---

## 📌 What's New?

13 new endpoints implemented for inventory management:
- **6 endpoints** for Consignment Receipt Management (new feature)
- **2 endpoints** for Inventory Adjustment Updates/Deletes
- **2 endpoints** for Inventory Loss Updates/Deletes

---

## 🚀 Getting Started

### 1. Start the Server

```bash
cd c:\projek\fastapi-bengkel
python main.py
```

Server will start at `http://localhost:8000`

### 2. Get Authentication Token

```bash
curl -X POST http://localhost:8000/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "username": "admin",
    "password": "admin123"
  }'
```

Use the returned `access_token` for all write operations (POST, PUT, DELETE).

### 3. Try Your First Request

**Create Consignment Receipt:**
```bash
curl -X POST http://localhost:8000/inventory/consignment-receipt/create \
  -H "Authorization: Bearer YOUR_TOKEN_HERE" \
  -H "Content-Type: application/json" \
  -d '{
    "product_id": "550e8400-e29b-41d4-a716-446655440000",
    "supplier_id": "650e8400-e29b-41d4-a716-446655440000",
    "receipt_number": "CR-2025-001",
    "receipt_date": "2025-01-18",
    "quantity_received": 50,
    "received_by": "John Doe"
  }'
```

---

## 📚 Endpoint Groups

### Consignment Receipt
| Method | Endpoint | Auth | Purpose |
|--------|----------|------|---------|
| POST | `/inventory/consignment-receipt/create` | ✅ | Create new receipt |
| GET | `/inventory/consignment-receipt/{id}` | ❌ | Get receipt details |
| GET | `/inventory/consignment-receipt` | ❌ | List all receipts |
| GET | `/inventory/consignment-receipt/supplier/{id}` | ❌ | Get by supplier |
| PUT | `/inventory/consignment-receipt/{id}` | ✅ | Update receipt |
| DELETE | `/inventory/consignment-receipt/{id}` | ✅ | Delete receipt |

### Adjustment (Update/Delete)
| Method | Endpoint | Auth | Purpose |
|--------|----------|------|---------|
| PUT | `/products/inventory/adjustment/{id}` | ✅ | Update adjustment |
| DELETE | `/products/inventory/adjustment/{id}` | ✅ | Delete adjustment |

### Loss (Update/Delete)
| Method | Endpoint | Auth | Purpose |
|--------|----------|------|---------|
| PUT | `/inventory/loss/{loss_id}` | ✅ | Update loss |
| DELETE | `/inventory/loss/{loss_id}` | ✅ | Delete loss |

---

## 🔑 Key Features

### Inventory Reversal
When you update or delete adjustments/losses, inventory is automatically adjusted:

**Example - Adjustment Delete:**
```
Original: 100 units → 95 units (adjustment of -5)
After delete: Inventory gains back 5 units → 100 units
```

**Example - Loss Update:**
```
Original: 2 units lost
Update to: 3 units lost
Impact: 1 additional unit removed from inventory
```

### Auto-Calculation
Total value is automatically calculated:
```
total_value = quantity_received × unit_price
```

### Audit Trail
All operations are tracked with:
- `created_at` - When record was created
- `updated_at` - When record was last updated
- `performed_by` / `received_by` - Who performed the action

---

## 📖 Full Documentation

For complete endpoint details, see:
- [API_DOCUMENTATION_COMPLETE.md](API_DOCUMENTATION_COMPLETE.md) - Full API documentation
- [NEW_ENDPOINTS_SUMMARY.md](NEW_ENDPOINTS_SUMMARY.md) - Detailed implementation summary
- [IMPLEMENTATION_COMPLETE.md](IMPLEMENTATION_COMPLETE.md) - Completion checklist

---

## 🧪 Run Tests

```bash
# Run consignment receipt tests
pytest test_consignment_receipt_endpoints.py -v

# Run adjustment/loss tests
pytest test_adjustment_loss_endpoints.py -v

# Run all new endpoint tests
pytest test_*_endpoints.py -v
```

---

## 💡 Common Tasks

### Create Consignment Receipt
```bash
POST /inventory/consignment-receipt/create
Authorization: Bearer TOKEN
Content-Type: application/json

{
  "product_id": "uuid",
  "supplier_id": "uuid",
  "receipt_number": "CR-2025-001",
  "receipt_date": "2025-01-18",
  "quantity_received": 50,
  "unit_price": 100000,
  "received_by": "John"
}
```

### Update Inventory Adjustment
```bash
PUT /products/inventory/adjustment/{adjustment_id}
Authorization: Bearer TOKEN
Content-Type: application/json

{
  "old_quantity": 100,
  "new_quantity": 90,
  "reason": "Recount correction"
}
```

### Delete Loss Record
```bash
DELETE /inventory/loss/{loss_id}
Authorization: Bearer TOKEN
```

---

## ⚠️ Important Notes

1. **Authentication Required** - All write operations (POST, PUT, DELETE) need JWT token
2. **Inventory Impact** - Deleting adjustments/losses reverses their inventory impact
3. **Date Format** - Use ISO format: `YYYY-MM-DD`
4. **UUID Format** - Product and supplier IDs must be valid UUIDs
5. **Unique Receipt Numbers** - Each consignment receipt must have a unique receipt_number

---

## 🐛 Troubleshooting

### 401 Unauthorized
- Make sure you're using valid JWT token
- Token might have expired
- Login again to get a new token

### 404 Not Found
- Check if the ID (receipt_id, adjustment_id, etc.) exists
- Verify UUID format is correct

### 422 Validation Error
- Check required fields are provided
- Verify date format (YYYY-MM-DD)
- Ensure numeric fields contain valid numbers

### 500 Server Error
- Check application logs for details
- Verify database connection
- Restart the server

---

## 📞 Support

For issues or questions:
1. Check the full documentation files listed above
2. Review test files for example usage
3. Check server logs for error messages
4. Contact the development team

---

## 🎯 Next Steps

1. **Setup** - Start the server and get authentication token
2. **Test** - Try the example requests above
3. **Integrate** - Update your frontend to use new endpoints
4. **Verify** - Test inventory calculations are correct
5. **Deploy** - Push to production when ready

---

**Happy coding! 🚀**
