# Perbaikan Laporan Penjualan (Sales Report)

## Ringkasan Perubahan
Telah ditambahkan kolom-kolom berikut pada laporan penjualan jasa dan barang:
- **No. Polisi (NOPOL)**: Nomor plat kendaraan dari tabel vehicle
- **Harga Jual (Price)**: Harga penjualan per item (sudah ada sebelumnya)
- **Harga Beli/HPP (Cost)**: Harga pokok penjualan dari product atau service

---

## Perubahan Laporan Penjualan Barang (Product Sales Report)

### Endpoint
`POST /accounting/product-sales-report`

### Schema Baru - ProductSalesReportItem
```python
class ProductSalesReportItem(DecimalModel):
    workorder_no: str           # Nomor Work Order
    workorder_date: date        # Tanggal masuk WO
    customer_name: str          # Nama pelanggan
    product_name: str           # Nama produk
    nopol: Optional[str]        # ✨ BARU: No. Polisi kendaraan
    quantity: Decimal           # Jumlah barang
    price: Decimal              # Harga jual per unit
    hpp: Optional[Decimal]      # ✨ BARU: Harga pokok penjualan (cost)
    subtotal: Decimal           # Total penjualan (setelah diskon)
    discount: Decimal           # Diskon
```

### Perubahan Service
- Query sekarang include join ke tabel `Vehicle` untuk mendapatkan `no_pol`
- Query sekarang include `Product.cost` untuk mendapatkan nilai HPP
- Menggunakan `outerjoin` untuk Vehicle supaya tidak ada baris yang hilang jika vehicle_id NULL

**File yang berubah**: [services/services_accounting.py](services/services_accounting.py#L1673-L1731)

---

## Perubahan Laporan Penjualan Jasa (Service Sales Report)

### Endpoint
`POST /accounting/service-sales-report`

### Schema Baru - ServiceSalesReportItem
```python
class ServiceSalesReportItem(DecimalModel):
    workorder_no: str           # Nomor Work Order
    workorder_date: date        # Tanggal masuk WO
    customer_name: str          # Nama pelanggan
    service_name: str           # Nama jasa/service
    nopol: Optional[str]        # ✨ BARU: No. Polisi kendaraan
    quantity: Decimal           # Jumlah jam/unit jasa
    price: Decimal              # Harga jual per unit
    hpp: Optional[Decimal]      # ✨ BARU: Harga pokok penjualan (cost)
    subtotal: Decimal           # Total penjualan (setelah diskon)
    discount: Decimal           # Diskon
```

### Perubahan Service
- Query sekarang include join ke tabel `Vehicle` untuk mendapatkan `no_pol`
- Query sekarang include `Service.cost` untuk mendapatkan nilai HPP
- Menggunakan `outerjoin` untuk Vehicle supaya tidak ada baris yang hilang jika vehicle_id NULL

**File yang berubah**: [services/services_accounting.py](services/services_accounting.py#L1738-L1804)

---

## Struktur Data Terkait

### Vehicle Model (models/customer.py)
Kolom penting untuk report:
- `id`: UUID (primary key)
- `no_pol`: String (nomor polisi)

### Product Model (models/workorder.py)
Kolom penting untuk report:
- `id`: UUID (primary key)
- `name`: String (nama produk)
- `price`: Numeric (harga jual default)
- `cost`: Numeric (harga pokok penjualan)

### Service Model (models/workorder.py)
Kolom penting untuk report:
- `id`: UUID (primary key)
- `name`: String (nama service)
- `price`: String (harga jual)
- `cost`: Numeric (harga pokok penjualan)

### Workorder Model (models/workorder.py)
Kolom yang digunakan:
- `id`: UUID (primary key)
- `no_wo`: String (nomor work order)
- `tanggal_masuk`: DateTime (tanggal masuk)
- `customer_id`: UUID (FK ke customer)
- `vehicle_id`: UUID (FK ke vehicle) ← Digunakan untuk join

---

## Contoh Response Sebelum dan Sesudah

### Response Product Sales Report (Sebagian)
```json
{
  "total_quantity": 10,
  "total_sales": 5000000,
  "items": [
    {
      "workorder_no": "WO001",
      "workorder_date": "2024-01-15",
      "customer_name": "PT Maju Jaya",
      "product_name": "Oli Shell",
      "nopol": "B-1234-ABC",        // ✨ BARU
      "quantity": 5,
      "price": 150000,
      "hpp": 100000,                // ✨ BARU
      "subtotal": 750000,
      "discount": 0
    }
  ]
}
```

### Response Service Sales Report (Sebagian)
```json
{
  "total_quantity": 20,
  "total_sales": 8000000,
  "items": [
    {
      "workorder_no": "WO002",
      "workorder_date": "2024-01-16",
      "customer_name": "PT Maju Jaya",
      "service_name": "Servis Lengkap",
      "nopol": "B-1234-ABC",        // ✨ BARU
      "quantity": 10,
      "price": 500000,
      "hpp": 250000,                // ✨ BARU
      "subtotal": 5000000,
      "discount": 0
    }
  ]
}
```

---

## Testing

Untuk menguji perubahan ini, Anda bisa:

1. **Direct API Test**
   ```bash
   curl -X POST "http://localhost:8000/accounting/product-sales-report" \
     -H "Authorization: Bearer YOUR_JWT_TOKEN" \
     -H "Content-Type: application/json" \
     -d '{
       "start_date": "2024-01-01",
       "end_date": "2024-01-31"
     }'
   ```

2. **Menggunakan pytest**
   ```bash
   pytest test_service_sales_report.py -v
   pytest test_mechanic_sales_report.py -v
   ```

3. **Manual Testing dengan Python**
   ```python
   from datetime import date
   from schemas.service_accounting import ProductSalesReportRequest
   from services.services_accounting import generate_product_sales_report
   
   request = ProductSalesReportRequest(
       start_date=date(2024, 1, 1),
       end_date=date(2024, 1, 31)
   )
   report = generate_product_sales_report(db, request)
   ```

---

## Notes

- ✨ Kolom baru `nopol` dan `hpp` adalah **optional** untuk backward compatibility
- Jika vehicle tidak ada (vehicle_id NULL), `nopol` akan bernilai `NULL`
- Jika product/service tidak memiliki cost, `hpp` akan bernilai `NULL`
- Semua nilai sudah menggunakan Decimal untuk precision finansial yang tepat

---

## Hubungan Database

```
ProductOrdered
├── product_id → Product (name, cost) ✨ hpp dari sini
├── workorder_id → Workorder (no_wo, tanggal_masuk, customer_id)
│   ├── customer_id → Customer (nama)
│   └── vehicle_id → Vehicle (no_pol) ✨ nopol dari sini
└── quantity, price, subtotal, discount

ServiceOrdered
├── service_id → Service (name, cost) ✨ hpp dari sini
├── workorder_id → Workorder (no_wo, tanggal_masuk, customer_id)
│   ├── customer_id → Customer (nama)
│   └── vehicle_id → Vehicle (no_pol) ✨ nopol dari sini
└── quantity, price, subtotal, discount
```

---

**Last Updated**: 2024-01-15
**Status**: ✅ Implementasi Selesai
