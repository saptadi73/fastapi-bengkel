# Consignment Receipt, Adjustment & Lost Goods List Implementation Guide

## Status: ✅ Backend Implementation Complete

Dokumentasi ini merangkum implementasi backend untuk tiga fitur list/report:
1. **Daftar Penerimaan Konsinyasi** (Consignment Receipt List)
2. **Daftar Adjustmen** (Adjustment List)
3. **Daftar Kehilangan Barang** (Lost Goods List)

---

## 📋 1. Daftar Penerimaan Konsinyasi (Consignment Receipt List)

### Tujuan
Menampilkan daftar semua produk yang diterima sebagai konsinyasi dari supplier, termasuk:
- Informasi produk konsinyasi
- Supplier/vendor yang menyediakan
- Stok yang ada
- Komisi per unit

### Endpoint yang Sudah Ada

#### 1.1 Get All Consignment Inventory
**Endpoint:** `GET /products/inventory/all/consignment`  
**Auth Required:** ❌ No

**Response:**
```json
{
  "status": "success",
  "data": [
    {
      "id": "550e8400-e29b-41d4-a716-446655440000",
      "name": "Oli Shell Konsinyasi",
      "type": "sparepart",
      "description": "Oli mesin berkualitas tinggi - konsinyasi",
      "price": 150000,
      "hpp": 100000,
      "min_stock": 10,
      "is_consignment": true,
      "consignment_commission": 15000,
      "category_name": "Sparepart",
      "brand_name": "Shell",
      "satuan_name": "Botol",
      "supplier_name": "PT Supplier Jaya",
      "total_stock": 50
    }
  ]
}
```

**Field Definitions:**
- `id` (UUID): ID unik produk
- `name` (string): Nama produk
- `type` (string): Jenis produk
- `description` (string): Deskripsi produk
- `price` (decimal): Harga jual
- `hpp` (decimal): Harga pokok penjualan
- `min_stock` (decimal): Stok minimum
- `is_consignment` (boolean): Flag konsinyasi (always true)
- `consignment_commission` (decimal): Komisi per unit (Rp)
- `category_name` (string): Kategori produk
- `brand_name` (string): Brand/merek
- `satuan_name` (string): Satuan (unit)
- `supplier_name` (string): Nama supplier/vendor
- `total_stock` (decimal): Total stok yang ada

### Implementasi Backend

**File:** [services/services_product.py](services/services_product.py)  
**Function:** `getAllInventoryProductsConsignment(db: Session)`

```python
def getAllInventoryProductsConsignment(db: Session):
    """
    Get all inventory products yang merupakan konsinyasi
    Hanya menampilkan produk dengan is_consignment = true
    """
    try:
        products = db.query(Product).filter(
            Product.is_consignment == True
        ).all()
        
        result = []
        for product in products:
            inventory = get_or_create_inventory(db, product.id)
            result.append({
                'id': str(product.id),
                'name': product.name,
                'type': product.type,
                'description': product.description,
                'price': inventory.price if inventory else product.price,
                'hpp': inventory.cost if inventory else product.cost,
                'min_stock': product.min_stock,
                'is_consignment': product.is_consignment,
                'consignment_commission': product.consignment_commission,
                'category_name': product.category.name if product.category else None,
                'brand_name': product.brand.name if product.brand else None,
                'satuan_name': product.satuan.name if product.satuan else None,
                'supplier_name': product.supplier.nama if product.supplier else None,
                'total_stock': inventory.quantity if inventory else 0
            })
        
        return result
    except Exception as e:
        raise Exception(f"Error fetching consignment products: {str(e)}")
```

**File:** [routes/routes_product.py](routes/routes_product.py)  
**Route:** `GET /products/inventory/all/consignment`

```python
@router.get("/inventory/all/consignment")
def get_consignment_inventory(db: Session = Depends(get_db)):
    try:
        result = getAllInventoryProductsConsignment(db)
        return success_response(
            data=result,
            message="Daftar produk konsinyasi berhasil diambil"
        )
    except Exception as e:
        return error_response(message=f"Gagal mengambil daftar konsinyasi: {str(e)}")
```

### Usage Example (Frontend)
```javascript
// Ambil daftar konsinyasi
const response = await fetch('/products/inventory/all/consignment');
const { data: consignmentList } = await response.json();

// Display di table/list
consignmentList.forEach(item => {
  console.log(`${item.name} (${item.supplier_name}): ${item.total_stock} unit @ Rp ${item.price}`);
});
```

---

## 🔄 2. Daftar Adjustmen (Adjustment List)

### Tujuan
Menampilkan riwayat semua adjustment stok yang dilakukan, termasuk:
- Tanggal adjustment
- Produk yang di-adjust
- Jumlah adjustment
- Alasan adjustment
- User yang melakukan

### Endpoint yang Sudah Ada

#### 2.1 Create Product Adjustment
**Endpoint:** `POST /products/inventory/adjustment`  
**Auth Required:** ✅ Yes

**Request Body:**
```json
{
  "product_id": "550e8400-e29b-41d4-a716-446655440000",
  "adjustment_qty": -5,
  "reason": "Rusak saat pengecekan",
  "tanggal": "2025-01-18"
}
```

**Response:**
```json
{
  "status": "success",
  "data": {
    "id": "adj-uuid",
    "product_id": "550e8400-e29b-41d4-a716-446655440000",
    "quantity": -5,
    "reason": "Rusak saat pengecekan",
    "date": "2025-01-18",
    "created_at": "2025-01-18T10:30:00"
  },
  "message": "Adjustment stok berhasil dibuat"
}
```

#### 2.2 Product Move History Report (Includes Adjustments)
**Endpoint:** `POST /inventory/product-move-history-report`  
**Auth Required:** ✅ Yes

**Request Body:**
```json
{
  "start_date": "2025-01-01",
  "end_date": "2025-01-31"
}
```

**Response:**
```json
{
  "status": "success",
  "data": {
    "total_items": 150,
    "items": [
      {
        "product_id": "550e8400-e29b-41d4-a716-446655440000",
        "product_name": "Oli Shell 1L",
        "type": "adjustment",
        "quantity": -5,
        "timestamp": "2025-01-18T10:30:00",
        "performed_by": "admin_user",
        "notes": "Rusak saat pengecekan",
        "price": 150000,
        "hpp": 100000,
        "customer_name": null,
        "vendor_name": null,
        "nopol": null
      }
    ]
  }
}
```

**Field Definitions untuk Adjustment:**
- `type` (string): "adjustment" untuk perubahan stok manual
- `quantity` (decimal): Jumlah adjustment (positif = tambah, negatif = kurang)
- `notes` (string): Alasan/keterangan adjustment
- `performed_by` (string): User yang melakukan
- `timestamp` (datetime): Waktu adjustment dilakukan

### Implementasi Backend

**File:** [routes/routes_product.py](routes/routes_product.py)  
**Route:** `POST /products/inventory/adjustment`

```python
@router.post("/inventory/adjustment", dependencies=[Depends(jwt_required)])
def adjust_product_inventory(
    request_data: dict,
    db: Session = Depends(get_db),
    current_user: dict = Depends(jwt_required)
):
    try:
        product_id = request_data.get("product_id")
        adjustment_qty = request_data.get("adjustment_qty")
        reason = request_data.get("reason")
        tanggal = request_data.get("tanggal")
        
        # Validasi
        if not product_id or adjustment_qty is None:
            return error_response(message="product_id dan adjustment_qty harus diisi")
        
        # Cek product
        product = db.query(Product).filter(Product.id == product_id).first()
        if not product:
            return error_response(message="Produk tidak ditemukan")
        
        # Update inventory
        inventory = get_or_create_inventory(db, product_id)
        inventory.quantity += adjustment_qty
        inventory.updated_at = datetime.now()
        
        # Create history record
        history = ProductMovedHistory(
            product_id=product_id,
            type="adjustment",
            quantity=adjustment_qty,
            notes=reason or "Manual adjustment",
            performed_by=current_user.get("username"),
            created_at=datetime.fromisoformat(tanggal) if tanggal else datetime.now()
        )
        
        db.add(history)
        db.commit()
        
        return success_response(
            data={
                "product_id": str(product_id),
                "adjustment_qty": adjustment_qty,
                "reason": reason,
                "timestamp": history.created_at.isoformat()
            },
            message="Adjustment stok berhasil dibuat"
        )
    except Exception as e:
        db.rollback()
        return error_response(message=f"Gagal membuat adjustment: {str(e)}")
```

**File:** [services/services_inventory.py](services/services_inventory.py)  
**Function:** `generate_product_move_history_report()`

Sudah support untuk filter type="adjustment", menampilkan:
- Product name dan ID
- Adjustment quantity (positif/negatif)
- Tanggal dan waktu
- Alasan/notes
- User yang melakukan

### Usage Example (Frontend)
```javascript
// 1. Ambil daftar adjustment
const response = await fetch('/inventory/product-move-history-report', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    start_date: '2025-01-01',
    end_date: '2025-01-31'
  })
});

const { data } = await response.json();

// 2. Filter hanya adjustment type
const adjustments = data.items.filter(item => item.type === 'adjustment');

// 3. Display di table
adjustments.forEach(adj => {
  console.log(`${adj.product_name}: ${adj.quantity} unit (${adj.notes})`);
});
```

---

## ❌ 3. Daftar Kehilangan Barang (Lost Goods List)

### Tujuan
Menampilkan riwayat semua barang yang hilang/rusak, termasuk:
- Tanggal kehilangan
- Produk yang hilang
- Jumlah yang hilang
- Alasan kehilangan
- Nilai kerugian

### Endpoint yang Sudah Ada

#### 3.1 Create Product Loss (Kehilangan Barang)
**Endpoint:** `POST /inventory/move/loss`  
**Auth Required:** ✅ Yes

**Request Body:**
```json
{
  "product_id": "550e8400-e29b-41d4-a716-446655440000",
  "kuantitas": 2,
  "reason": "Rusak karena banjir",
  "tanggal": "2025-01-18"
}
```

**Response:**
```json
{
  "status": "success",
  "data": {
    "product_id": "550e8400-e29b-41d4-a716-446655440000",
    "quantity": -2,
    "reason": "Rusak karena banjir",
    "timestamp": "2025-01-18T10:30:00",
    "value_loss": 200000
  },
  "message": "Pencatatan kehilangan barang berhasil"
}
```

#### 3.2 Lost Goods Journal Entry (Accounting)
**Function:** `create_lost_goods_journal_entry()`

Mencatat kehilangan barang dengan journal entry:
```
Dr Beban Kehilangan Barang (Account 6004)      Rp 200,000
   Cr Inventory (Account 1-2001)               Rp 200,000
```

### Implementasi Backend

**File:** [routes/routes_inventory.py](routes/routes_inventory.py)  
**Route:** `POST /inventory/move/loss`

```python
@router.post("/move/loss", dependencies=[Depends(jwt_required)])
def create_product_loss(
    request_data: dict,
    db: Session = Depends(get_db),
    current_user: dict = Depends(jwt_required)
):
    try:
        product_id = request_data.get("product_id")
        kuantitas = request_data.get("kuantitas")
        reason = request_data.get("reason")
        tanggal = request_data.get("tanggal")
        
        # Validasi
        if not product_id or not kuantitas:
            return error_response(message="product_id dan kuantitas harus diisi")
        
        # Cek product
        product = db.query(Product).filter(Product.id == product_id).first()
        if not product:
            return error_response(message="Produk tidak ditemukan")
        
        # Create loss history (negative quantity)
        history = createProductMoveHistoryNewLoss(
            db=db,
            data={
                "product_id": product_id,
                "kuantitas": kuantitas,  # Will be negative
                "reason": reason or "Lost/damaged",
                "tanggal": tanggal
            },
            username=current_user.get("username")
        )
        
        # Calculate loss value
        loss_value = kuantitas * (product.cost or 0)
        
        return success_response(
            data={
                "product_id": str(product_id),
                "quantity": -kuantitas,
                "reason": reason,
                "value_loss": loss_value,
                "timestamp": history.created_at.isoformat()
            },
            message="Pencatatan kehilangan barang berhasil"
        )
    except Exception as e:
        db.rollback()
        return error_response(message=f"Gagal mencatat kehilangan: {str(e)}")
```

**File:** [services/services_accounting.py](services/services_accounting.py)  
**Function:** `create_lost_goods_journal_entry()`

```python
def create_lost_goods_journal_entry(db: Session, data_entry: LostGoodsJournalEntry) -> dict:
    """
    Create a lost goods journal entry.
    Records inventory loss as expense.
    """
    try:
        if data_entry.quantity <= 0:
            raise ValueError("Quantity must be positive for lost goods entry")
        
        # Get account codes
        loss_account = db.query(Account).filter(
            Account.code == "6004"  # Beban Kehilangan Barang
        ).first()
        inventory_account = db.query(Account).filter(
            Account.code == "1-2001"  # Inventory
        ).first()
        
        if not loss_account or not inventory_account:
            raise ValueError("Account codes 6004 or 1-2001 not found")
        
        total_loss = data_entry.quantity * data_entry.cost
        
        # Create journal entries
        # Dr Beban Kehilangan Barang
        entry1 = JournalEntry(
            account_id=loss_account.id,
            debit=total_loss,
            credit=Decimal("0.00"),
            description=f"Kehilangan: {data_entry.description}",
            date=data_entry.date,
            ref_table="product_moved_history"
        )
        
        # Cr Inventory
        entry2 = JournalEntry(
            account_id=inventory_account.id,
            debit=Decimal("0.00"),
            credit=total_loss,
            description=f"Kehilangan: {data_entry.description}",
            date=data_entry.date,
            ref_table="product_moved_history"
        )
        
        db.add(entry1)
        db.add(entry2)
        db.commit()
        
        return {
            "loss_value": total_loss,
            "journal_entry_ids": [str(entry1.id), str(entry2.id)]
        }
    except Exception as e:
        db.rollback()
        raise Exception(f"Failed to create lost goods entry: {str(e)}")
```

### Product Move History - Loss Items
**Endpoint:** `POST /inventory/product-move-history-report`  

Daftar kehilangan barang dapat diambil dari report ini dengan filter:
```json
{
  "start_date": "2025-01-01",
  "end_date": "2025-01-31"
}
```

Response includes items dengan `type: "loss"`:
```json
{
  "product_id": "550e8400-e29b-41d4-a716-446655440000",
  "product_name": "Oli Shell 1L",
  "type": "loss",
  "quantity": -2,
  "timestamp": "2025-01-18T10:30:00",
  "performed_by": "admin_user",
  "notes": "Rusak karena banjir",
  "price": 150000,
  "hpp": 100000
}
```

### Usage Example (Frontend)
```javascript
// 1. Ambil daftar kehilangan barang
const response = await fetch('/inventory/product-move-history-report', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    start_date: '2025-01-01',
    end_date: '2025-01-31'
  })
});

const { data } = await response.json();

// 2. Filter hanya loss/kehilangan items
const lostGoods = data.items.filter(item => item.type === 'loss');

// 3. Calculate total loss value
const totalLoss = lostGoods.reduce((sum, item) => {
  return sum + (Math.abs(item.quantity) * item.hpp);
}, 0);

// 4. Display
console.log(`Total kerugian barang hilang: Rp ${totalLoss}`);
lostGoods.forEach(item => {
  const lossValue = Math.abs(item.quantity) * item.hpp;
  console.log(`${item.product_name}: ${Math.abs(item.quantity)} unit (Rp ${lossValue})`);
});
```

---

## 📊 Summary Implementasi Backend

| Fitur | Endpoint | Method | Status | Notes |
|-------|----------|--------|--------|-------|
| **Daftar Penerimaan Konsinyasi** | `/products/inventory/all/consignment` | GET | ✅ Complete | List semua konsinyasi products |
| **Buat Konsinyasi** | `/products/create/new` | POST | ✅ Complete | Dengan field `is_consignment`, `consignment_commission` |
| **Daftar Adjustmen** | `/inventory/product-move-history-report` | POST | ✅ Complete | Filter type="adjustment" |
| **Buat Adjustment** | `/products/inventory/adjustment` | POST | ✅ Complete | Create stok adjustment record |
| **Daftar Kehilangan** | `/inventory/product-move-history-report` | POST | ✅ Complete | Filter type="loss" |
| **Buat Kehilangan** | `/inventory/move/loss` | POST | ✅ Complete | Record kehilangan barang |
| **Jurnal Kehilangan** | (Internal) | - | ✅ Complete | Auto journal entry (6004 & 1-2001) |

---

## 🔧 Data Model Reference

### ProductMovedHistory Model
```python
class ProductMovedHistory(Base):
    __tablename__ = "product_moved_history"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    product_id = Column(UUID(as_uuid=True), ForeignKey('product.id'))
    type = Column(String, nullable=False)  # 'income', 'outcome', 'adjustment', 'loss'
    quantity = Column(Numeric(12,2), nullable=False)
    notes = Column(String, nullable=True)
    performed_by = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    product = relationship("Product")
```

### Product Model - Consignment Fields
```python
class Product(Base):
    __tablename__ = "product"
    
    # ... existing fields ...
    supplier_id = Column(UUID(as_uuid=True), ForeignKey('supplier.id'), nullable=True)
    is_consignment = Column(Boolean, nullable=False, default=False)
    consignment_commission = Column(Numeric(10,2), nullable=True)
    
    supplier = relationship('Supplier', back_populates='products')
```

---

## 📝 Frontend Integration Notes

### 1. Konsinyasi Receipt List View
- Show all consignment products from `/products/inventory/all/consignment`
- Display: Produk, Supplier, Harga, Komisi, Stok
- Support search/filter by supplier name

### 2. Adjustment List View
- Get from `/inventory/product-move-history-report` with type="adjustment" filter
- Display: Tanggal, Produk, Jumlah, Alasan, User
- Support date range filtering
- Show summary: Total adjusted items

### 3. Lost Goods List View
- Get from `/inventory/product-move-history-report` with type="loss" filter
- Display: Tanggal, Produk, Jumlah, Alasan, Nilai Kerugian
- Support date range filtering
- Show summary: Total loss value in Rp
- Link to related journal entries

### 4. Create Forms
All create operations require JWT authentication:
- Konsinyasi: Included in product creation form
- Adjustment: Quick form with product selector
- Lost Goods: Quick form with product selector and cost calculation

---

## 🧪 Testing Checklist

- [ ] List semua konsinyasi products
- [ ] Filter konsinyasi by supplier
- [ ] Create konsinyasi product dengan commission
- [ ] Verify stok konsinyasi tracked correctly
- [ ] Create adjustment stok (increase & decrease)
- [ ] Verify adjustment in move history
- [ ] Create loss record (kehilangan barang)
- [ ] Verify loss in move history
- [ ] Verify loss creates journal entry
- [ ] Calculate total loss value correctly
- [ ] Date range filtering works
- [ ] User attribution recorded correctly

---

## 📚 Related Documentation

- [Consignment Implementation Summary](CONSIGNMENT_IMPLEMENTATION_SUMMARY.md)
- [Product Move History Report](API_DOCUMENTATION_COMPLETE.md#82-product-move-history-report)
- [Inventory Adjustment](API_DOCUMENTATION_COMPLETE.md#720-inventory-adjustment)
- [Lost Goods Journal Entry](API_DOCUMENTATION_COMPLETE.md)

---

**Status:** ✅ Backend Implementation Complete  
**Last Updated:** 2026-02-01  
**Ready for:** Frontend Development & Integration
