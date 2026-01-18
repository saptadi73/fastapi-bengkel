# Service (Jasa Layanan Bengkel) API Documentation

## 📋 Overview

Dokumentasi lengkap untuk API pengelolaan **Service/Jasa Layanan Bengkel**. Service adalah layanan pekerjaan yang ditawarkan bengkel, seperti ganti oli, servis rem, cat, dll.

## 🔗 API Endpoints

### Base URL
```
http://localhost:8000/products
```

---

## 1. Create Service (Buat Jasa Baru)

### Endpoint
```
POST /products/service/create/new
```

### Authentication
- ✅ **Diperlukan**: JWT Token (Header: `Authorization: Bearer <token>`)

### Request Body
```json
{
  "name": "Ganti Oli",
  "description": "Layanan penggantian oli mesin standar",
  "price": 150000,
  "cost": 50000
}
```

### Schema: `CreateService`
| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `name` | string | ✅ Yes | Nama layanan jasa |
| `description` | string | ❌ No | Deskripsi detail layanan |
| `price` | decimal | ❌ No | Harga jual layanan kepada customer |
| `cost` | decimal | ❌ No | Biaya/HPP (Harga Pokok Penjualan) layanan |

### Response (Success)
```json
{
  "success": true,
  "data": {
    "id": "550e8400-e29b-41d4-a716-446655440000",
    "name": "Ganti Oli",
    "description": "Layanan penggantian oli mesin standar",
    "price": 150000,
    "cost": 50000
  },
  "message": null
}
```

### Response (Error)
```json
{
  "success": false,
  "data": null,
  "message": "Failed to create service"
}
```

### cURL Example
```bash
curl -X POST "http://localhost:8000/products/service/create/new" \
  -H "Authorization: Bearer <YOUR_JWT_TOKEN>" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Ganti Oli",
    "description": "Layanan penggantian oli mesin standar",
    "price": 150000,
    "cost": 50000
  }'
```

---

## 2. Get All Services (Daftar Semua Jasa)

### Endpoint
```
GET /products/service/all
```

### Authentication
- ❌ **Tidak Diperlukan** (Public endpoint)

### Query Parameters
- Tidak ada

### Response (Success)
```json
{
  "success": true,
  "data": [
    {
      "id": "550e8400-e29b-41d4-a716-446655440000",
      "name": "Ganti Oli",
      "description": "Layanan penggantian oli mesin standar",
      "price": 150000,
      "cost": 50000
    },
    {
      "id": "550e8400-e29b-41d4-a716-446655440001",
      "name": "Servis Rem",
      "description": "Pemeriksaan dan servis sistem rem",
      "price": 200000,
      "cost": 80000
    },
    {
      "id": "550e8400-e29b-41d4-a716-446655440002",
      "name": "Ganti Filter Udara",
      "description": null,
      "price": 75000,
      "cost": 25000
    }
  ],
  "message": null
}
```

### Response (Empty List)
```json
{
  "success": true,
  "data": [],
  "message": null
}
```

### cURL Example
```bash
curl -X GET "http://localhost:8000/products/service/all"
```

### Python Example
```python
import requests

response = requests.get("http://localhost:8000/products/service/all")
services = response.json()["data"]

for service in services:
    print(f"{service['name']}: Rp {service['price']:,}")
```

---

## 3. Get Service by ID (Detail Jasa)

### Endpoint
```
GET /products/service/{service_id}
```

### Authentication
- ❌ **Tidak Diperlukan** (Public endpoint)

### Path Parameters
| Parameter | Type | Description |
|-----------|------|-------------|
| `service_id` | UUID string | ID service yang ingin diambil |

### Response (Success)
```json
{
  "success": true,
  "data": {
    "id": "550e8400-e29b-41d4-a716-446655440000",
    "name": "Ganti Oli",
    "description": "Layanan penggantian oli mesin standar",
    "price": 150000,
    "cost": 50000
  },
  "message": null
}
```

### Response (Not Found)
```json
{
  "success": false,
  "data": null,
  "message": "Service not found"
}
```

### cURL Example
```bash
curl -X GET "http://localhost:8000/products/service/550e8400-e29b-41d4-a716-446655440000"
```

---

## ⚠️ Update & Delete Service

### Status Saat Ini
Operasi **UPDATE** dan **DELETE** untuk Service **BELUM TERSEDIA** (tidak ada endpoint).

### Workaround Saat Ini
Jika perlu update atau delete service:
1. Hubungi database administrator
2. Atau gunakan database client langsung (DBeaver, pgAdmin, etc.)

### Rencana Ke Depan
- [ ] Tambahkan endpoint `PUT /products/service/{service_id}` untuk update
- [ ] Tambahkan endpoint `DELETE /products/service/{service_id}` untuk delete
- [ ] Tambahkan soft-delete mechanism untuk data integrity

---

## 💡 Use Cases

### Scenario 1: Aplikasi Frontend Menampilkan Daftar Layanan

**Kode Frontend (JavaScript/React):**
```javascript
// Ambil daftar semua service
const response = await fetch('http://localhost:8000/products/service/all');
const result = await response.json();
const services = result.data;

// Tampilkan di dropdown atau list
services.forEach(service => {
  console.log(`${service.name}: Rp ${service.price.toLocaleString('id-ID')}`);
});
```

### Scenario 2: Tambah Service Baru (Admin Panel)

**Kode Frontend (JavaScript):**
```javascript
const token = localStorage.getItem('jwt_token');

const newService = {
  name: "Servis AC",
  description: "Pembersihan dan servis sistem AC mobil",
  price: 250000,
  cost: 100000
};

const response = await fetch('http://localhost:8000/products/service/create/new', {
  method: 'POST',
  headers: {
    'Authorization': `Bearer ${token}`,
    'Content-Type': 'application/json'
  },
  body: JSON.stringify(newService)
});

const result = await response.json();
if (result.success) {
  console.log('Service berhasil ditambahkan:', result.data);
} else {
  console.error('Gagal menambahkan service:', result.message);
}
```

### Scenario 3: Ambil Detail Service Spesifik

**Kode Python:**
```python
import requests
from decimal import Decimal

service_id = "550e8400-e29b-41d4-a716-446655440000"
response = requests.get(f"http://localhost:8000/products/service/{service_id}")

if response.status_code == 200:
    service = response.json()["data"]
    print(f"Nama: {service['name']}")
    print(f"Harga: Rp {int(float(service['price'])):,}")
    print(f"HPP: Rp {int(float(service['cost'])):,}")
    print(f"Margin: Rp {int(float(service['price']) - float(service['cost'])):,}")
else:
    print("Service tidak ditemukan")
```

---

## 📊 Integrasi dengan Work Order

Service digunakan dalam Work Order (Pesanan Kerja) ketika mechanic menambahkan jasa layanan:

### Contoh Struktur Work Order dengan Service
```json
{
  "id": "wo-001",
  "no_wo": "WO-202601-0001",
  "customer_id": "cust-001",
  "status": "selesai",
  "service_ordered": [
    {
      "id": "so-001",
      "workorder_id": "wo-001",
      "service_id": "550e8400-e29b-41d4-a716-446655440000",
      "service_name": "Ganti Oli",
      "quantity": 1,
      "price": 150000,
      "subtotal": 150000,
      "discount": 0
    },
    {
      "id": "so-002",
      "workorder_id": "wo-001",
      "service_id": "550e8400-e29b-41d4-a716-446655440001",
      "service_name": "Servis Rem",
      "quantity": 1,
      "price": 200000,
      "subtotal": 200000,
      "discount": 0
    }
  ]
}
```

---

## 🔍 Model Database

### Table: `service`
```sql
CREATE TABLE service (
  id VARCHAR(36) PRIMARY KEY,
  name VARCHAR(255) NOT NULL,
  description TEXT,
  price NUMERIC(15,2),
  cost NUMERIC(15,2),
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);
```

### Relasi dengan Service Ordered
```sql
CREATE TABLE service_ordered (
  id VARCHAR(36) PRIMARY KEY,
  workorder_id VARCHAR(36) NOT NULL,
  service_id VARCHAR(36) NOT NULL,
  quantity FLOAT NOT NULL,
  price NUMERIC(15,2),
  subtotal NUMERIC(15,2),
  discount NUMERIC(15,2) DEFAULT 0,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY (workorder_id) REFERENCES workorder(id),
  FOREIGN KEY (service_id) REFERENCES service(id)
);
```

---

## 🛠️ Technical Details

### File Terkait:
- **Routes**: `routes/routes_product.py` (Lines 69-110)
- **Services**: `services/services_product.py` (Lines 81-102)
- **Schemas**: `schemas/service_product.py` (Lines 69-86)
- **Models**: `models/workorder.py` (Service model)

### Fungsi-Fungsi:
```python
# Create
createServicenya(db: Session, service_data: CreateService) → dict

# Read All
get_all_services(db: Session) → list[dict]

# Read By ID
get_service_by_id(db: Session, service_id: str) → dict
```

---

## ❌ Known Limitations

| Fitur | Status | Note |
|-------|--------|------|
| Create Service | ✅ Available | Endpoint: POST /service/create/new |
| Get All Services | ✅ Available | Endpoint: GET /service/all |
| Get By ID | ✅ Available | Endpoint: GET /service/{id} |
| Update Service | ❌ Not Available | Akan ditambahkan di fase berikutnya |
| Delete Service | ❌ Not Available | Akan ditambahkan di fase berikutnya |
| Bulk Import | ❌ Not Available | Untuk CSV/Excel import |
| Soft Delete | ❌ Not Available | Untuk maintain data integrity |

---

## 🔐 Security Considerations

1. **Create Service** memerlukan JWT authentication
2. **Get All/By ID** adalah public endpoint (no auth required)
3. Untuk production, pertimbangkan:
   - Restrict Get All ke authorized users only
   - Implementasi role-based access control (admin only)
   - Add audit logging untuk create/update/delete
   - Implement soft delete untuk data integrity

---

## 📝 Best Practices

### Naming Convention
- Gunakan nama deskriptif: "Ganti Oli" bukan "Oli"
- Format: Action + Object (e.g., "Ganti Oli", "Servis Rem", "Cat Ulang")

### Pricing Strategy
- Price: Harga jual ke customer
- Cost: HPP untuk mencatat profit margin
- Margin = Price - Cost

### Common Service Types
```json
[
  {"name": "Ganti Oli", "price": 150000, "cost": 50000},
  {"name": "Servis Rem", "price": 200000, "cost": 80000},
  {"name": "Ganti Filter Udara", "price": 75000, "cost": 25000},
  {"name": "Cat Ulang", "price": 500000, "cost": 200000},
  {"name": "Servis AC", "price": 250000, "cost": 100000},
  {"name": "Perawatan Rutin", "price": 300000, "cost": 100000}
]
```

---

## 🔄 Changelog

**Januari 2026**:
- ✅ Dokumentasi lengkap untuk Service API
- ✅ Contoh request/response
- ✅ Use cases dan integrasi dengan Work Order
- ❌ Update/Delete endpoints belum tersedia

---

## ❓ FAQ

**Q: Bagaimana menambah service baru?**
A: Gunakan endpoint `POST /products/service/create/new` dengan JWT token.

**Q: Bisakah update service yang sudah ada?**
A: Tidak tersedia endpoint update. Hubungi database admin atau gunakan database client.

**Q: Apakah service bisa dihapus?**
A: Tidak tersedia endpoint delete. Data existing tidak bisa dihapus untuk maintain referential integrity.

**Q: Berapa maksimal jumlah service?**
A: Tidak ada limit, tapi performa bisa menurun jika > 10,000 services. Pertimbangkan pagination.

**Q: Bagaimana jika harga service berubah?**
A: Saat ini tidak ada versioning. Update langsung di database atau tunggu fitur update di release berikutnya.

---

## 📞 Support

Jika ada pertanyaan atau bug report:
1. Check dokumentasi ini terlebih dahulu
2. Lihat contoh di bagian "Use Cases"
3. Cek file `/services/services_product.py` untuk logic detail
4. Contact backend team untuk feature request

