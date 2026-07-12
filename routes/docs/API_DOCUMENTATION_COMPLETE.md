# API Documentation - FastAPI Bengkel

**Base URL:** `http://localhost:8000`  
**Production URL:** `https://carspeed.gagakrimang.web.id`

**Version:** 1.0.1  
**Last Updated:** July 12, 2026

## 📋 Table of Contents

1. [Authentication](#1-authentication)
2. [User Management](#2-user-management)
3. [Role Management](#3-role-management)
4. [Role-User Management](#4-role-user-management)
5. [Customer Management](#5-customer-management)
6. [Work Orders](#6-work-orders)
7. [Products & Services](#7-products--services)
8. [Inventory Management](#8-inventory-management)
   - [8.6 Consignment Receipt Management](#86-consignment-receipt-management)
   - [8.7 Inventory Adjustment Management](#87-inventory-adjustment-management)
   - [8.8 Inventory Loss Management](#88-inventory-loss-management)
9. [Purchase Orders](#9-purchase-orders)
10. [Expenses](#10-expenses)
11. [Booking](#11-booking)
12. [Supplier](#12-supplier)
13. [Karyawan (Employee)](#13-karyawan-employee)
14. [Attendance](#14-attendance)
15. [Dashboard](#15-dashboard)
16. [Accounting & Reports](#16-accounting--reports)
17. [WhatsApp Integration](#17-whatsapp-integration)
18. [WhatsApp Reports](#18-whatsapp-reports)
19. [Manual WhatsApp](#19-manual-whatsapp)
20. [Scheduler](#20-scheduler)
21. [Packet Orders](#21-packet-orders)

---

## 🔐 Authentication

All protected endpoints require JWT token in the Authorization header:
```
Authorization: Bearer <your_jwt_token>
```

### Common Response Format

**Success Response:**
```json
{
  "status": "success",
  "message": "Operation successful message",
  "data": { /* response data */ }
}
```

**Error Response:**
```json
{
  "status": "error",
  "message": "Error message description",
  "data": null
}
```

---

## 1. Authentication

### 1.1 Login

**Endpoint:** `POST /auth/login`  
**Auth Required:** ❌ No

**Request Body:**
```json
{
  "username": "admin",
  "password": "password123"
}
```

**Response:**
```json
{
  "status": "success",
  "message": "Login successful",
  "data": {
    "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "token_type": "bearer",
    "user": {
      "id": "uuid-string",
      "username": "admin",
      "email": "admin@example.com",
      "is_active": true,
      "roles": [
        {
          "id": "uuid-string",
          "name": "admin"
        }
      ]
    }
  }
}
```

### 1.2 Register

**Endpoint:** `POST /auth/register`  
**Auth Required:** ❌ No

**Request Body:**
```json
{
  "username": "newuser",
  "email": "user@example.com",
  "password": "password123"
}
```

**Response:**
```json
{
  "status": "success",
  "message": "User registered successfully",
  "data": {
    "id": "uuid-string",
    "username": "newuser",
    "email": "user@example.com",
    "is_active": true
  }
}
```

---

## 2. User Management

### 2.1 Get All Users

**Endpoint:** `GET /users/`  
**Auth Required:** ❌ No

**Response:**
```json
{
  "status": "success",
  "message": "All users retrieved successfully",
  "data": [
    {
      "id": "uuid-string",
      "username": "user1",
      "email": "user1@example.com",
      "is_active": true
    }
  ]
}
```

### 2.2 Get User by ID

**Endpoint:** `GET /users/{user_id}`  
**Auth Required:** ❌ No

**Response:**
```json
{
  "status": "success",
  "message": "User retrieved successfully",
  "data": {
    "id": "uuid-string",
    "username": "user1",
    "email": "user1@example.com",
    "is_active": true
  }
}
```

---

## 3. Role Management

### 3.1 Get All Roles

**Endpoint:** `GET /roles/`  
**Auth Required:** ❌ No

**Response:**
```json
{
  "status": "success",
  "message": "Roles retrieved successfully",
  "data": [
    {
      "id": "uuid-string",
      "name": "admin",
      "description": "Administrator role"
    }
  ]
}
```

### 3.2 Get Role by ID

**Endpoint:** `GET /roles/{role_id}`  
**Auth Required:** ❌ No

### 3.3 Create Role

**Endpoint:** `POST /roles/`  
**Auth Required:** ❌ No

**Request Body:**
```json
{
  "name": "mechanic",
  "description": "Mechanic role"
}
```

### 3.4 Update Role

**Endpoint:** `PUT /roles/{role_id}`  
**Auth Required:** ❌ No

**Request Body:**
```json
{
  "name": "senior_mechanic",
  "description": "Senior mechanic role"
}
```

### 3.5 Delete Role

**Endpoint:** `DELETE /roles/{role_id}`  
**Auth Required:** ❌ No

---

## 4. Role-User Management

### 4.1 Assign Role to User

**Endpoint:** `POST /role-user/assign`  
**Auth Required:** ❌ No

**Request Body:**
```json
{
  "user_id": "uuid-string",
  "role_id": "uuid-string"
}
```

### 4.2 Remove Role from User

**Endpoint:** `DELETE /role-user/remove`  
**Auth Required:** ❌ No

**Query Parameters:**
- `user_id` (string): User UUID
- `role_id` (string): Role UUID

### 4.3 Get User Roles

**Endpoint:** `GET /role-user/user/{user_id}/roles`  
**Auth Required:** ❌ No

### 4.4 Get Users by Role

**Endpoint:** `GET /role-user/role/{role_id}/users`  
**Auth Required:** ❌ No

### 4.5 Update User Roles

**Endpoint:** `PUT /role-user/user/{user_id}/roles`  
**Auth Required:** ✅ Yes

**Request Body:**
```json
{
  "role_ids": ["uuid-1", "uuid-2"]
}
```

### 4.6 Get All Roles

**Endpoint:** `GET /role-user/roles`  
**Auth Required:** ❌ No

### 4.7 Get All Users with Roles

**Endpoint:** `GET /role-user/users-with-roles`  
**Auth Required:** ❌ No

**Response:**
```json
{
  "status": "success",
  "data": [
    {
      "id": "uuid-string",
      "username": "user1",
      "email": "user1@example.com",
      "roles": [
        {
          "id": "uuid-string",
          "name": "admin"
        }
      ]
    }
  ]
}
```

---

## 5. Customer Management

### 5.1 Create Customer with Vehicle

**Endpoint:** `POST /customers/with-vehicle`  
**Auth Required:** ✅ Yes

**Request Body:**
```json
{
  "nama": "John Doe",
  "alamat": "Jl. Merdeka No. 123",
  "telepon": "08123456789",
  "email": "john@example.com",
  "vehicles": [
    {
      "nopol": "B 1234 ABC",
      "merk": "Toyota",
      "tipe": "Avanza",
      "tahun": 2020,
      "warna": "Silver",
      "no_rangka": "MHKA1234567890",
      "no_mesin": "1NZ1234567"
    }
  ]
}
```

### 5.2 Get All Customers with Vehicles

**Endpoint:** `GET /customers/with-vehicles`  
**Auth Required:** ❌ No

**Response:**
```json
{
  "status": "success",
  "data": [
    {
      "id": "uuid-string",
      "nama": "John Doe",
      "alamat": "Jl. Merdeka No. 123",
      "telepon": "08123456789",
      "email": "john@example.com",
      "vehicles": [
        {
          "id": "uuid-string",
          "nopol": "B 1234 ABC",
          "merk": "Toyota",
          "tipe": "Avanza",
          "tahun": 2020,
          "warna": "Silver"
        }
      ]
    }
  ]
}
```

### 5.3 Get Customer by Vehicle ID

**Endpoint:** `GET /customers/with-vehicles/{vehicle_id}`  
**Auth Required:** ❌ No

### 5.4 Get Service History by Vehicle

**Endpoint:** `GET /customers/history/service/{vehicle_id}`  
**Auth Required:** ❌ No

**Response:**
```json
{
  "status": "success",
  "data": {
    "vehicle_id": "uuid-string",
    "nopol": "B 1234 ABC",
    "customer": {
      "id": "uuid-string",
      "nama": "John Doe"
    },
    "service_history": [
      {
        "workorder_id": "uuid-string",
        "tanggal": "2025-01-15",
        "keluhan": "Servis rutin",
        "products": [],
        "services": []
      }
    ]
  }
}
```

### 5.5 Get Customer with Vehicles by ID

**Endpoint:** `GET /customers/{customer_id}/with-vehicles`  
**Auth Required:** ❌ No

### 5.6 Create Customer Only

**Endpoint:** `POST /customers/customer-only`  
**Auth Required:** ✅ Yes

**Request Body:**
```json
{
  "nama": "Jane Doe",
  "alamat": "Jl. Sudirman No. 456",
  "telepon": "08234567890",
  "email": "jane@example.com"
}
```

### 5.7 Get All Customers

**Endpoint:** `GET /customers/all`  
**Auth Required:** ❌ No

### 5.8 Add Vehicle to Customer

**Endpoint:** `POST /customers/add-vehicle`  
**Auth Required:** ✅ Yes

**Request Body:**
```json
{
  "customer_id": "uuid-string",
  "nopol": "B 5678 XYZ",
  "merk": "Honda",
  "tipe": "Jazz",
  "tahun": 2021,
  "warna": "Red",
  "no_rangka": "MHKA9876543210",
  "no_mesin": "L15Z9876543"
}
```

### 5.9 Send Maintenance Reminder

**Endpoint:** `POST /customers/send-maintenance-reminder`  
**Auth Required:** ✅ Yes

**Description:** Send WhatsApp maintenance reminders to customers whose maintenance schedule is less than 3 days.

**Response:**
```json
{
  "status": "success",
  "data": {
    "total_customers": 10,
    "reminder_sent": 8,
    "details": [
      {
        "customer_name": "John Doe",
        "phone": "08123456789",
        "vehicle": "B 1234 ABC",
        "maintenance_date": "2025-01-20",
        "sent": true
      }
    ]
  }
}
```

---

## 6. Work Orders

### 6.1 Create New Work Order

**Endpoint:** `POST /workorders/create/new`  
**Auth Required:** ✅ Yes

**Request Body:**
```json
{
  "customer_id": "uuid-string",
  "vehicle_id": "uuid-string",
  "tanggal_masuk": "2025-01-18",
  "keluhan": "Ganti oli dan filter",
  "status_wo": "pending",
  "mekanik_id": "uuid-string",
  "km_masuk": 50000,
  "products_ordered": [
    {
      "product_id": "uuid-string",
      "kuantitas": 4,
      "harga": 50000
    }
  ],
  "services_ordered": [
    {
      "service_id": "uuid-string",
      "kuantitas": 1,
      "harga": 100000
    }
  ]
}
```

### 6.2 Get All Work Orders

**Endpoint:** `GET /workorders/all`  
**Auth Required:** ❌ No

**Response:**
```json
{
  "status": "success",
  "data": [
    {
      "id": "uuid-string",
      "customer": {
        "nama": "John Doe",
        "telepon": "08123456789"
      },
      "vehicle": {
        "nopol": "B 1234 ABC",
        "merk": "Toyota"
      },
      "tanggal_masuk": "2025-01-18",
      "keluhan": "Ganti oli",
      "status_wo": "pending",
      "total_cost": 250000,
      "products_ordered": [],
      "services_ordered": []
    }
  ]
}
```

### 6.3 Get Work Order by ID

**Endpoint:** `GET /workorders/{workorder_id}`  
**Auth Required:** ❌ No

### 6.4 Update Work Order Status Only

**Endpoint:** `POST /workorders/update-only-status`  
**Auth Required:** ✅ Yes

**Request Body:**
```json
{
  "workorder_id": "uuid-string",
  "status_pembayaran": "lunas",
  "metode_pembayaran": "cash",
  "jumlah_bayar": 250000,
  "id_akun_kas": "uuid-string"
}
```

### 6.5 Update Work Order

**Endpoint:** `POST /workorders/update/{workorder_id}`  
**Auth Required:** ✅ Yes

### 6.6 Update Work Order Keluhan (Complaint)

**Endpoint:** `POST /workorders/update/keluhan/{workorder_id}`  
**Auth Required:** ✅ Yes

**Request Body:**
```json
{
  "keluhan": "Updated complaint description"
}
```

### 6.7 Update Only Product Ordered

**Endpoint:** `POST /workorders/update/onlyproductordered/{workorder_id}`  
**Auth Required:** ✅ Yes

### 6.8 Update Only Service Ordered

**Endpoint:** `POST /workorders/update/onlyserviceordered/{workorder_id}`  
**Auth Required:** ✅ Yes

### 6.9 Update Work Order Lengkap (Complete)

**Endpoint:** `POST /workorders/update/workorderlengkap/{workorder_id}`  
**Auth Required:** ✅ Yes

### 6.10 Add Product Order

**Endpoint:** `POST /workorders/add/productorder`  
**Auth Required:** ✅ Yes

**Request Body:**
```json
{
  "workorder_id": "uuid-string",
  "product_id": "uuid-string",
  "kuantitas": 2,
  "harga": 75000
}
```

### 6.11 Update Product Order

**Endpoint:** `PUT /workorders/update/productorder/{product_ordered_id}`  
**Auth Required:** ✅ Yes

**Request Body:**
```json
{
  "kuantitas": 3,
  "harga": 80000
}
```

### 6.12 Delete Product Order

**Endpoint:** `DELETE /workorders/delete/productorder/{product_ordered_id}`  
**Auth Required:** ✅ Yes

### 6.13 Add Service Order

**Endpoint:** `POST /workorders/add/serviceorder`  
**Auth Required:** ✅ Yes

**Request Body:**
```json
{
  "workorder_id": "uuid-string",
  "service_id": "uuid-string",
  "kuantitas": 1,
  "harga": 150000
}
```

### 6.14 Update Service Order

**Endpoint:** `PUT /workorders/update/serviceorder/{service_ordered_id}`  
**Auth Required:** ✅ Yes

### 6.15 Delete Service Order

**Endpoint:** `DELETE /workorders/delete/serviceorder/{service_ordered_id}`  
**Auth Required:** ✅ Yes

### 6.16 Delete Work Order

**Endpoint:** `DELETE /workorders/{workorder_id}`  
**Auth Required:** ✅ Yes

### 6.17 Get Work Orders by Customer

**Endpoint:** `GET /workorders/customer/{customer_id}`  
**Auth Required:** ❌ No

### 6.18 Get Work Order Payment Status

**Endpoint:** `GET /workorders/{workorder_id}/status-pembayaran`  
**Auth Required:** ❌ No

**Response:**
```json
{
  "status": "success",
  "data": {
    "workorder_id": "uuid-string",
    "status_pembayaran": "lunas",
    "total_cost": 250000,
    "jumlah_bayar": 250000,
    "sisa": 0
  }
}
```

### 6.19 Get Work Order Status

**Endpoint:** `GET /workorders/{workorder_id}/status`  
**Auth Required:** ❌ No

---

## 7. Products & Services

### 7.1 Create New Product

**Endpoint:** `POST /products/create/new`  
**Auth Required:** ❌ No

**Request Body:**
```json
{
  "nama": "Oli Mesin Mobil",
  "brand_id": "uuid-string",
  "category_id": "uuid-string",
  "satuan_id": "uuid-string",
  "harga_jual": 75000,
  "harga_beli": 60000,
  "stock": 100,
  "is_consignment": false
}
```

### 7.2 Get All Products

**Endpoint:** `GET /products/all`  
**Auth Required:** ❌ No

**Response:**
```json
{
  "status": "success",
  "data": [
    {
      "id": "uuid-string",
      "nama": "Oli Mesin",
      "brand": "Castrol",
      "category": "Pelumas",
      "satuan": "Liter",
      "harga_jual": 75000,
      "harga_beli": 60000,
      "stock": 100,
      "is_consignment": false
    }
  ]
}
```

### 7.3 Get Product by ID

**Endpoint:** `GET /products/{product_id}`  
**Auth Required:** ❌ No

### 7.3.1 Update Product

**Endpoint:** `PUT /products/{product_id}`
**Auth Required:** Yes

Request bersifat parsial: kirim hanya field yang ingin diubah dan minimal satu field wajib ada.

```json
{
  "name": "Oli Mesin 1L",
  "type": "sparepart",
  "description": "Oli mesin sintetis",
  "price": 150000,
  "cost": 100000,
  "min_stock": 10,
  "brand_id": "uuid-string",
  "category_id": "uuid-string",
  "satuan_id": "uuid-string",
  "supplier_id": null,
  "is_consignment": false,
  "consignment_commission": 0,
  "is_internal_consumption": false
}
```

- HTTP `200`: produk berhasil diperbarui.
- HTTP `404`: produk tidak ditemukan.
- HTTP `422`: payload kosong, nilai negatif, atau field wajib diisi `null`.
- HTTP `500`: kegagalan database yang tidak terduga.

### 7.3.2 Delete Product

**Endpoint:** `DELETE /products/{product_id}`
**Auth Required:** Yes

- HTTP `200`: produk yang belum pernah digunakan berhasil dihapus.
- HTTP `404`: produk tidak ditemukan.
- HTTP `409`: produk masih direferensikan Work Order, PO, inventory, pergerakan stok,
  histori HPP, paket, atau penerimaan konsinyasi.
- HTTP `500`: kegagalan database yang tidak terduga.

Penghapusan tidak melakukan cascade terhadap histori transaksi.

### 7.4 Create New Service

**Endpoint:** `POST /products/service/create/new`  
**Auth Required:** ✅ Yes

**Request Body:**
```json
{
  "nama": "Tune Up Mesin",
  "harga": 300000,
  "deskripsi": "Complete engine tune up service"
}
```

### 7.5 Get All Services

**Endpoint:** `GET /products/service/all`  
**Auth Required:** ❌ No

### 7.6 Get Service by ID

**Endpoint:** `GET /products/service/{service_id}`  
**Auth Required:** ❌ No

### 7.7 Create Brand

**Endpoint:** `POST /products/brand/create/new`  
**Auth Required:** ✅ Yes

**Request Body:**
```json
{
  "nama": "Castrol"
}
```

### 7.8 Create Category

**Endpoint:** `POST /products/category/create/new`  
**Auth Required:** ✅ Yes

**Request Body:**
```json
{
  "nama": "Pelumas"
}
```

### 7.9 Create Satuan (Unit)

**Endpoint:** `POST /products/satuan/create/new`  
**Auth Required:** ✅ Yes

**Request Body:**
```json
{
  "nama": "Liter"
}
```

### 7.10 Get All Brands

**Endpoint:** `GET /products/brands/all`  
**Auth Required:** ❌ No

### 7.11 Get All Satuans

**Endpoint:** `GET /products/satuans/all`  
**Auth Required:** ❌ No

### 7.12 Get All Categories

**Endpoint:** `GET /products/categories/all`  
**Auth Required:** ❌ No

### 7.13 Get All Inventory

**Endpoint:** `GET /products/inventory/all`  
**Auth Required:** ❌ No

**Query Parameters:**
- `page` (optional, default `1`): halaman data inventory, minimum `1`
- `limit` (optional, default `25`): jumlah item per halaman, minimum `1`, maksimum `100`
- `search` (optional): pencarian nama, type, deskripsi, brand, atau kategori produk; panjang `1` sampai `100` karakter
- `category_id` (optional): filter berdasarkan kategori
- `stock_status` (optional): `safe` atau `reorder`

Query parameter yang melanggar batas atau enum di atas menghasilkan HTTP `422`.

**Response Body:**
```json
{
  "status": "success",
  "message": "Inventory retrieved successfully",
  "data": [
    {
      "id": "550e8400-e29b-41d4-a716-446655440000",
      "name": "Oli Shell 1L",
      "type": "product",
      "description": "Oli mesin berkualitas tinggi",
      "price": 150000,
      "purchase_price": 95000,
      "hpp": 100000,
      "margin": 50000.0,
      "margin_percentage": 33.33,
      "min_stock": 10,
      "total_stock": 50,
      "stock_status": "safe",
      "is_consignment": false,
      "category_name": "Sparepart",
      "brand_name": "Shell",
      "satuan_name": "Botol",
      "vendor_code": "VND-001", 
      "supplier_name": "PT Supplier Maju"
    }
  ],
  "pagination": {
    "page": 1,
    "limit": 25,
    "total": 150,
    "total_pages": 6,
    "has_previous": false,
    "has_next": true
  }
}
```

**Field Definitions:**
- `price` (decimal): harga jual saat ini
- `purchase_price` (decimal/null): harga transaksi terbaru antara PO berstatus `diterima`/`dibayarkan` dan penerimaan konsinyasi dengan quantity positif; `null` jika belum ada histori valid. Pada instalasi lama yang belum memiliki tabel konsinyasi, sumber tersebut dilewati tanpa menggagalkan endpoint.
- `hpp` (decimal): harga pokok inventory yang dipakai untuk margin/laba-rugi
- `margin` (decimal): selisih `price - hpp`
- `margin_percentage` (decimal): persentase margin terhadap harga jual
- `min_stock` (decimal): stok minimum
- `total_stock` (decimal): total stok saat ini di inventory
- `stock_status` (string): status stok, saat ini `safe` atau `reorder`
- `category_name` (string): nama kategori
- `brand_name` (string): nama brand
- `satuan_name` (string): nama satuan
- `vendor_code` (string/null): kode unik supplier/vendor yang berasal dari sumber transaksi yang sama dengan `purchase_price` terbaru. Jika belum ada histori transaksi, field ini fallback ke supplier master produk.
- `supplier_name` (string/null): nama supplier/vendor yang berasal dari sumber transaksi yang sama dengan `purchase_price` terbaru. Jika belum ada histori transaksi, field ini fallback ke supplier master produk.

Response menggunakan satu envelope saja. `data` langsung berupa array inventory dan `pagination`
berada sejajar dengan `data`, bukan berada di dalam `data`.

Kegagalan database atau mapper yang tidak terduga menghasilkan HTTP `500` dengan pesan umum
`Failed to retrieve inventory`; detail internal tidak diekspos pada response production.

**Empty Response:**
```json
{
  "status": "success",
  "message": "Inventory retrieved successfully",
  "data": [],
  "pagination": {
    "page": 1,
    "limit": 25,
    "total": 0,
    "total_pages": 0,
    "has_previous": false,
    "has_next": false
  }
}
```

### 7.14 Get All Consignment Inventory

**Endpoint:** `GET /products/inventory/all/consignment`  
**Auth Required:** ❌ No

**Response:** Sama seperti "Get All Inventory" tetapi hanya menampilkan produk dengan `is_consignment: true`

### 7.15 Get All Non-Consignment Inventory

**Endpoint:** `GET /products/inventory/all/excconsignment`  
**Auth Required:** ❌ No

**Response:** Sama seperti "Get All Inventory" tetapi hanya menampilkan produk dengan `is_consignment: false`

### 7.16 Get Inventory by Product ID

**Endpoint:** `GET /products/inventory/{product_id}`  
**Auth Required:** ❌ No

**Response:** Sama seperti item pada "Get All Inventory" tetapi hanya 1 produk berdasarkan `product_id`. Semantik `purchase_price`, `vendor_code`, dan `supplier_name` juga sama: ketiganya mengikuti sumber transaksi terbaru, dengan fallback supplier master produk jika histori transaksi belum ada.

### 7.17 Create Product Move (Single)

**Endpoint:** `POST /products/inventory/move/new`  
**Auth Required:** ✅ Yes

**Request Body:**
```json
{
  "product_id": "uuid-string",
  "from_location": "warehouse",
  "to_location": "shop",
  "kuantitas": 10,
  "tanggal": "2025-01-18",
  "keterangan": "Stock replenishment"
}
```

### 7.18 Create Product Move (Multi)

**Endpoint:** `POST /products/inventory/move/new/multi`  
**Auth Required:** ✅ Yes

**Request Body:**
```json
{
  "moves": [
    {
      "product_id": "uuid-1",
      "kuantitas": 5
    },
    {
      "product_id": "uuid-2",
      "kuantitas": 10
    }
  ],
  "from_location": "warehouse",
  "to_location": "shop",
  "tanggal": "2025-01-18"
}
```

### 7.19 Update Product Cost

**Endpoint:** `PUT /products/cost`  
**Auth Required:** ✅ Yes

**Request Body:**
```json
{
  "product_id": "uuid-string",
  "new_cost": 65000,
  "effective_date": "2025-01-18"
}
```

### 7.20 Inventory Adjustment

**Endpoint:** `POST /products/inventory/adjustment`  
**Auth Required:** ✅ Yes

**Request Body:**
```json
{
  "product_id": "uuid-string",
  "quantity": -5,
  "performed_by": "admin",
  "notes": "Stock opname selisih -5"
}
```

### 7.21 Get Cost History

**Endpoint:** `GET /products/cost-history`  
**Auth Required:** ❌ No

**Query Parameters:**
- `start_date` (optional): Filter from date
- `end_date` (optional): Filter to date

### 7.22 Get Cost History by Product

**Endpoint:** `GET /products/{product_id}/cost-history`  
**Auth Required:** ❌ No

### 7.23 Get Cost Summary by Product

**Endpoint:** `GET /products/{product_id}/cost-summary`  
**Auth Required:** ❌ No

**Response:**
```json
{
  "status": "success",
  "data": {
    "product_id": "uuid-string",
    "product_name": "Oli Mesin",
    "current_cost": 65000,
    "average_cost": 62500,
    "total_quantity": 100,
    "cost_history": []
  }
}
```

---

## 8. Inventory Management

### 8.1 Get Inventory by Product

**Endpoint:** `GET /inventory/{product_id}`  
**Auth Required:** ❌ No

### 8.2 Product Move History Report

**Endpoint:** `POST /inventory/product-move-history-report`  
**Auth Required:** ✅ Yes

**Request Body:**
```json
{
  "start_date": "2026-07-01", "end_date": "2026-07-31", "product_id": null,
  "movement_type": null, "reference_type": null, "supplier_id": null,
  "customer_id": null, "search": null, "page": 1, "limit": 25, "sort_order": "asc"
}
```

**Response Body:**
```json
{
  "status": "success", "message": "Laporan pergerakan barang berhasil dihasilkan",
  "data": {
    "summary": {"opening_balance": 5, "total_in": 10, "total_out": 4, "total_adjustment": 0, "closing_balance": 11},
    "total_entries": 1,
    "items": [{"movement_id": "uuid", "product_id": "uuid", "product_name": "Oli Mesin", "type": "income", "quantity": 10, "quantity_in": 10, "quantity_out": 0, "balance_before": 5, "balance_after": 15, "purchase_price": 100000, "selling_price": null, "price": 100000, "hpp": 100000, "reference_type": "purchase_order", "reference_id": "uuid", "reference_no": "PO-001", "purchase_order_id": "uuid", "purchase_order_no": "PO-001", "workorder_id": null, "workorder_no": null, "supplier_id": "uuid", "vendor_code": "VND-001", "vendor_name": "PT Vendor", "customer_id": null, "customer_name": null, "vehicle_id": null, "nopol": null, "timestamp": "2026-07-12T10:00:00+07:00", "performed_by": "admin", "notes": "received"}],
    "pagination": {"page": 1, "limit": 25, "total": 1, "total_pages": 1, "has_previous": false, "has_next": false}
  }
}
```

`movement_type`: `income`, `outcome`, `adjustment`, `loss`, atau `internal_consumption`.
`reference_type`: `purchase_order`, `workorder`, `consignment_receipt`, `adjustment`, `loss`, atau `internal_consumption`.
`page >= 1`, `1 <= limit <= 100`, dan `sort_order` hanya `asc`/`desc`.
Harga dan HPP menggunakan snapshot transaksi. Data lama tanpa referensi mengembalikan field terkait sebagai `null`.
OpenAPI mendokumentasikan response `200`, `401`, `403`, `404`, `422`, dan `500`.

### 8.3 Create Product Move

**Endpoint:** `POST /inventory/move/new`  
**Auth Required:** ✅ Yes

### 8.4 Create Product Loss

**Endpoint:** `POST /inventory/move/loss`  
**Auth Required:** ✅ Yes

**Request Body:**
```json
{
  "product_id": "uuid-string",
  "kuantitas": 2,
  "reason": "Damaged during inspection",
  "tanggal": "2025-01-18"
}
```

### 8.5 Update Product Cost

**Endpoint:** `POST /inventory/update-cost`  
**Auth Required:** ✅ Yes

---

## 8.6 Consignment Receipt Management

### 8.6.1 Create Consignment Receipt

**Endpoint:** `POST /inventory/consignment-receipt/create`  
**Auth Required:** ✅ Yes

**Description:** Track when consignment products are received from suppliers.

**Request Body:**
```json
{
  "product_id": "uuid-string",
  "supplier_id": "uuid-string",
  "receipt_number": "CR-2025-001",
  "receipt_date": "2025-01-18",
  "quantity_received": 50,
  "unit_price": 100000,
  "total_value": 5000000,
  "received_by": "John Doe",
  "notes": "Received 50 units of brake pads from PT Supplier"
}
```

**Response:**
```json
{
  "status": "success",
  "message": "Consignment receipt created successfully",
  "data": {
    "id": "uuid-string",
    "receipt_number": "CR-2025-001",
    "receipt_date": "2025-01-18",
    "quantity_received": 50,
    "total_value": 5000000,
    "created_at": "2025-01-18T10:30:00"
  }
}
```

**Field Definitions:**
- `product_id` (string, required): UUID of consignment product
- `supplier_id` (string, required): UUID of supplier
- `receipt_number` (string, required): Unique receipt number (e.g., CR-2025-001)
- `receipt_date` (date, required): Date of receipt (YYYY-MM-DD)
- `quantity_received` (decimal, required): Quantity received
- `unit_price` (decimal, optional): Price per unit at time of receipt
- `total_value` (decimal, optional): Total value of receipt (auto-calculated if not provided)
- `received_by` (string, required): User who received the goods
- `notes` (string, optional): Additional notes

### 8.6.2 Get Consignment Receipt by ID

**Endpoint:** `GET /inventory/consignment-receipt/{receipt_id}`  
**Auth Required:** ❌ No

**Response:**
```json
{
  "status": "success",
  "data": {
    "id": "uuid-string",
    "receipt_number": "CR-2025-001",
    "receipt_date": "2025-01-18",
    "product_id": "uuid-string",
    "supplier_id": "uuid-string",
    "quantity_received": 50,
    "unit_price": 100000,
    "total_value": 5000000,
    "notes": "Received 50 units of brake pads from PT Supplier",
    "received_by": "John Doe",
    "created_at": "2025-01-18T10:30:00",
    "updated_at": "2025-01-18T10:30:00"
  }
}
```

### 8.6.3 List All Consignment Receipts

**Endpoint:** `GET /inventory/consignment-receipt`  
**Auth Required:** ❌ No

**Query Parameters:**
- `skip` (integer, default: 0): Number of records to skip
- `limit` (integer, default: 100): Number of records to return

**Response:**
```json
{
  "status": "success",
  "message": "Retrieved 5 consignment receipts",
  "data": [
    {
      "id": "uuid-string",
      "receipt_number": "CR-2025-001",
      "receipt_date": "2025-01-18",
      "product_id": "uuid-string",
      "supplier_id": "uuid-string",
      "quantity_received": 50,
      "unit_price": 100000,
      "total_value": 5000000
    }
  ]
}
```

### 8.6.4 List Receipts by Supplier

**Endpoint:** `GET /inventory/consignment-receipt/supplier/{supplier_id}`  
**Auth Required:** ❌ No

**Path Parameters:**
- `supplier_id` (string): UUID of the supplier

**Query Parameters:**
- `skip` (integer, default: 0): Number of records to skip
- `limit` (integer, default: 100): Number of records to return

### 8.6.5 Update Consignment Receipt

**Endpoint:** `PUT /inventory/consignment-receipt/{receipt_id}`  
**Auth Required:** ✅ Yes

**Path Parameters:**
- `receipt_id` (string): UUID of the receipt to update

**Request Body (all fields optional):**
```json
{
  "receipt_date": "2025-01-19",
  "quantity_received": 55,
  "unit_price": 105000,
  "total_value": 5775000,
  "notes": "Updated quantity after recount"
}
```

**Response:**
```json
{
  "status": "success",
  "message": "Consignment receipt updated successfully",
  "data": {
    "id": "uuid-string",
    "receipt_number": "CR-2025-001",
    "receipt_date": "2025-01-19",
    "quantity_received": 55,
    "total_value": 5775000,
    "updated_at": "2025-01-18T15:45:00"
  }
}
```

### 8.6.6 Delete Consignment Receipt

**Endpoint:** `DELETE /inventory/consignment-receipt/{receipt_id}`  
**Auth Required:** ✅ Yes

**Path Parameters:**
- `receipt_id` (string): UUID of the receipt to delete

**Response:**
```json
{
  "status": "success",
  "message": "Consignment receipt deleted successfully",
  "data": {
    "id": "uuid-string",
    "receipt_number": "CR-2025-001",
    "deleted_at": "2025-01-18T16:00:00"
  }
}
```

---

## 8.7 Inventory Adjustment Management

### 8.7.1 Create Inventory Adjustment

**Endpoint:** `POST /products/inventory/adjustment`  
**Auth Required:** ✅ Yes

**Description:** Record manual inventory adjustments (corrections).

**Request Body:**
```json
{
  "product_id": "uuid-string",
  "quantity": -5,
  "performed_by": "John Doe",
  "notes": "Stock opname selisih -5"
}
```

### 8.7.2 List Inventory Adjustments

**Endpoint:** `GET /products/inventory/adjustment`  
**Auth Required:** ❌ No

**Query Parameters:**
- `skip` (int, optional, default: 0): Jumlah data yang dilewati
- `limit` (int, optional, default: 100): Jumlah data yang diambil

**Response:**
```json
{
  "status": "success",
  "message": "Retrieved 2 adjustment records",
  "data": [
    {
      "id": "uuid-string",
      "product_id": "uuid-string",
      "type": "adjustment",
      "quantity": -5,
      "timestamp": "2026-07-12T09:15:00",
      "performed_by": "John Doe",
      "notes": "Stock opname selisih -5"
    }
  ]
}
```

### 8.7.3 Get Inventory Adjustment by ID

**Endpoint:** `GET /products/inventory/adjustment/{adjustment_id}`  
**Auth Required:** ❌ No

**Path Parameters:**
- `adjustment_id` (string): UUID adjustment

### 8.7.4 Update Inventory Adjustment

**Endpoint:** `PUT /products/inventory/adjustment/{adjustment_id}`  
**Auth Required:** ✅ Yes

**Path Parameters:**
- `adjustment_id` (string): UUID of the adjustment to update

**Request Body:**
```json
{
  "product_id": "uuid-string",
  "quantity": -10,
  "performed_by": "Jane Doe",
  "notes": "Revisi hasil stock opname"
}
```

**Response:**
```json
{
  "status": "success",
  "message": "Adjustment updated successfully",
  "data": {
    "id": "uuid-string",
    "product_id": "uuid-string",
    "type": "adjustment",
    "quantity": -10,
    "timestamp": "2026-07-12T10:30:00",
    "performed_by": "Jane Doe",
    "notes": "Revisi hasil stock opname"
  }
}
```

**Important Note:**
- When updating an adjustment, the inventory is recalculated based on the difference
- Old adjustment effect is reversed, then new adjustment is applied
- Example: Old quantity move: -5, New quantity move: -10 = Net change: -5 more units removed

### 8.7.5 Delete Inventory Adjustment

**Endpoint:** `DELETE /products/inventory/adjustment/{adjustment_id}`  
**Auth Required:** ✅ Yes

**Path Parameters:**
- `adjustment_id` (string): UUID of the adjustment to delete

**Response:**
```json
{
  "status": "success",
  "message": "Adjustment deleted and reversed successfully",
  "data": {
    "message": "Adjustment deleted successfully",
    "deleted_id": "uuid-string",
    "reversed_quantity": -5
  }
}
```

**Important Note:**
- Deleting an adjustment reverses its effect on inventory
- If adjustment was -5 units, inventory will gain back 5 units
- Ensures inventory audit trail accuracy

---

## 8.8 Inventory Loss Management

### 8.8.1 Create Inventory Loss

**Endpoint:** `POST /inventory/move/loss`  
**Auth Required:** ✅ Yes

**Description:** Record lost, damaged, or destroyed inventory.

**Request Body:**
```json
{
  "product_id": "uuid-string",
  "type": "outcome",
  "quantity": 2,
  "performed_by": "Gudang",
  "notes": "Barang rusak saat inspeksi"
}
```

### 8.8.2 List Inventory Loss

**Endpoint:** `GET /inventory/loss`  
**Auth Required:** ❌ No

**Query Parameters:**
- `skip` (int, optional, default: 0): Jumlah data yang dilewati
- `limit` (int, optional, default: 100): Jumlah data yang diambil

### 8.8.3 Get Inventory Loss by ID

**Endpoint:** `GET /inventory/loss/{loss_id}`  
**Auth Required:** ❌ No

**Path Parameters:**
- `loss_id` (string): UUID loss record

### 8.8.4 Update Inventory Loss

**Endpoint:** `PUT /inventory/loss/{loss_id}`  
**Auth Required:** ✅ Yes

**Path Parameters:**
- `loss_id` (string): UUID of the loss record to update

**Request Body:**
```json
{
  "product_id": "uuid-string",
  "type": "outcome",
  "quantity": 3,
  "performed_by": "Gudang",
  "notes": "Tambahan barang rusak ditemukan"
}
```

**Response:**
```json
{
  "status": "success",
  "message": "Loss record updated successfully",
  "data": {
    "id": "uuid-string",
    "product_id": "uuid-string",
    "type": "outcome",
    "quantity": 3,
    "timestamp": "2026-07-12T11:20:00",
    "performed_by": "Gudang",
    "notes": "Tambahan barang rusak ditemukan"
  }
}
```

**Important Note:**
- When updating a loss, the inventory quantity is adjusted
- Old loss effect is reversed, then new loss quantity is applied
- Example: Old: 2 lost, New: 3 lost = 1 additional unit removed from inventory

### 8.8.5 Delete Inventory Loss

**Endpoint:** `DELETE /inventory/loss/{loss_id}`  
**Auth Required:** ✅ Yes

**Path Parameters:**
- `loss_id` (string): UUID of the loss record to delete

**Response:**
```json
{
  "status": "success",
  "message": "Loss record deleted and reversed successfully",
  "data": {
    "message": "Loss record deleted successfully",
    "deleted_id": "uuid-string",
    "reversed_quantity": 2
  }
}
```

**Important Note:**
- Deleting a loss reverses its effect on inventory
- If 2 units were lost, inventory will gain back 2 units
- Useful for correcting erroneous loss records

---

## 9. Purchase Orders

### 9.1 Create Purchase Order

**Endpoint:** `POST /purchase-orders/create`  
**Auth Required:** ✅ Yes

**Request Body:**
```json
{
  "supplier_id": "uuid-string",
  "tanggal_po": "2025-01-18",
  "status_po": "pending",
  "lines": [
    {
      "product_id": "uuid-string",
      "kuantitas": 50,
      "harga": 60000
    }
  ]
}
```

### 9.2 Get All Purchase Orders

**Endpoint:** `GET /purchase-orders/`  
**Auth Required:** ❌ No

**Response:**
```json
{
  "status": "success",
  "data": [
    {
      "id": "uuid-string",
      "no_po": "PO-2025-001",
      "supplier": {
        "nama": "PT Supplier Jaya"
      },
      "tanggal_po": "2025-01-18",
      "status_po": "pending",
      "total": 3000000,
      "lines": []
    }
  ]
}
```

### 9.3 Get Purchase Order by ID

**Endpoint:** `GET /purchase-orders/{purchase_order_identifier}`  
**Auth Required:** ❌ No

### 9.4 Update Purchase Order

**Endpoint:** `POST /purchase-orders/{purchase_order_id}`  
**Auth Required:** ✅ Yes

### 9.5 Update Purchase Order Status

**Endpoint:** `POST /purchase-orders/{purchase_order_id}/status`  
**Auth Required:** ✅ Yes

**Request Body:**
```json
{
  "status_po": "approved"
}
```

### 9.6 Delete Purchase Order

**Endpoint:** `DELETE /purchase-orders/{purchase_order_id}`  
**Auth Required:** ✅ Yes

### 9.7 Upload Bukti (Proof of Payment)

**Endpoint:** `POST /purchase-orders/{purchase_order_id}/upload-bukti`  
**Auth Required:** ✅ Yes

**Request:** Multipart form-data
- `file`: Image file

### 9.8 Update PO Line

**Endpoint:** `PUT /purchase-orders/{purchase_order_id}/lines/{line_id}`  
**Auth Required:** ✅ Yes

### 9.9 Add PO Line

**Endpoint:** `POST /purchase-orders/{purchase_order_id}/lines`  
**Auth Required:** ✅ Yes

**Request Body:**
```json
{
  "product_id": "uuid-string",
  "kuantitas": 20,
  "harga": 65000
}
```

### 9.10 Delete PO Line

**Endpoint:** `DELETE /purchase-orders/{purchase_order_id}/lines/{line_id}`  
**Auth Required:** ✅ Yes

### 9.11 Pay Purchase Order

**Endpoint:** `POST /purchase-orders/pay/{purchase_id}`  
**Auth Required:** ✅ Yes

**Request Body:**
```json
{
  "jumlah_bayar": 3000000,
  "metode_pembayaran": "transfer",
  "id_akun_kas": "uuid-string",
  "tanggal_bayar": "2025-01-18"
}
```

### 9.12 Get PO by Supplier

**Endpoint:** `GET /purchase-orders/supplier/{supplier_id}`  
**Auth Required:** ❌ No

### 9.13 Get PO Payment Status

**Endpoint:** `GET /purchase-orders/{purchase_order_id}/status-pembayaran`  
**Auth Required:** ❌ No

---

## 10. Expenses

### 10.1 Create Expense

**Endpoint:** `POST /expenses/create`  
**Auth Required:** ✅ Yes

**Request Body:**
```json
{
  "tanggal": "2025-01-18",
  "kategori": "Operational",
  "deskripsi": "Office supplies",
  "jumlah": 500000,
  "metode_pembayaran": "cash",
  "id_akun_kas": "uuid-string"
}
```

### 10.2 Get All Expenses

**Endpoint:** `GET /expenses/`  
**Auth Required:** ❌ No

**Query Parameters:**
- `start_date` (optional)
- `end_date` (optional)
- `kategori` (optional)

### 10.3 Get Expense by ID

**Endpoint:** `GET /expenses/{expenses_id}`  
**Auth Required:** ❌ No

### 10.4 Update Expense

**Endpoint:** `PUT /expenses/{expenses_id}`  
**Auth Required:** ✅ Yes

### 10.5 Delete Expense

**Endpoint:** `DELETE /expenses/{expenses_id}`  
**Auth Required:** ✅ Yes

### 10.6 Upload Bukti Expense

**Endpoint:** `POST /expenses/{expenses_id}/upload-bukti`  
**Auth Required:** ✅ Yes

**Request:** Multipart form-data

### 10.7 Get Expense Status

**Endpoint:** `GET /expenses/{expenses_id}/status`  
**Auth Required:** ❌ No

---

## 11. Booking

### 11.1 Create Booking

**Endpoint:** `POST /bookings/create/new`  
**Auth Required:** ❌ No

**Request Body:**
```json
{
  "customer_id": "uuid-string",
  "vehicle_id": "uuid-string",
  "tanggal_booking": "2025-01-20",
  "jam_booking": "10:00",
  "keluhan": "Servis berkala 20.000 km",
  "status": "confirmed"
}
```

### 11.2 Get All Bookings

**Endpoint:** `GET /bookings/all`  
**Auth Required:** ❌ No

### 11.3 Get Booking by ID

**Endpoint:** `GET /bookings/{booking_id}`  
**Auth Required:** ❌ No

### 11.4 Update Booking

**Endpoint:** `POST /bookings/edit/{booking_id}`  
**Auth Required:** ✅ Yes

### 11.5 Delete Booking

**Endpoint:** `GET /bookings/delete/{booking_id}`  
**Auth Required:** ✅ Yes

---

## 12. Supplier

### 12.1 Create Supplier

**Endpoint:** `POST /suppliers/create`  
**Auth Required:** ✅ Yes

**Request Body:**
```json
{
  "nama": "PT Supplier ABC",
  "alamat": "Jl. Industri No. 88",
  "telepon": "021-12345678",
  "email": "supplier@example.com",
  "kontak_person": "John Supplier"
}
```

### 12.2 Update Supplier

**Endpoint:** `POST /suppliers/{supplier_id}`  
**Auth Required:** ✅ Yes

### 12.3 Delete Supplier

**Endpoint:** `DELETE /suppliers/{supplier_id}`  
**Auth Required:** ✅ Yes

### 12.4 Get All Suppliers

**Endpoint:** `GET /suppliers/all`  
**Auth Required:** ❌ No

### 12.5 Get Supplier by ID

**Endpoint:** `GET /suppliers/{supplier_id}`  
**Auth Required:** ❌ No

---

## 13. Karyawan (Employee)

### 13.1 Create Karyawan

**Endpoint:** `POST /karyawan/create`  
**Auth Required:** ✅ Yes

**Request Body:**
```json
{
  "nama": "Ahmad Mekanik",
  "posisi": "Mechanic",
  "telepon": "08567890123",
  "alamat": "Jl. Pekerja No. 45",
  "tanggal_masuk": "2025-01-01"
}
```

### 13.2 Get All Karyawan

**Endpoint:** `GET /karyawan/all`  
**Auth Required:** ❌ No

### 13.3 Get Karyawan by ID

**Endpoint:** `GET /karyawan/{karyawan_id}`  
**Auth Required:** ❌ No

---

## 14. Attendance

### 14.1 Create Attendance

**Endpoint:** `POST /attendance/create`  
**Auth Required:** ✅ Yes

**Request Body:**
```json
{
  "karyawan_id": "uuid-string",
  "tanggal": "2025-01-18",
  "jam_masuk": "08:00",
  "jam_keluar": "17:00",
  "status": "hadir"
}
```

### 14.2 Get All Attendance

**Endpoint:** `GET /attendance/`  
**Auth Required:** ❌ No

### 14.3 Get Attendance by ID

**Endpoint:** `GET /attendance/{attendance_id}`  
**Auth Required:** ❌ No

### 14.4 Get Attendance by Karyawan

**Endpoint:** `GET /attendance/karyawan/{karyawan_id}`  
**Auth Required:** ❌ No

### 14.5 Get Attendance by Date Range

**Endpoint:** `GET /attendance/date-range/`  
**Auth Required:** ❌ No

**Query Parameters:**
- `start_date`: YYYY-MM-DD
- `end_date`: YYYY-MM-DD

### 14.6 Update Attendance

**Endpoint:** `PUT /attendance/{attendance_id}`  
**Auth Required:** ✅ Yes

### 14.7 Delete Attendance

**Endpoint:** `DELETE /attendance/{attendance_id}`  
**Auth Required:** ✅ Yes

### 14.8 Check In

**Endpoint:** `POST /attendance/check-in/{karyawan_id}`  
**Auth Required:** ✅ Yes

**Response:**
```json
{
  "status": "success",
  "message": "Check-in successful",
  "data": {
    "attendance_id": "uuid-string",
    "karyawan_id": "uuid-string",
    "jam_masuk": "08:15:30"
  }
}
```

### 14.9 Check Out

**Endpoint:** `POST /attendance/check-out/{karyawan_id}`  
**Auth Required:** ✅ Yes

### 14.10 Get Attendance Status

**Endpoint:** `GET /attendance/status/{karyawan_id}`  
**Auth Required:** ❌ No

**Response:**
```json
{
  "status": "success",
  "data": {
    "karyawan_id": "uuid-string",
    "checked_in": true,
    "jam_masuk": "08:15:30",
    "checked_out": false
  }
}
```

---

## 15. Dashboard

All dashboard endpoints require authentication.

### 15.1 Dashboard Summary

**Endpoint:** `GET /dashboard/summary`  
**Auth Required:** ✅ Yes

**Response:**
```json
{
  "status": "success",
  "data": {
    "workorders_today": 12,
    "workorders_finished": 450,
    "workorders_pending": 38,
    "revenue_today": 5500000,
    "revenue_this_month": 85000000,
    "customers_total": 280,
    "vehicles_total": 350
  }
}
```

### 15.2 Work Orders Pie Chart

**Endpoint:** `GET /dashboard/workorders-pie`  
**Auth Required:** ✅ Yes

**Response:**
```json
{
  "status": "success",
  "data": {
    "labels": ["Pending", "In Progress", "Completed", "Cancelled"],
    "values": [38, 22, 450, 5]
  }
}
```

### 15.3 Sales Monthly Report

**Endpoint:** `GET /dashboard/sales-monthly`  
**Auth Required:** ✅ Yes

**Query Parameters:**
- `months` (optional, default: 6): Number of months (1-24)

**Response:**
```json
{
  "status": "success",
  "data": {
    "labels": ["Aug 2025", "Sep 2025", "Oct 2025", "Nov 2025", "Dec 2025", "Jan 2026"],
    "values": [45000000, 52000000, 48000000, 55000000, 60000000, 85000000]
  }
}
```

### 15.4 Purchase Monthly Report

**Endpoint:** `GET /dashboard/purchase-monthly`  
**Auth Required:** ✅ Yes

**Query Parameters:**
- `months` (optional, default: 6): Number of months (1-24)

### 15.5 Expenses Monthly Report

**Endpoint:** `GET /dashboard/expenses-monthly`  
**Auth Required:** ✅ Yes

**Query Parameters:**
- `months` (optional, default: 6): Number of months (1-24)

### 15.6 Combined Monthly Report

**Endpoint:** `GET /dashboard/combined-monthly`  
**Auth Required:** ✅ Yes

**Query Parameters:**
- `months` (optional, default: 6): Number of months (1-24)

**Response:**
```json
{
  "status": "success",
  "data": {
    "labels": ["Aug 2025", "Sep 2025", "Oct 2025", "Nov 2025", "Dec 2025", "Jan 2026"],
    "sales": [45000000, 52000000, 48000000, 55000000, 60000000, 85000000],
    "purchases": [30000000, 35000000, 32000000, 38000000, 40000000, 55000000],
    "expenses": [8000000, 9000000, 8500000, 9500000, 10000000, 12000000]
  }
}
```

---

## 16. Accounting & Reports

All accounting endpoints require authentication (✅).

### 16.1 Journal Entry - Purchase

**Endpoint:** `POST /accounting/purchase`  
**Auth Required:** ✅ Yes

### 16.2 Journal Entry - Sale

**Endpoint:** `POST /accounting/sale`  
**Auth Required:** ✅ Yes

### 16.3 Journal Entry - Payment AR (Account Receivable)

**Endpoint:** `POST /accounting/payment-ar`  
**Auth Required:** ✅ Yes

### 16.4 Journal Entry - Payment AP (Account Payable)

**Endpoint:** `POST /accounting/payment-ap`  
**Auth Required:** ✅ Yes

### 16.5 Journal Entry - Expense

**Endpoint:** `POST /accounting/expense`  
**Auth Required:** ✅ Yes

### 16.6 Journal Entry - Consignment Payment

**Endpoint:** `POST /accounting/consignment-payment`  
**Auth Required:** ✅ Yes

### 16.7 Sales Journal

**Endpoint:** `POST /accounting/sales-journal`  
**Auth Required:** ✅ Yes

**Request Body:**
```json
{
  "start_date": "2025-01-01",
  "end_date": "2025-01-31"
}
```

### 16.8 Sales Payment Journal

**Endpoint:** `POST /accounting/sales-payment-journal`  
**Auth Required:** ✅ Yes

### 16.9 Purchase Journal

**Endpoint:** `POST /accounting/purchase-journal`  
**Auth Required:** ✅ Yes

### 16.10 Purchase Payment Journal

**Endpoint:** `POST /accounting/purchase-payment-journal`  
**Auth Required:** ✅ Yes

### 16.11 Expense Journal

**Endpoint:** `POST /accounting/expense-journal`  
**Auth Required:** ✅ Yes

### 16.12 Expense Payment Journal

**Endpoint:** `POST /accounting/expense-payment-journal`  
**Auth Required:** ✅ Yes

### 16.13 Internal Consumption

**Endpoint:** `POST /accounting/internal-consumption`  
**Auth Required:** ✅ Yes

### 16.14 Cash In

**Endpoint:** `POST /accounting/cash-in`  
**Auth Required:** ✅ Yes

**Request Body:**
```json
{
  "tanggal": "2025-01-18",
  "jumlah": 5000000,
  "keterangan": "Modal tambahan",
  "id_akun_kas": "uuid-string",
  "id_akun_equity": "uuid-string"
}
```

### 16.15 Cash Out

**Endpoint:** `POST /accounting/cash-out`  
**Auth Required:** ✅ Yes

### 16.16 Get All Journals

**Endpoint:** `GET /accounting/journals`  
**Auth Required:** ❌ No

**Query Parameters:**
- `start_date` (optional)
- `end_date` (optional)
- `account_id` (optional)

### 16.17 Create Account

**Endpoint:** `POST /accounting/account/create`  
**Auth Required:** ✅ Yes

**Request Body:**
```json
{
  "kode": "1-1001",
  "nama": "Kas Besar",
  "tipe": "asset",
  "saldo_awal": 10000000
}
```

### 16.18 Edit Account

**Endpoint:** `POST /accounting/account/edit/{account_id}`  
**Auth Required:** ✅ Yes

### 16.19 Get All Accounts

**Endpoint:** `GET /accounting/account/all`  
**Auth Required:** ❌ No

### 16.20 Cash Book Report

**Endpoint:** `POST /accounting/cash-book-report`  
**Auth Required:** ✅ Yes

**Request Body:**
```json
{
  "start_date": "2025-01-01",
  "end_date": "2025-01-31",
  "id_akun_kas": "uuid-string"
}
```

**Response:**
```json
{
  "status": "success",
  "data": {
    "account_name": "Kas Besar",
    "start_date": "2025-01-01",
    "end_date": "2025-01-31",
    "saldo_awal": 10000000,
    "total_debit": 85000000,
    "total_kredit": 75000000,
    "saldo_akhir": 20000000,
    "transactions": []
  }
}
```

### 16.21 Expense Report

**Endpoint:** `POST /accounting/expense-report`  
**Auth Required:** ✅ Yes

**Request Body:**
```json
{
  "start_date": "2025-01-01",
  "end_date": "2025-01-31"
}
```

### 16.22 Get Bank Codes

**Endpoint:** `GET /accounting/bankcodes`  
**Auth Required:** ❌ No

### 16.23 Get Equity Codes

**Endpoint:** `GET /accounting/equitycodes`  
**Auth Required:** ❌ No

### 16.24 Get Tarik (Withdrawal) Codes

**Endpoint:** `GET /accounting/tarikcodes`  
**Auth Required:** ❌ No

### 16.25 Profit Loss Report

**Endpoint:** `POST /accounting/profit-loss-report`  
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
    "period": "2025-01-01 to 2025-01-31",
    "revenue": {
      "sales": 85000000,
      "services": 45000000,
      "total": 130000000
    },
    "cogs": 55000000,
    "gross_profit": 75000000,
    "expenses": {
      "operational": 12000000,
      "salary": 15000000,
      "total": 27000000
    },
    "net_profit": 48000000
  }
}
```

### 16.26 Cash Report

**Endpoint:** `POST /accounting/cash-report`  
**Auth Required:** ✅ Yes

### 16.27 Receivable & Payable Report

**Endpoint:** `POST /accounting/receivable-payable-report`  
**Auth Required:** ❌ No

**Request Body:**
```json
{
  "as_of_date": "2025-01-31"
}
```

### 16.28 Consignment Payable Report

**Endpoint:** `POST /accounting/consignment-payable-report`  
**Auth Required:** ✅ Yes

### 16.29 Product Sales Report

**Endpoint:** `POST /accounting/product-sales-report`  
**Auth Required:** ✅ Yes

**Request Body:**
```json
{
  "start_date": "2025-01-01",
  "end_date": "2025-01-31",
  "product_id": "uuid-string (optional)",
  "customer_id": "uuid-string (optional)"
}
```

**Response Body:**
```json
{
  "total_quantity": 50,
  "total_sales": 5000000,
  "total_hpp": 3333333.33,
  "items": [
    {
      "workorder_no": "WO001",
      "workorder_date": "2025-01-15",
      "customer_name": "PT Maju Jaya",
      "product_name": "Oli Shell 1L",
      "nopol": "B-1234-ABC",
      "quantity": 5,
      "price": 150000,
      "hpp": 100000,
      "subtotal": 750000,
      "discount": 0
    }
  ]
}
```

**Field Definitions (Summary):**
- `total_quantity` (decimal): Total unit barang yang terjual
- `total_sales` (decimal): Total pendapatan penjualan barang, dihitung dengan `SUM(items[].subtotal)`
- `total_hpp` (decimal): Total harga pokok penjualan, dihitung dengan `SUM(items[].hpp × items[].quantity)`; HPP `null` diperlakukan sebagai nol

Rumus aggregate resmi:

```text
total_sales = SUM(item.subtotal)
total_hpp   = SUM(COALESCE(item.hpp, 0) * item.quantity)
```

**Field Definitions (Items):**
- `workorder_no` (string): Nomor Work Order
- `workorder_date` (date): Tanggal masuk work order
- `customer_name` (string): Nama pelanggan
- `product_name` (string): Nama produk yang dijual
- `nopol` (string, nullable): Nomor polisi kendaraan
- `quantity` (decimal): Jumlah unit barang yang dijual
- `price` (decimal): Harga jual per unit
- `hpp` (decimal, nullable): Harga pokok penjualan (cost) - untuk analisis margin
- `subtotal` (decimal): Total penjualan (quantity × price - discount)
- `discount` (decimal): Jumlah diskon yang diberikan

### 16.30 Service Sales Report

**Endpoint:** `POST /accounting/service-sales-report`  
**Auth Required:** ✅ Yes

**Request Body:**
```json
{
  "start_date": "2025-01-01",
  "end_date": "2025-01-31",
  "service_id": "uuid-string (optional)",
  "customer_id": "uuid-string (optional)"
}
```

**Response Body:**
```json
{
  "total_quantity": 20,
  "total_sales": 8000000,
  "total_hpp": 5000000,
  "items": [
    {
      "workorder_no": "WO002",
      "workorder_date": "2025-01-16",
      "customer_name": "PT Maju Jaya",
      "service_name": "Servis Lengkap",
      "nopol": "B-1234-ABC",
      "quantity": 10,
      "price": 500000,
      "hpp": 250000,
      "subtotal": 5000000,
      "discount": 0
    }
  ]
}
```

**Field Definitions (Summary):**
- `total_quantity` (decimal): Total unit/jam jasa yang terjual
- `total_sales` (decimal): Total pendapatan penjualan jasa (setelah diskon)
- `total_hpp` (decimal): Total harga pokok penjualan (cost × quantity) - untuk perhitungan margin/profit

**Field Definitions (Items):**
- `workorder_no` (string): Nomor Work Order
- `workorder_date` (date): Tanggal masuk work order
- `customer_name` (string): Nama pelanggan
- `service_name` (string): Nama layanan/jasa yang dijual
- `nopol` (string, nullable): Nomor polisi kendaraan
- `quantity` (decimal): Jumlah unit/jam jasa yang dijual
- `price` (decimal): Harga jual per unit
- `hpp` (decimal, nullable): Harga pokok penjualan (cost) - untuk analisis margin
- `subtotal` (decimal): Total penjualan (quantity × price - discount)
- `discount` (decimal): Jumlah diskon yang diberikan

### 16.31 Mechanic Sales Report

**Endpoint:** `POST /accounting/mechanic-sales-report`  
**Auth Required:** ✅ Yes

**Request Body:**
```json
{
  "start_date": "2025-01-01",
  "end_date": "2025-01-31",
  "mekanik_id": "uuid-string"
}
```

### 16.32 Daily Report

**Endpoint:** `POST /accounting/daily-report`  
**Auth Required:** ✅ Yes

**Purpose:** Menyediakan snapshot laporan harian terpadu untuk dashboard/halaman Daily Report frontend dalam satu request.

**Request Body:**
```json
{
  "date": "2025-01-18"
}
```

**Request Validation Rules:**
- `date` wajib diisi.
- Format `date` harus `YYYY-MM-DD`.
- Batas waktu harian dihitung berdasarkan timezone bisnis backend.
- Rekomendasi timezone default: `Asia/Bangkok`.
- Batas hari: dari `YYYY-MM-DDT00:00:00+07:00` sampai sebelum hari berikutnya.

**Response:**
```json
{
  "status": "success",
  "message": "Laporan harian berhasil dihasilkan",
  "data": {
    "date": "2025-01-18",
    "timezone": "Asia/Bangkok",
    "generated_at": "2026-07-12T17:30:00+07:00",
    "work_orders": {
      "total_workorders": 10,
      "total_revenue": 7500000,
      "total_hpp": 4200000,
      "gross_profit": 3300000,
      "items": [
        {
          "workorder_id": "uuid-string",
          "workorder_no": "WO-20250118-001",
          "customer_name": "Budi",
          "total_biaya": 750000,
          "status": "completed",
          "total_revenue": 750000,
          "total_hpp": 420000,
          "gross_profit": 330000,
          "payment_status": "paid"
        }
      ]
    },
    "outflows": {
      "total_cash_out": 2500000,
      "expenses": {
        "total": 500000,
        "items": [
          {
            "expense_id": null,
            "payment_id": "uuid-string",
            "payment_date": "2025-01-18",
            "category": "Biaya Listrik",
            "description": "Pembayaran listrik bulanan",
            "amount": 500000,
            "payment_channel": "bank",
            "account_code": "1002",
            "account_name": "Bank BCA",
            "channel_code": "BANK_1002"
          }
        ]
      },
      "purchase_order_payments": {
        "total": 2000000,
        "items": [
          {
            "purchase_order_id": "uuid-string",
            "purchase_order_no": "PO-20250117-001",
            "payment_id": "uuid-string",
            "payment_date": "2025-01-18",
            "supplier_name": "PT Supplier Jaya",
            "amount_paid": 2000000,
            "payment_channel": "bank",
            "account_code": "1002",
            "account_name": "Bank BCA",
            "channel_code": "BANK_1002"
          }
        ]
      }
    },
    "payment_channels": [
      {
        "code": "CASHIER_CASH",
        "name": "Kas Kasir",
        "type": "cashier_cash",
        "account_code": "1001",
        "opening_balance": 1000000,
        "cash_in": 3500000,
        "cash_out": 500000,
        "closing_balance": 4000000
      },
      {
        "code": "BANK_1002",
        "name": "Bank BCA",
        "type": "bank",
        "account_code": "1002",
        "opening_balance": 10000000,
        "cash_in": 1500000,
        "cash_out": 2000000,
        "closing_balance": 9500000
      },
      {
        "code": "QRIS",
        "name": "QRIS",
        "type": "qris",
        "account_code": "1003",
        "opening_balance": 0,
        "cash_in": 1250000,
        "cash_out": 0,
        "closing_balance": 1250000
      },
      {
        "code": "DEBIT",
        "name": "Debit",
        "type": "debit",
        "account_code": "1004",
        "opening_balance": 0,
        "cash_in": 1000000,
        "cash_out": 0,
        "closing_balance": 1000000
      }
    ],
    "cashier_cash": {
      "code": "CASHIER_CASH",
      "account_code": "1001",
      "account_name": "Kas Kasir",
      "opening_balance": 1000000,
      "cash_in": 3500000,
      "cash_out": 500000,
      "closing_balance": 4000000
    },
    "product_sales": {
      "total_quantity": 15,
      "total_sales": 3750000,
      "total_hpp": 2250000,
      "total_margin": 1500000,
      "margin_percentage": 40,
      "items": []
    },
    "service_sales": {
      "total_quantity": 8,
      "total_sales": 3750000,
      "total_hpp": 1950000,
      "total_margin": 1800000,
      "margin_percentage": 48,
      "items": []
    },
    "purchase_orders": {
      "total_quantity": 0,
      "total_purchases": 0,
      "items": []
    },
    "profit_loss": {
      "total_revenue": 7500000,
      "product_hpp": 2250000,
      "service_hpp": 1950000,
      "total_hpp": 4200000,
      "gross_profit": 3300000,
      "operating_expenses": 500000,
      "total_expenses": 4700000,
      "net_profit": 2800000,
      "revenues": [],
      "expenses": []
    },
    "sales_count": 23,
    "sales_total": 7500000,
    "cash_in": 7250000,
    "cash_out": 2500000,
    "expenses": 500000,
    "net_cash": 4750000,
    "workorders": [
      {
        "workorder_id": "uuid-string",
        "workorder_no": "WO-20250118-001",
        "customer_name": "Budi",
        "total_biaya": 750000,
        "status": "completed",
        "total_revenue": 750000,
        "total_hpp": 420000,
        "gross_profit": 330000,
        "payment_status": "paid"
      }
    ]
  }
}
```

**Calculation Rules:**
- `outflows.total_cash_out = outflows.expenses.total + outflows.purchase_order_payments.total`
- `product_sales.total_margin = product_sales.total_sales - product_sales.total_hpp`
- `service_sales.total_margin = service_sales.total_sales - service_sales.total_hpp`
- `work_orders.gross_profit = work_orders.total_revenue - work_orders.total_hpp`
- `payment_channels[].closing_balance = opening_balance + cash_in - cash_out`
- `profit_loss.total_hpp = profit_loss.product_hpp + profit_loss.service_hpp`
- `profit_loss.gross_profit = profit_loss.total_revenue - profit_loss.total_hpp`
- `profit_loss.net_profit = profit_loss.gross_profit - profit_loss.operating_expenses`
- Pembayaran PO tidak dikurangkan langsung dari `profit_loss.net_profit`.

**Field Definitions (Main):**
- `date` (date): Tanggal laporan harian.
- `timezone` (string): Timezone perhitungan harian.
- `generated_at` (datetime): Waktu report dibuat.
- `work_orders` (object): Aggregate dan daftar WO harian.
- `outflows` (object): Cash-out aktual (biaya + pembayaran PO).
- `payment_channels` (array): Posisi kas per channel dengan tipe stabil.
- `cashier_cash` (object): Ringkasan saldo kas kasir.
- `product_sales` (object): Aggregate dan detail penjualan produk.
- `service_sales` (object): Aggregate dan detail penjualan jasa.
- `purchase_orders` (object): Aggregate pembelian harian.
- `profit_loss` (object): Laba rugi harian.

**Field Definitions (Work Orders):**
- `work_orders.total_workorders` (int): Jumlah work order pada tanggal laporan.
- `work_orders.total_revenue` (decimal): Total revenue WO.
- `work_orders.total_hpp` (decimal): Total HPP WO.
- `work_orders.gross_profit` (decimal): Revenue dikurangi HPP.
- `work_orders.items[].status` (enum): Status proses WO: `draft`, `process`, `completed`, atau `cancelled`.
- `work_orders.items[].payment_status` (enum): Status pembayaran WO: `unpaid`, `partial`, `paid`, atau `refunded`.

**Field Definitions (Outflows):**
- `outflows.total_cash_out` (decimal): Total cash-out aktual.
- `outflows.expenses.total` (decimal): Total biaya yang benar-benar dibayar pada tanggal laporan.
- `outflows.expenses.items[]` (array): Detail pembayaran biaya per jurnal.
- `outflows.purchase_order_payments.total` (decimal): Total pembayaran PO aktual pada tanggal laporan.
- `outflows.purchase_order_payments.items[]` (array): Detail pembayaran PO per jurnal.
- `outflows.expenses.items[].expense_id` (UUID/null): ID master expense; boleh `null` untuk jurnal biaya yang tidak berasal dari master expense.
- `outflows.expenses.items[].payment_id` (UUID): ID journal entry pembayaran yang unik.
- `outflows.expenses.items[].payment_date` (date): Tanggal pembayaran aktual dalam format `YYYY-MM-DD`.
- `outflows.expenses.items[].amount` (decimal): Nominal biaya yang benar-benar dibayar.
- `outflows.expenses.items[].payment_channel` (enum): Tipe channel pembayaran: `cashier_cash`, `bank`, `qris`, `debit`, `petty_cash`, atau `other`.
- `outflows.expenses.items[].channel_code` (string): Identifier channel stabil yang dapat dipetakan ke `payment_channels[].code`.
- `outflows.expenses.items[].account_code` (string): Kode Chart of Account sumber dana.
- `outflows.purchase_order_payments.items[].payment_id` (UUID): ID journal entry pembayaran yang unik.
- `outflows.purchase_order_payments.items[].payment_date` (date): Tanggal pembayaran aktual dalam format `YYYY-MM-DD`.
- `outflows.purchase_order_payments.items[].amount_paid` (decimal): Nominal pembayaran PO pada tanggal laporan.
- `outflows.purchase_order_payments.items[].payment_channel` (enum): Tipe channel pembayaran.
- `outflows.purchase_order_payments.items[].channel_code` (string): Identifier channel stabil yang dapat dipetakan ke `payment_channels[].code`.
- `outflows.purchase_order_payments.items[].account_code` (string): Kode Chart of Account sumber dana.

**Field Definitions (Payment Channels):**
- `payment_channels[].code` (string): Kode channel stabil untuk frontend.
- `payment_channels[].name` (string): Nama akun/channel.
- `payment_channels[].type` (enum): `cashier_cash`, `bank`, `qris`, `debit`, `petty_cash`, `other`.
- `payment_channels[].opening_balance` (decimal): Saldo awal channel.
- `payment_channels[].cash_in` (decimal): Arus masuk channel.
- `payment_channels[].cash_out` (decimal): Arus keluar channel.
- `payment_channels[].closing_balance` (decimal): Saldo akhir channel.

**Field Definitions (Legacy Compatibility):**
- `sales_count` (int): Jumlah item penjualan produk + jasa (legacy).
- `sales_total` (decimal): Total penjualan produk + jasa (legacy).
- `cash_in` (decimal): Total cash-in seluruh channel (legacy).
- `cash_out` (decimal): Total cash-out seluruh channel (legacy).
- `expenses` (decimal): Alias ke `outflows.expenses.total` (legacy).
- `net_cash` (decimal): `cash_in - cash_out` (legacy).
- `workorders` (array): Alias legacy dari `work_orders.items`.

**Empty-State Response Example:**
```json
{
  "status": "success",
  "message": "Laporan harian berhasil dihasilkan",
  "data": {
    "date": "2025-01-18",
    "timezone": "Asia/Bangkok",
    "generated_at": "2026-07-12T17:30:00+07:00",
    "work_orders": {"total_workorders": 0, "total_revenue": 0, "total_hpp": 0, "gross_profit": 0, "items": []},
    "outflows": {"total_cash_out": 0, "expenses": {"total": 0, "items": []}, "purchase_order_payments": {"total": 0, "items": []}},
    "payment_channels": [],
    "cashier_cash": {"code": "CASHIER_CASH", "account_code": "1001", "account_name": "Kas Kasir", "opening_balance": 0, "cash_in": 0, "cash_out": 0, "closing_balance": 0},
    "product_sales": {"total_quantity": 0, "total_sales": 0, "total_hpp": 0, "total_margin": 0, "margin_percentage": 0, "items": []},
    "service_sales": {"total_quantity": 0, "total_sales": 0, "total_hpp": 0, "total_margin": 0, "margin_percentage": 0, "items": []},
    "purchase_orders": {"total_quantity": 0, "total_purchases": 0, "items": []},
    "profit_loss": {"total_revenue": 0, "product_hpp": 0, "service_hpp": 0, "total_hpp": 0, "gross_profit": 0, "operating_expenses": 0, "total_expenses": 0, "net_profit": 0, "revenues": [], "expenses": []},
    "sales_count": 0,
    "sales_total": 0,
    "cash_in": 0,
    "cash_out": 0,
    "expenses": 0,
    "net_cash": 0,
    "workorders": []
  }
}
```

**Frontend Notes:**
- Gunakan `outflows.expenses` untuk daftar biaya harian (cash-out aktual)
- Gunakan `outflows.purchase_order_payments` untuk pembayaran PO aktual
- Gunakan `cashier_cash.closing_balance` untuk kartu "Sisa Cash di Kasir"
- Gunakan `payment_channels[].type` untuk klasifikasi channel, jangan berdasarkan `account_name`

**DailyReport.vue Migration Notes:**
- Ganti sumber kartu biaya dari `profit_loss.expenses` ke `outflows.expenses.total`
- Ganti total pembayaran PO ke `outflows.purchase_order_payments.total`
- Ambil ringkasan kas kasir dari `cashier_cash.closing_balance`
- Gunakan `work_orders.total_workorders`, `work_orders.total_revenue`, `work_orders.gross_profit`
- Simpan fallback ke field legacy sampai deployment frontend selesai

**Excel Export Mapping (Frontend):**
- Sheet `Summary`: `date`, `work_orders.total_workorders`, `work_orders.total_revenue`, `outflows.total_cash_out`, `cashier_cash.closing_balance`, `profit_loss.net_profit`
- Sheet `Work Orders`: `work_orders.items[]`
- Sheet `Outflows Expenses`: `outflows.expenses.items[]`
- Sheet `Outflows PO Payments`: `outflows.purchase_order_payments.items[]`
- Sheet `Payment Channels`: `payment_channels[]`
- Sheet `Product Sales`: `product_sales.items[]`
- Sheet `Service Sales`: `service_sales.items[]`

**Backward Compatibility:**
- Field lama tetap dipertahankan selama masa transisi frontend
- Field baru ditambahkan agar halaman Daily Report frontend bisa migrasi bertahap tanpa breaking change

**Legacy to New Mapping (Recommended):**
- `expenses` -> `outflows.expenses.total`
- `workorders` -> `work_orders.items`
- `cash_out` -> `outflows.total_cash_out` untuk cash-out harian aktual
- `sales_total` -> `work_orders.total_revenue` untuk rekonsiliasi utama

**Error Response (Invalid Date):**
```json
{
  "status": "error",
  "message": "Invalid date format. Expected YYYY-MM-DD"
}
```

**HTTP Status:** `422 Unprocessable Entity`

**Error Response (Unauthorized):**
```json
{
  "status": "error",
  "message": "Authentication required"
}
```

**HTTP Status:** `401 Unauthorized`

---

## 17. WhatsApp Integration

### 17.1 Send WhatsApp Message

**Endpoint:** `POST /whatsapp/send`  
**Auth Required:** ✅ Yes

**Request Body:**
```json
{
  "phone_number": "628123456789",
  "message": "Halo, ini adalah reminder servis kendaraan Anda.",
  "schedule_time": null
}
```

**Response:**
```json
{
  "status": "success",
  "message": "WhatsApp message sent successfully",
  "data": {
    "message_id": "msg-12345",
    "phone_number": "628123456789",
    "status": "sent"
  }
}
```

### 17.2 Send Simple WhatsApp

**Endpoint:** `POST /whatsapp/send-simple`  
**Auth Required:** ❌ No

**Request Body:**
```json
{
  "phone_number": "628123456789",
  "message": "Test message"
}
```

### 17.3 Send WhatsApp with File

**Endpoint:** `POST /whatsapp/send-with-file`  
**Auth Required:** ❌ No

**Request:** Multipart form-data
- `phone_number`: string
- `message`: string
- `file`: File attachment

### 17.4 Send Scheduled WhatsApp

**Endpoint:** `POST /whatsapp/send-scheduled`  
**Auth Required:** ❌ No

**Request Body:**
```json
{
  "phone_number": "628123456789",
  "message": "Scheduled reminder message",
  "schedule_time": "2025-01-20T10:00:00"
}
```

---

## 18. WhatsApp Reports

### 18.1 Get All WhatsApp Reports

**Endpoint:** `GET /whatsapp-report/`  
**Auth Required:** ❌ No

**Query Parameters:**
- `status` (optional): Filter by status (sent, failed, pending)
- `start_date` (optional)
- `end_date` (optional)

**Response:**
```json
{
  "status": "success",
  "data": [
    {
      "id": "uuid-string",
      "customer_name": "John Doe",
      "phone_number": "628123456789",
      "vehicle_nopol": "B 1234 ABC",
      "message": "Reminder servis",
      "sent_at": "2025-01-18T10:30:00",
      "status": "sent"
    }
  ]
}
```

### 18.2 Get WhatsApp Report Detail

**Endpoint:** `GET /whatsapp-report/detail`  
**Auth Required:** ❌ No

### 18.3 Get WhatsApp Statistics

**Endpoint:** `GET /whatsapp-report/statistics`  
**Auth Required:** ❌ No

**Response:**
```json
{
  "status": "success",
  "data": {
    "total_sent": 450,
    "total_failed": 12,
    "total_pending": 5,
    "success_rate": 97.4,
    "this_month": 85,
    "this_week": 23,
    "today": 5
  }
}
```

### 18.4 Get Reports by Customer

**Endpoint:** `GET /whatsapp-report/customer/{id_customer}`  
**Auth Required:** ❌ No

### 18.5 Get Report by Customer and Vehicle

**Endpoint:** `GET /whatsapp-report/customer/{id_customer}/vehicle/{id_vehicle}`  
**Auth Required:** ❌ No

### 18.6 Delete WhatsApp Report

**Endpoint:** `DELETE /whatsapp-report/{report_id}`  
**Auth Required:** ❌ No

### 18.7 Reset Send Frequency

**Endpoint:** `POST /whatsapp-report/reset-frequency`  
**Auth Required:** ❌ No

**Description:** Reset the frequency counter for sending maintenance reminders.

---

## 19. Manual WhatsApp

### 19.1 Create Manual WhatsApp Record

**Endpoint:** `POST /manual-whatsapp/`  
**Auth Required:** ❌ No

**Request Body:**
```json
{
  "nopol": "B 1234 ABC",
  "customer_name": "John Doe",
  "phone_number": "628123456789",
  "vehicle_brand": "Toyota",
  "vehicle_type": "Avanza",
  "last_service_date": "2024-12-18",
  "next_service_date": "2025-03-18",
  "reminder_days_before": 3,
  "is_active": true
}
```

### 19.2 Bulk Import Manual WhatsApp

**Endpoint:** `POST /manual-whatsapp/bulk-import`  
**Auth Required:** ❌ No

**Request:** Multipart form-data
- `file`: CSV file with columns (nopol, customer_name, phone_number, etc.)

### 19.3 Get All Manual WhatsApp Records

**Endpoint:** `GET /manual-whatsapp/`  
**Auth Required:** ❌ No

**Query Parameters:**
- `skip` (default: 0)
- `limit` (default: 100)
- `is_active` (optional): Filter by active status

### 19.4 Get Manual WhatsApp by ID

**Endpoint:** `GET /manual-whatsapp/{record_id}`  
**Auth Required:** ❌ No

### 19.5 Get Manual WhatsApp by Nopol

**Endpoint:** `GET /manual-whatsapp/by-nopol/{nopol}`  
**Auth Required:** ❌ No

### 19.6 Update Manual WhatsApp Record

**Endpoint:** `PUT /manual-whatsapp/{record_id}`  
**Auth Required:** ❌ No

### 19.7 Toggle Active Status

**Endpoint:** `PATCH /manual-whatsapp/{record_id}/toggle-active`  
**Auth Required:** ❌ No

### 19.8 Delete Manual WhatsApp Record

**Endpoint:** `DELETE /manual-whatsapp/{record_id}`  
**Auth Required:** ❌ No

### 19.9 Send All Reminders

**Endpoint:** `POST /manual-whatsapp/send-reminders`  
**Auth Required:** ❌ No

**Description:** Send reminders to all vehicles due for service based on reminder_days_before.

**Response:**
```json
{
  "status": "success",
  "data": {
    "total_checked": 50,
    "reminders_sent": 12,
    "reminders_failed": 1,
    "details": []
  }
}
```

### 19.10 Send Single Reminder

**Endpoint:** `POST /manual-whatsapp/{record_id}/send-reminder`  
**Auth Required:** ❌ No

### 19.11 Send Custom Message

**Endpoint:** `POST /manual-whatsapp/send-custom-message`  
**Auth Required:** ❌ No

**Request Body:**
```json
{
  "record_ids": ["uuid-1", "uuid-2"],
  "message": "Custom reminder message for your vehicle service"
}
```

### 19.12 Get Statistics Summary

**Endpoint:** `GET /manual-whatsapp/stats/summary`  
**Auth Required:** ❌ No

**Response:**
```json
{
  "status": "success",
  "data": {
    "total_records": 120,
    "active_records": 115,
    "inactive_records": 5,
    "due_for_service_this_week": 8,
    "due_for_service_this_month": 25,
    "overdue": 3
  }
}
```

---

## 20. Scheduler

### 20.1 Start Maintenance Reminder Scheduler

**Endpoint:** `POST /scheduler/maintenance-reminder/start`  
**Auth Required:** ✅ Yes

**Request Body:**
```json
{
  "hour": 7,
  "minute": 0
}
```

**Response:**
```json
{
  "status": "success",
  "message": "Maintenance reminder scheduler started",
  "data": {
    "schedule": "Every day at 07:00",
    "status": "running"
  }
}
```

### 20.2 Stop Maintenance Reminder Scheduler

**Endpoint:** `POST /scheduler/maintenance-reminder/stop`  
**Auth Required:** ✅ Yes

### 20.3 Get Scheduler Status

**Endpoint:** `GET /scheduler/maintenance-reminder/status`  
**Auth Required:** ✅ Yes

**Response:**
```json
{
  "status": "success",
  "data": {
    "is_running": true,
    "schedule": "Every day at 07:00",
    "last_run": "2025-01-18T07:00:00",
    "next_run": "2025-01-19T07:00:00"
  }
}
```

### 20.4 Run Scheduler Now

**Endpoint:** `POST /scheduler/maintenance-reminder/run-now`  
**Auth Required:** ✅ Yes

**Description:** Manually trigger the maintenance reminder scheduler immediately.

---

## 21. Packet Orders

### 21.1 Create Packet Order

**Endpoint:** `POST /packetorders/create/new`  
**Auth Required:** ✅ Yes

**Request Body:**
```json
{
  "name": "Paket Servis Lengkap",
  "product_line_packet_order": [
    {
      "product_id": "uuid-string",
      "quantity": 4,
      "price": 75000,
      "satuan_id": "uuid-string",
      "discount": 0,
      "subtotal": 300000
    }
  ],
  "service_line_packet_order": [
    {
      "service_id": "uuid-string",
      "quantity": 1,
      "price": 200000,
      "discount": 0,
      "subtotal": 200000
    }
  ]
}
```

### 21.2 Get All Packet Orders

**Endpoint:** `GET /packetorders/all`  
**Auth Required:** ❌ No

### 21.3 Get Packet Order by ID

**Endpoint:** `GET /packetorders/{packet_id}`  
**Auth Required:** ❌ No

### 21.4 Update Packet Order

**Endpoint:** `PUT /packetorders/{packet_id}`  
**Auth Required:** ✅ Yes

**Path Parameters:**
- `packet_id` (string): UUID packet order

**Request Body:** Same as Create Packet Order

### 21.5 Delete Packet Order

**Endpoint:** `DELETE /packetorders/{packet_id}`  
**Auth Required:** ✅ Yes

---

## 📊 Common HTTP Status Codes

- **200 OK**: Request successful
- **201 Created**: Resource created successfully
- **204 No Content**: Request successful, no content to return
- **400 Bad Request**: Invalid request format or parameters
- **401 Unauthorized**: Authentication required or token invalid
- **403 Forbidden**: Insufficient permissions
- **404 Not Found**: Resource not found
- **500 Internal Server Error**: Server error

---

## 🔒 Security Notes

1. **JWT Tokens expire after 12 hours** - Obtain a new token by logging in again
2. Store tokens securely in your client application
3. Never expose your API keys or tokens in public repositories
4. Use HTTPS in production environments
5. WhatsApp API key should be kept in `.env` file: `STARSENDER_API_KEY`

---

## 📝 Additional Notes

### CORS Configuration

The API accepts requests from:
- `http://localhost:*` (any port during development)
- `http://127.0.0.1:*` (any port during development)
- `https://carspeed.gagakrimang.web.id` (production)

### File Uploads

Endpoints that accept file uploads use `multipart/form-data`:
- Maximum file size: Configured in server
- Supported formats: Images (jpg, png, pdf) for proof of payment/receipts

### Date Format

- Date fields use: `YYYY-MM-DD` (e.g., `2025-01-18`)
- DateTime fields use ISO 8601: `YYYY-MM-DDTHH:mm:ss` (e.g., `2025-01-18T10:30:00`)

### Pagination

Some list endpoints support pagination:
- `skip`: Number of records to skip (default: 0)
- `limit`: Maximum records to return (default: 100)

---

## 🎯 Quick Start Examples

### Login and Get Token
```bash
curl -X POST http://localhost:8000/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"password123"}'
```

### Use Token in Subsequent Requests
```bash
curl -X GET http://localhost:8000/dashboard/summary \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"
```

### Create Work Order
```bash
curl -X POST http://localhost:8000/workorders/create/new \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "customer_id":"uuid-here",
    "vehicle_id":"uuid-here",
    "tanggal_masuk":"2025-01-18",
    "keluhan":"Ganti oli"
  }'
```

---

**For more detailed information about specific features:**
- Dashboard: See `DASHBOARD_DOCUMENTATION.md`
- WhatsApp Integration: See `WHATSAPP_API_DOCUMENTATION.md`
- Manual WhatsApp: See `MANUAL_WHATSAPP_DOCUMENTATION.md`
- Authentication & Roles: See `LOGIN_WITH_ROLES_DOCUMENTATION.md`
- Services: See `SERVICE_DOCUMENTATION.md`

---

**Last Updated:** July 12, 2026  
**Maintained by:** FastAPI Bengkel Team
