# Quick Reference - Konsinyasi, Adjustmen & Kehilangan Barang

## Backend Status: ✅ READY

Semua implementasi backend sudah complete. Frontend tinggal consume endpoint yang sudah ada.

---

## 1️⃣ Daftar Penerimaan Konsinyasi

### GET List
```bash
GET /products/inventory/all/consignment
```

### Response
```json
{
  "status": "success",
  "data": [
    {
      "id": "uuid",
      "name": "Oli Shell Konsinyasi",
      "supplier_name": "PT Supplier Jaya",
      "price": 150000,
      "hpp": 100000,
      "consignment_commission": 15000,
      "total_stock": 50
    }
  ]
}
```

### Create New Konsinyasi
```bash
POST /products/create/new
Content-Type: application/json
Authorization: Bearer {token}

{
  "name": "Oli Shell Konsinyasi",
  "is_consignment": true,
  "consignment_commission": 15000,
  "supplier_id": "uuid",
  "price": 150000,
  "cost": 100000,
  "brand_id": "uuid",
  "satuan_id": "uuid",
  "category_id": "uuid"
}
```

---

## 2️⃣ Daftar Adjustmen

### GET List (via Move History Report)
```bash
POST /inventory/product-move-history-report
Content-Type: application/json
Authorization: Bearer {token}

{
  "start_date": "2025-01-01",
  "end_date": "2025-01-31"
}
```

### Response (Filter `type: "adjustment"`)
```json
{
  "status": "success",
  "data": {
    "total_items": 150,
    "items": [
      {
        "product_name": "Oli Shell 1L",
        "type": "adjustment",
        "quantity": -5,
        "timestamp": "2025-01-18T10:30:00",
        "performed_by": "admin_user",
        "notes": "Rusak saat pengecekan"
      }
    ]
  }
}
```

### Create Adjustment
```bash
POST /products/inventory/adjustment
Content-Type: application/json
Authorization: Bearer {token}

{
  "product_id": "uuid",
  "adjustment_qty": -5,
  "reason": "Rusak saat pengecekan",
  "tanggal": "2025-01-18"
}
```

---

## 3️⃣ Daftar Kehilangan Barang

### GET List (via Move History Report)
```bash
POST /inventory/product-move-history-report
Content-Type: application/json
Authorization: Bearer {token}

{
  "start_date": "2025-01-01",
  "end_date": "2025-01-31"
}
```

### Response (Filter `type: "loss"`)
```json
{
  "status": "success",
  "data": {
    "items": [
      {
        "product_name": "Oli Shell 1L",
        "type": "loss",
        "quantity": -2,
        "timestamp": "2025-01-18T10:30:00",
        "performed_by": "admin_user",
        "notes": "Rusak karena banjir",
        "hpp": 100000
      }
    ]
  }
}
```

### Create Loss Record
```bash
POST /inventory/move/loss
Content-Type: application/json
Authorization: Bearer {token}

{
  "product_id": "uuid",
  "kuantitas": 2,
  "reason": "Rusak karena banjir",
  "tanggal": "2025-01-18"
}
```

---

## 📝 Frontend Implementation Examples

### JavaScript - Get Konsinyasi List
```javascript
async function getConsignmentList() {
  const response = await fetch('/products/inventory/all/consignment');
  const { data } = await response.json();
  return data;
}

// Usage
const consignments = await getConsignmentList();
consignments.forEach(item => {
  console.log(`${item.name} (${item.supplier_name}): Rp ${item.price}`);
});
```

### JavaScript - Get Adjustments
```javascript
async function getAdjustmentList(startDate, endDate) {
  const response = await fetch('/inventory/product-move-history-report', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ start_date: startDate, end_date: endDate })
  });
  
  const { data } = await response.json();
  return data.items.filter(item => item.type === 'adjustment');
}

// Usage
const adjustments = await getAdjustmentList('2025-01-01', '2025-01-31');
const summary = adjustments.reduce((sum, adj) => sum + adj.quantity, 0);
console.log(`Total adjustment: ${summary} unit`);
```

### JavaScript - Get Lost Goods & Calculate Loss
```javascript
async function getLostGoodsList(startDate, endDate) {
  const response = await fetch('/inventory/product-move-history-report', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ start_date: startDate, end_date: endDate })
  });
  
  const { data } = await response.json();
  const lostGoods = data.items.filter(item => item.type === 'loss');
  
  // Calculate total loss value
  const totalLoss = lostGoods.reduce((sum, item) => {
    return sum + (Math.abs(item.quantity) * item.hpp);
  }, 0);
  
  return { items: lostGoods, totalLoss };
}

// Usage
const { items, totalLoss } = await getLostGoodsList('2025-01-01', '2025-01-31');
console.log(`Total kerugian: Rp ${totalLoss.toLocaleString('id-ID')}`);
items.forEach(item => {
  const itemLoss = Math.abs(item.quantity) * item.hpp;
  console.log(`${item.product_name}: ${Math.abs(item.quantity)} unit (Rp ${itemLoss})`);
});
```

---

## 🔑 Key Points

| Feature | Endpoint | Method | Auth | Filter |
|---------|----------|--------|------|--------|
| Konsinyasi List | `/products/inventory/all/consignment` | GET | ❌ | `is_consignment=true` |
| Konsinyasi Create | `/products/create/new` | POST | ✅ | - |
| Adjustment List | `/inventory/product-move-history-report` | POST | ✅ | `type=adjustment` |
| Adjustment Create | `/products/inventory/adjustment` | POST | ✅ | - |
| Lost Goods List | `/inventory/product-move-history-report` | POST | ✅ | `type=loss` |
| Lost Goods Create | `/inventory/move/loss` | POST | ✅ | - |

---

## 🎯 Frontend Checklist

- [ ] Display konsinyasi list dengan supplier info
- [ ] Show adjustment list dengan date filtering
- [ ] Display lost goods dengan total loss calculation
- [ ] Add form untuk create adjustment
- [ ] Add form untuk create loss record
- [ ] Link ke detail product page
- [ ] Show user attribution (performed_by)
- [ ] Format currency values (Rp)
- [ ] Handle pagination (jika items > 100)
- [ ] Add search/filter functionality

---

**Status:** ✅ Backend Ready for Frontend Integration  
**Documentation:** [CONSIGNMENT_ADJUSTMENT_LOSTGOODS_IMPLEMENTATION.md](CONSIGNMENT_ADJUSTMENT_LOSTGOODS_IMPLEMENTATION.md)
