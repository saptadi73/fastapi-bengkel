# Auto-Import Routes System

## 🎯 Tujuan

Sistem ini dibuat agar **tidak perlu update `main.py` setiap kali menambah atau mengubah routes**. Semua routes akan di-import secara otomatis!

## ✨ Keuntungan

### ❌ Sebelum (Manual):
```python
# main.py - Harus update setiap kali ada route baru
from routes import routes_customer, routes_auth, routes_product, routes_workorder, ...

app.include_router(routes_auth.router)
app.include_router(routes_booking.router)
app.include_router(routes_workorder.router)
# ... 13 baris lagi untuk setiap router
```

### ✅ Sesudah (Otomatis):
```python
# main.py - Tidak perlu update lagi!
from routes import all_routers

for router in all_routers:
    app.include_router(router)
```

## 🔧 Cara Kerja

### 1. **Auto-Discovery di `routes/__init__.py`**

```python
# Sistem akan otomatis scan semua file routes_*.py
for file in routes_dir.glob("routes_*.py"):
    module = importlib.import_module(f"routes.{module_name}")
    if hasattr(module, 'router'):
        all_routers.append(module.router)
```

### 2. **Naming Convention**

File routes **HARUS** mengikuti pattern:
- ✅ `routes_*.py` (contoh: `routes_product.py`, `routes_customer.py`)
- ✅ Harus memiliki variable `router` di dalamnya
- ❌ File lain akan diabaikan (contoh: `helper.py`, `utils.py`)

### 3. **Import di main.py**

```python
from routes import all_routers

for router in all_routers:
    app.include_router(router)
```

## 📝 Cara Menambah Route Baru

### Langkah 1: Buat File Route Baru

Buat file dengan nama `routes_namafitur.py` di folder `routes/`:

```python
# routes/routes_namafitur.py
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from models.database import SessionLocal

router = APIRouter(prefix="/namafitur", tags=["Nama Fitur"])

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.get("/")
def get_all_items(db: Session = Depends(get_db)):
    return {"message": "List of items"}

@router.post("/create")
def create_item(db: Session = Depends(get_db)):
    return {"message": "Item created"}
```

### Langkah 2: Restart Server

```bash
# Restart FastAPI server
# Ctrl+C untuk stop, lalu jalankan lagi
uvicorn main:app --reload
```

### Langkah 3: Selesai! ✅

Route baru otomatis tersedia tanpa perlu edit `main.py`!

## 🔍 Verifikasi

Saat server start, Anda akan melihat output:

```
✓ Loaded router from: routes_accounting
✓ Loaded router from: routes_attendance
✓ Loaded router from: routes_auth
✓ Loaded router from: routes_booking
✓ Loaded router from: routes_customer
✓ Loaded router from: routes_expenses
✓ Loaded router from: routes_inventory
✓ Loaded router from: routes_karyawan
✓ Loaded router from: routes_packet_order
✓ Loaded router from: routes_product
✓ Loaded router from: routes_purchase_order
✓ Loaded router from: routes_supplier
✓ Loaded router from: routes_workorder

📦 Total routers loaded: 13
```

## ⚠️ Troubleshooting

### Problem: Router tidak ter-load

**Penyebab 1:** Nama file tidak sesuai pattern
```python
❌ product_routes.py  # Salah
❌ routes.py          # Salah
✅ routes_product.py  # Benar
```

**Penyebab 2:** Tidak ada variable `router`
```python
❌ app = APIRouter()  # Salah nama variable
✅ router = APIRouter()  # Benar
```

**Penyebab 3:** Error di dalam file route
- Cek console output untuk error message
- Fix error di file route tersebut

### Problem: Duplicate routes

Jika ada error "Route already exists":
- Pastikan tidak ada 2 file dengan endpoint yang sama
- Gunakan prefix yang berbeda untuk setiap router

## 📊 Struktur File

```
routes/
├── __init__.py              ← Auto-import logic
├── routes_accounting.py     ← Auto-loaded
├── routes_attendance.py     ← Auto-loaded
├── routes_auth.py           ← Auto-loaded
├── routes_booking.py        ← Auto-loaded
├── routes_customer.py       ← Auto-loaded
├── routes_expenses.py       ← Auto-loaded
├── routes_inventory.py      ← Auto-loaded
├── routes_karyawan.py       ← Auto-loaded
├── routes_packet_order.py   ← Auto-loaded
├── routes_product.py        ← Auto-loaded
├── routes_purchase_order.py ← Auto-loaded
├── routes_supplier.py       ← Auto-loaded
├── routes_workorder.py      ← Auto-loaded
└── routes_NAMAFITUR.py      ← Tambah file baru di sini!
```

## 🎨 Template Route Baru

Copy template ini untuk membuat route baru:

```python
"""
Route untuk [Nama Fitur]
Deskripsi singkat tentang fitur ini
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from models.database import SessionLocal
from schemas.service_[nama] import Create[Nama], [Nama]Response
from services.services_[nama] import create_[nama], get_all_[nama]
from supports.utils_json_response import success_response, error_response
from middleware.jwt_required import jwt_required

router = APIRouter(prefix="/[nama]", tags=["[Nama]"])

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.get("/all")
def list_all(db: Session = Depends(get_db)):
    """Get all items"""
    try:
        result = get_all_[nama](db)
        return success_response(data=result)
    except Exception as e:
        return error_response(message=str(e))
    finally:
        db.close()

@router.post("/create", dependencies=[Depends(jwt_required)])
def create(data: Create[Nama], db: Session = Depends(get_db)):
    """Create new item"""
    try:
        result = create_[nama](db, data)
        return success_response(data=result)
    except Exception as e:
        return error_response(message=str(e))
    finally:
        db.close()

@router.get("/{item_id}")
def get_by_id(item_id: str, db: Session = Depends(get_db)):
    """Get item by ID"""
    try:
        result = get_[nama]_by_id(db, item_id)
        if not result:
            raise HTTPException(status_code=404, detail="Item not found")
        return success_response(data=result)
    except Exception as e:
        return error_response(message=str(e))
    finally:
        db.close()
```

## 🚀 Keuntungan Sistem Ini

1. **Maintainability** ✅
   - Tidak perlu edit `main.py` setiap kali ada route baru
   - Lebih mudah maintain dan scale

2. **Clean Code** ✅
   - `main.py` lebih ringkas dan bersih
   - Separation of concerns yang lebih baik

3. **Developer Friendly** ✅
   - Developer baru tinggal tambah file di folder `routes/`
   - Tidak perlu tahu struktur `main.py`

4. **Error Handling** ✅
   - Jika ada error di satu route, route lain tetap bisa load
   - Error message yang jelas di console

5. **Scalability** ✅
   - Mudah menambah puluhan route tanpa bloat `main.py`
   - Struktur yang konsisten

## 📚 Best Practices

1. **Naming Convention**
   - Gunakan `routes_[nama_fitur].py`
   - Nama file lowercase dengan underscore
   - Contoh: `routes_user_management.py`

2. **Router Configuration**
   - Selalu gunakan `prefix` untuk grouping
   - Gunakan `tags` untuk dokumentasi API
   - Contoh: `router = APIRouter(prefix="/users", tags=["User Management"])`

3. **Documentation**
   - Tambahkan docstring di setiap endpoint
   - Gunakan type hints untuk parameter
   - Contoh:
     ```python
     @router.get("/{user_id}")
     def get_user(user_id: str, db: Session = Depends(get_db)):
         """Get user by ID"""
         ...
     ```

4. **Error Handling**
   - Gunakan try-except di setiap endpoint
   - Return consistent error response
   - Close database session di finally block

## 🔄 Migration dari Sistem Lama

Jika Anda punya kode lama dengan manual import:

### Before:
```python
from routes import routes_customer, routes_auth
app.include_router(routes_auth.router)
app.include_router(routes_customer.router)
```

### After:
```python
from routes import all_routers
for router in all_routers:
    app.include_router(router)
```

**Tidak ada perubahan di file routes!** Semua file `routes_*.py` tetap sama.

## ✅ Checklist

Saat menambah route baru, pastikan:

- [ ] File bernama `routes_*.py`
- [ ] Ada variable `router = APIRouter(...)`
- [ ] Router memiliki `prefix` dan `tags`
- [ ] Semua endpoint memiliki docstring
- [ ] Error handling sudah ada
- [ ] Database session di-close dengan benar
- [ ] Test endpoint dengan Postman/curl

## 🎉 Kesimpulan

Dengan sistem auto-import ini:
- ✅ **Tidak perlu edit `main.py` lagi**
- ✅ **Tambah route baru lebih cepat**
- ✅ **Kode lebih bersih dan maintainable**
- ✅ **Developer friendly**

Selamat coding! 🚀
