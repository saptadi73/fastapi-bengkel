# WhatsApp Report Tracking - Dokumentasi Lengkap

## Daftar Isi
- [Ringkasan](#ringkasan)
- [Setup Database](#setup-database)
- [Arsitektur](#arsitektur)
- [API Endpoints](#api-endpoints)
- [Cara Penggunaan](#cara-penggunaan)
- [Contoh Response](#contoh-response)

---

## Ringkasan

WhatsApp Report adalah fitur untuk tracking pengiriman pesan WhatsApp kepada setiap kombinasi customer dan vehicle. Fitur ini otomatis mencatat setiap pesan yang berhasil terkirim melalui scheduler maintenance reminder.

**Fitur Utama:**
- ✅ Auto tracking setiap pengiriman WhatsApp ke customer+vehicle
- ✅ Update frequency (berapa kali sudah dikirim) dan tanggal pengiriman terakhir
- ✅ Statistik menyeluruh (total pesan, average per customer, breakdown by frequency)
- ✅ Detail report dengan informasi customer dan vehicle
- ✅ Reset frequency untuk analisis berkala
- ✅ Integrasi seamless dengan existing WhatsApp scheduler

**Data yang Dicatat:**
```
whatsapp_report table
├── id: UUID (primary key)
├── id_customer: UUID (foreign key ke customer)
├── id_vehicle: UUID (foreign key ke vehicle)
├── last_message_date: DateTime (kapan pesan terakhir dikirim)
├── frequency: Integer (total berapa kali pesan dikirim)
├── created_at: DateTime (kapan record dibuat)
└── updated_at: DateTime (kapan record terakhir diupdate)
```

---

## Setup Database

### 1. Buat Table

```bash
cd c:\projek\fastapi-bengkel
python database/create_whatsapp_report_table.py
```

**Output yang diharapkan:**
```
✓ Table 'whatsapp_report' created successfully

Columns:
  - id: UUID
  - id_customer: UUID
  - id_vehicle: UUID
  - last_message_date: DATETIME
  - frequency: INTEGER
  - created_at: DATETIME
  - updated_at: DATETIME
```

---

## Arsitektur

### Flow Diagram

```
┌────────────────────────────────────┐
│ Scheduler (APScheduler)            │
│ maintenance_reminder_job()         │
└─────────────┬──────────────────────┘
              │
              ▼
┌────────────────────────────────────────┐
│ Service: services_customer.py          │
│ send_maintenance_reminder_whatsapp()   │
│                                        │
│ 1. Get list customers with vehicles    │
│ 2. Check maintenance dates             │
│ 3. Send WhatsApp message               │
│ 4. Update whatsapp_report tracking ◄── NEW
└────────────────────────────────────────┘
              │
              ▼
┌────────────────────────────────────────┐
│ Service: services_whatsapp_report.py   │
│ create_or_update_whatsapp_report()     │
│                                        │
│ - Check existing record (cust+vehicle) │
│ - Create or update frequency           │
│ - Update last_message_date             │
└────────────────────────────────────────┘
              │
              ▼
┌────────────────────────────────────────┐
│ Database: whatsapp_report table        │
│ Auto-updated setiap pesan terkirim     │
└────────────────────────────────────────┘
```

### Komponen

#### 1. **Model** (`models/whatsapp_report.py`)
```python
class WhatsappReport(Base):
    __tablename__ = 'whatsapp_report'
    
    id: UUID (primary key)
    id_customer: UUID (FK → customer.id)
    id_vehicle: UUID (FK → vehicle.id)
    last_message_date: DateTime
    frequency: Integer
    created_at: DateTime
    updated_at: DateTime
```

#### 2. **Schema** (`schemas/whatsapp_report.py`)
- `WhatsappReportResponse`: Response minimal dengan basic info
- `WhatsappReportDetail`: Response dengan customer & vehicle info lengkap
- `WhatsappReportStatistics`: Statistik agregat

#### 3. **Service** (`services/services_whatsapp_report.py`)
Fungsi utama:
- `create_or_update_whatsapp_report()`: Create atau update record saat pesan terkirim
- `get_all_whatsapp_reports()`: Get semua reports
- `get_whatsapp_report_by_customer_vehicle()`: Get report spesifik customer+vehicle
- `get_whatsapp_reports_by_customer()`: Get semua reports untuk customer
- `get_whatsapp_report_details()`: Get reports dengan detail lengkap
- `get_whatsapp_report_statistics()`: Get statistik agregat
- `delete_whatsapp_report()`: Hapus report
- `reset_frequency()`: Reset frequency untuk analysis berkala

#### 4. **Route** (`routes/routes_whatsapp_report.py`)
Endpoint untuk akses tracking dan statistik

#### 5. **Scheduler Integration** (`services/services_customer.py`)
Fungsi `send_maintenance_reminder_whatsapp()` sudah diupdate untuk:
- Memanggil `create_or_update_whatsapp_report()` setiap kali pesan terkirim
- Handle error gracefully (tidak stop pengiriman jika error update report)

---

## API Endpoints

### 1. **List semua reports (minimal format)**
```http
GET /whatsapp-report/
```

**Response:**
```json
[
  {
    "id": "550e8400-e29b-41d4-a716-446655440000",
    "id_customer": "6ba7b810-9dad-11d1-80b4-00c04fd430c8",
    "id_vehicle": "6ba7b811-9dad-11d1-80b4-00c04fd430c8",
    "last_message_date": "2026-01-05T10:30:00",
    "frequency": 5,
    "created_at": "2025-12-20T08:00:00",
    "updated_at": "2026-01-05T10:30:00"
  }
]
```

---

### 2. **List reports dengan detail lengkap**
```http
GET /whatsapp-report/detail
```

**Response:**
```json
[
  {
    "id": "550e8400-e29b-41d4-a716-446655440000",
    "customer_name": "Budi Santoso",
    "customer_phone": "6281234567890",
    "vehicle_model": "Avanza",
    "vehicle_nopol": "B 1234 CD",
    "last_message_date": "2026-01-05T10:30:00",
    "frequency": 5,
    "created_at": "2025-12-20T08:00:00",
    "updated_at": "2026-01-05T10:30:00"
  }
]
```

---

### 3. **Get statistik WhatsApp reports**
```http
GET /whatsapp-report/statistics
```

**Response:**
```json
{
  "total_customers_with_vehicles": 45,
  "total_messages_sent": 182,
  "average_messages_per_customer": 4.04,
  "customers_by_frequency": {
    "1": 10,
    "2": 15,
    "3": 12,
    "5": 8
  }
}
```

**Penjelasan:**
- `total_customers_with_vehicles`: Jumlah unique kombinasi customer+vehicle yang pernah dikirim pesan
- `total_messages_sent`: Total pesan yang terkirim (sum of all frequency)
- `average_messages_per_customer`: Rata-rata pesan per kombinasi customer+vehicle
- `customers_by_frequency`: Breakdown berapa customer+vehicle yang mendapat pesan 1x, 2x, 3x, dst

---

### 4. **Get reports untuk customer tertentu**
```http
GET /whatsapp-report/customer/{id_customer}
```

**Contoh:**
```http
GET /whatsapp-report/customer/6ba7b810-9dad-11d1-80b4-00c04fd430c8
```

**Response:**
```json
[
  {
    "id": "550e8400-e29b-41d4-a716-446655440000",
    "id_customer": "6ba7b810-9dad-11d1-80b4-00c04fd430c8",
    "id_vehicle": "6ba7b811-9dad-11d1-80b4-00c04fd430c8",
    "last_message_date": "2026-01-05T10:30:00",
    "frequency": 5,
    "created_at": "2025-12-20T08:00:00",
    "updated_at": "2026-01-05T10:30:00"
  }
]
```

---

### 5. **Get report untuk customer + vehicle tertentu**
```http
GET /whatsapp-report/customer/{id_customer}/vehicle/{id_vehicle}
```

**Contoh:**
```http
GET /whatsapp-report/customer/6ba7b810-9dad-11d1-80b4-00c04fd430c8/vehicle/6ba7b811-9dad-11d1-80b4-00c04fd430c8
```

**Response:**
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "id_customer": "6ba7b810-9dad-11d1-80b4-00c04fd430c8",
  "id_vehicle": "6ba7b811-9dad-11d1-80b4-00c04fd430c8",
  "last_message_date": "2026-01-05T10:30:00",
  "frequency": 5,
  "created_at": "2025-12-20T08:00:00",
  "updated_at": "2026-01-05T10:30:00"
}
```

---

### 6. **Delete report**
```http
DELETE /whatsapp-report/{report_id}
```

**Contoh:**
```http
DELETE /whatsapp-report/550e8400-e29b-41d4-a716-446655440000
```

**Response:**
```json
{
  "message": "Report berhasil dihapus"
}
```

---

### 7. **Reset frequency**
```http
POST /whatsapp-report/reset-frequency
```

**Query Parameters:**
- `id_customer` (optional): UUID customer. Jika tidak diberikan, reset semua.

**Contoh 1 - Reset untuk customer tertentu:**
```http
POST /whatsapp-report/reset-frequency?id_customer=6ba7b810-9dad-11d1-80b4-00c04fd430c8
```

**Contoh 2 - Reset semua:**
```http
POST /whatsapp-report/reset-frequency
```

**Response:**
```json
{
  "message": "Frequency untuk 5 report customer 6ba7b810-9dad-11d1-80b4-00c04fd430c8 berhasil direset",
  "count": 5
}
```

---

## Cara Penggunaan

### Scenario 1: Monitor Total Pesan WhatsApp yang Terkirim

```bash
# Get statistik keseluruhan
curl -X GET "http://localhost:8000/whatsapp-report/statistics"
```

Hasil:
- Tahu berapa total pesan yang sudah dikirim ke semua customer
- Tahu rata-rata berapa pesan per customer
- Tahu breakdown customer berdasarkan frequency

---

### Scenario 2: Lihat Detail Customer + Vehicle yang Pernah Dikirim

```bash
# Get detail reports dengan nama customer dan vehicle info
curl -X GET "http://localhost:8000/whatsapp-report/detail"
```

Hasil:
- Lihat nama customer, nomor HP, model vehicle, no pol
- Tahu kapan terakhir dikirim pesan
- Tahu berapa kali sudah dikirim

---

### Scenario 3: Cek Pengiriman untuk Customer Spesifik

```bash
# Get semua pengiriman untuk customer tertentu
curl -X GET "http://localhost:8000/whatsapp-report/customer/6ba7b810-9dad-11d1-80b4-00c04fd430c8"
```

Hasil:
- Lihat semua vehicle customer ini yang pernah dikirim pesan
- Tahu frequency dan last sent date untuk masing-masing vehicle

---

### Scenario 4: Reset Frequency untuk Analisis Bulanan

```bash
# Reset frequency untuk semua (mulai hitungan baru bulan ini)
curl -X POST "http://localhost:8000/whatsapp-report/reset-frequency"
```

Atau reset untuk customer tertentu saja:
```bash
curl -X POST "http://localhost:8000/whatsapp-report/reset-frequency?id_customer=6ba7b810-9dad-11d1-80b4-00c04fd430c8"
```

---

## Contoh Response

### Statistik Lengkap
```json
{
  "total_customers_with_vehicles": 125,
  "total_messages_sent": 487,
  "average_messages_per_customer": 3.9,
  "customers_by_frequency": {
    "1": 25,
    "2": 30,
    "3": 35,
    "4": 25,
    "5": 10
  }
}
```

Interpretasi:
- 125 kombinasi customer+vehicle pernah dikirim pesan
- Total 487 pesan terkirim
- Rata-rata setiap customer+vehicle mendapat ~4 pesan
- 25 customer+vehicle mendapat 1 pesan, 30 mendapat 2 pesan, dst

---

## Integration dengan Scheduler

Tracking otomatis terjadi di fungsi `send_maintenance_reminder_whatsapp()`:

```python
# Setiap kali pesan WhatsApp berhasil terkirim:
if customer_id and vehicle_id:
    try:
        # Otomatis update/create whatsapp_report
        create_or_update_whatsapp_report(db, customer_id, vehicle_id)
    except Exception as report_error:
        # Log warning tapi tetap lanjut pengiriman
        logger.warning(f"Error updating report: {str(report_error)}")
```

**Keuntungan:**
- Otomatis tracking tanpa perlu manual
- Error handling yang baik (tidak stop pengiriman)
- Data selalu up-to-date

---

## Database Query Examples

### Direct SQL Queries

Jika ingin query langsung ke database:

```sql
-- Total pesan per customer+vehicle
SELECT id_customer, id_vehicle, frequency, last_message_date 
FROM whatsapp_report 
ORDER BY frequency DESC 
LIMIT 10;

-- Customer dengan pesan terbanyak
SELECT wr.id_customer, c.nama, COUNT(*) as vehicle_count, SUM(wr.frequency) as total_messages
FROM whatsapp_report wr
JOIN customer c ON wr.id_customer = c.id
GROUP BY wr.id_customer, c.nama
ORDER BY total_messages DESC;

-- Vehicle yang belum pernah dikirim pesan
SELECT v.id, v.no_pol, v.customer_id
FROM vehicle v
LEFT JOIN whatsapp_report wr ON v.id = wr.id_vehicle
WHERE wr.id IS NULL;

-- Last 10 pesan yang terkirim
SELECT wr.id, c.nama, v.no_pol, wr.last_message_date, wr.frequency
FROM whatsapp_report wr
JOIN customer c ON wr.id_customer = c.id
JOIN vehicle v ON wr.id_vehicle = v.id
ORDER BY wr.last_message_date DESC
LIMIT 10;
```

---

## Notes & Best Practices

1. **Frequency Reset:** Reset frequency setiap bulan untuk tracking bulanan yang akurat
2. **Error Handling:** Report tracking tidak akan stop pengiriman pesan (graceful degradation)
3. **Performance:** Gunakan index pada `id_customer` dan `id_vehicle` untuk query yang cepat
4. **Backup:** Jangan lupa backup database sebelum reset frequency bulk
5. **Monitoring:** Gunakan endpoint `/whatsapp-report/statistics` untuk monitoring kesehatan pengiriman

---

## File Structure

```
project/
├── models/
│   └── whatsapp_report.py          # SQLAlchemy model
├── schemas/
│   └── whatsapp_report.py          # Pydantic schemas
├── services/
│   ├── services_whatsapp_report.py # Business logic
│   └── services_customer.py        # Modified untuk track reporting
├── routes/
│   └── routes_whatsapp_report.py   # API endpoints
├── database/
│   └── create_whatsapp_report_table.py  # Table creation script
└── main.py                         # Routes otomatis di-include
```

---

## Troubleshooting

### Issue: Table tidak terbuat
**Solusi:** Run script create_whatsapp_report_table.py dengan venv yang aktif

### Issue: Report tracking tidak berjalan
**Solusi:** Pastikan scheduler sudah running (`/scheduler/maintenance-reminder/start`)

### Issue: Performance lambat saat query
**Solusi:** Buat index: `CREATE INDEX idx_whatsapp_report_customer ON whatsapp_report(id_customer);`
