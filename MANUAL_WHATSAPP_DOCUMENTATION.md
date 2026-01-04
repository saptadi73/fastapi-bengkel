# Dokumentasi Manual WhatsApp - FastAPI Bengkel

## Daftar Isi
- [Ringkasan](#ringkasan)
- [Setup Database](#setup-database)
- [Architecture](#architecture)
- [API Endpoints](#api-endpoints)
- [Schemas](#schemas)
- [Service Functions](#service-functions)
- [Contoh Penggunaan](#contoh-penggunaan)
- [Integrasi dengan Existing System](#integrasi-dengan-existing-system)

---

## Ringkasan

Sistem Manual WhatsApp adalah fitur untuk mengirim reminder WhatsApp ke customer yang **belum terintegrasi dengan sistem customer utama**. 

**Use Cases:**
- Customer yang nomor polisinya tidak ada dalam database utama
- Customer walk-in yang ingin dikirimi reminder
- Customer dari partner workshop lain
- Customer yang data lengkapnya tidak lengkap di sistem utama

**Features:**
- ✅ Table terpisah `manual_whatsapp` untuk customer manual
- ✅ CRUD operations lengkap (Create, Read, Update, Delete)
- ✅ Phone number normalization otomatis (08xxx → 62xxx)
- ✅ Bulk import untuk banyak customer sekaligus
- ✅ Pengiriman reminder WhatsApp otomatis/manual
- ✅ **Pengiriman custom message ke nomor manapun (tanpa database)**
- ✅ Tracking reminder (berapa kali sudah dikirim, terakhir kapan)
- ✅ Status aktif/tidak aktif per customer
- ✅ Statistics dan reporting

---

## Setup Database

### 1. Buat Table

```bash
cd c:\projek\fastapi-bengkel
python database/create_manual_whatsapp_table.py
```

**Output yang diharapkan:**
```
✓ Table 'manual_whatsapp' created successfully

Columns:
  - id: VARCHAR(36)
  - customer_name: VARCHAR(255)
  - nopol: VARCHAR(20)
  - no_hp: VARCHAR(20)
  - last_service: DATE
  - next_service: DATE
  - is_active: INTEGER
  - reminder_sent_count: INTEGER
  - last_reminder_sent: DATETIME
  - notes: VARCHAR(500)
  - created_at: DATETIME
  - updated_at: DATETIME
```

### 2. Register Model di Database

Edit `models/database.py` dan pastikan import:
```python
from models.manual_whatsapp import ManualWhatsApp
```

---

## Architecture

### Data Model

```
manual_whatsapp
├── id (UUID, PK)
├── customer_name (String, required)
├── nopol (String, unique, required)
├── no_hp (String, required)
├── last_service (Date)
├── next_service (Date)
├── is_active (Integer: 1=active, 0=inactive)
├── reminder_sent_count (Integer, tracking)
├── last_reminder_sent (DateTime, tracking)
├── notes (String, optional)
├── created_at (DateTime)
└── updated_at (DateTime)
```

### Service Layer Architecture

```
┌─────────────────────────────────────────┐
│   Routes (routes_manual_whatsapp.py)    │
└────────────┬────────────────────────────┘
             │
┌────────────▼────────────────────────────┐
│ Services (services_manual_whatsapp.py)  │
│                                         │
│ - CRUD Operations                       │
│ - Phone Normalization                   │
│ - Reminder Logic                        │
│ - Bulk Import                           │
└────────────┬────────────────────────────┘
             │
┌────────────▼────────────────────────────┐
│  Models (models/manual_whatsapp.py)     │
│  Schemas (schemas/manual_whatsapp.py)   │
└─────────────────────────────────────────┘
             │
┌────────────▼────────────────────────────┐
│  WhatsApp Service                       │
│  (services/services_whatsapp.py)        │
│                                         │
│  - send_whatsapp_message_sync()         │
└─────────────────────────────────────────┘
             │
┌────────────▼────────────────────────────┐
│  StarSender API Gateway                 │
│  https://api.starsender.online/api/send │
└─────────────────────────────────────────┘
```

---

## API Endpoints

### Base URL
```
POST/GET/PUT/DELETE /manual-whatsapp
```

**Authentication**: ✅ Semua endpoint memerlukan JWT Token

### Summary Endpoint
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/manual-whatsapp/` | Create record baru |
| POST | `/manual-whatsapp/bulk-import` | Bulk import banyak records |
| GET | `/manual-whatsapp/` | Get semua records |
| GET | `/manual-whatsapp/{record_id}` | Get by ID |
| GET | `/manual-whatsapp/by-nopol/{nopol}` | Get by nopol |
| PUT | `/manual-whatsapp/{record_id}` | Update record |
| PATCH | `/manual-whatsapp/{record_id}/toggle-active` | Toggle active status |
| DELETE | `/manual-whatsapp/{record_id}` | Delete record |
| POST | `/manual-whatsapp/send-reminders` | Bulk send reminders |
| POST | `/manual-whatsapp/{record_id}/send-reminder` | Send reminder to specific customer |
| **POST** | **`/manual-whatsapp/send-custom-message`** | **Send custom message (NEW)** |
| GET | `/manual-whatsapp/stats/summary` | Get statistics |

---

### 1. CREATE - POST `/manual-whatsapp/`

Buat record manual WhatsApp baru untuk satu customer.

**Request Body:**
```json
{
  "customer_name": "Bapak Joko",
  "nopol": "B 1234 XYZ",
  "no_hp": "08123456789",
  "last_service": "2025-10-15",
  "next_service": "2026-01-15",
  "notes": "Customer VIP"
}
```

**Response (201 Created):**
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "customer_name": "Bapak Joko",
  "nopol": "B 1234 XYZ",
  "no_hp": "628123456789",
  "last_service": "2025-10-15",
  "next_service": "2026-01-15",
  "is_active": 1,
  "reminder_sent_count": 0,
  "last_reminder_sent": null,
  "notes": "Customer VIP",
  "created_at": "2026-01-03T10:30:00",
  "updated_at": "2026-01-03T10:30:00"
}
```

**Example cURL:**
```bash
curl -X POST "http://localhost:8000/manual-whatsapp/" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "customer_name": "Bapak Joko",
    "nopol": "B 1234 XYZ",
    "no_hp": "08123456789",
    "next_service": "2026-01-15"
  }'
```

---

### 2. BULK IMPORT - POST `/manual-whatsapp/bulk-import`

Import banyak customer sekaligus.

**Request Body:**
```json
[
  {
    "customer_name": "Bapak Joko",
    "nopol": "B 1234 XYZ",
    "no_hp": "08123456789",
    "next_service": "2026-01-15"
  },
  {
    "customer_name": "Ibu Siti",
    "nopol": "B 5678 ABC",
    "no_hp": "08987654321",
    "next_service": "2026-01-20"
  },
  {
    "customer_name": "Pak Budi",
    "nopol": "B 9999 DEF",
    "no_hp": "08555123456",
    "next_service": "2026-01-25"
  }
]
```

**Response:**
```json
{
  "success": true,
  "data": {
    "total": 3,
    "imported": 3,
    "failed": 0,
    "failures": []
  },
  "message": "Import selesai. 3 berhasil, 0 gagal"
}
```

**Example Python:**
```python
import requests
import json

data = [
    {
        "customer_name": "Bapak Joko",
        "nopol": "B 1234 XYZ",
        "no_hp": "08123456789",
        "next_service": "2026-01-15"
    },
    {
        "customer_name": "Ibu Siti",
        "nopol": "B 5678 ABC",
        "no_hp": "08987654321",
        "next_service": "2026-01-20"
    }
]

headers = {
    'Authorization': 'Bearer YOUR_JWT_TOKEN',
    'Content-Type': 'application/json'
}

response = requests.post(
    'http://localhost:8000/manual-whatsapp/bulk-import',
    headers=headers,
    json=data
)

result = response.json()
print(f"Imported: {result['data']['imported']}/{result['data']['total']}")
```

---

### 3. READ ALL - GET `/manual-whatsapp/`

Get semua record manual WhatsApp.

**Query Parameters:**
- `active_only`: boolean (default: false) - Hanya tampilkan customer aktif

**Response:**
```json
{
  "total": 45,
  "active": 42,
  "inactive": 3,
  "data": [
    {
      "id": "550e8400-e29b-41d4-a716-446655440000",
      "customer_name": "Bapak Joko",
      "nopol": "B 1234 XYZ",
      "no_hp": "628123456789",
      "last_service": "2025-10-15",
      "next_service": "2026-01-15",
      "is_active": 1,
      "reminder_sent_count": 2,
      "last_reminder_sent": "2026-01-03T10:30:00",
      "notes": "Customer VIP",
      "created_at": "2025-11-20T08:00:00",
      "updated_at": "2026-01-03T10:30:00"
    }
  ]
}
```

**Example cURL:**
```bash
# Get semua
curl -X GET "http://localhost:8000/manual-whatsapp/" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"

# Get hanya yang aktif
curl -X GET "http://localhost:8000/manual-whatsapp/?active_only=true" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"
```

---

### 4. READ BY ID - GET `/manual-whatsapp/{record_id}`

Get detail record by ID.

**Path Parameter:**
- `record_id`: UUID dari record

**Response:**
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "customer_name": "Bapak Joko",
  "nopol": "B 1234 XYZ",
  "no_hp": "628123456789",
  "last_service": "2025-10-15",
  "next_service": "2026-01-15",
  "is_active": 1,
  "reminder_sent_count": 2,
  "last_reminder_sent": "2026-01-03T10:30:00",
  "notes": "Customer VIP",
  "created_at": "2025-11-20T08:00:00",
  "updated_at": "2026-01-03T10:30:00"
}
```

---

### 5. READ BY NOPOL - GET `/manual-whatsapp/by-nopol/{nopol}`

Get detail record by nomor polisi.

**Path Parameter:**
- `nopol`: Nomor polisi

**Example cURL:**
```bash
curl -X GET "http://localhost:8000/manual-whatsapp/by-nopol/B%201234%20XYZ" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"
```

---

### 6. UPDATE - PUT `/manual-whatsapp/{record_id}`

Update record (semua field opsional).

**Path Parameter:**
- `record_id`: UUID dari record

**Request Body (semua opsional):**
```json
{
  "customer_name": "Bapak Joko Updated",
  "nopol": "B 1234 XYZ",
  "no_hp": "08123456789",
  "last_service": "2025-10-15",
  "next_service": "2026-02-01",
  "is_active": 1,
  "notes": "Updated notes"
}
```

**Response:** Updated record (sama seperti GET)

**Example cURL:**
```bash
curl -X PUT "http://localhost:8000/manual-whatsapp/550e8400-e29b-41d4-a716-446655440000" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "next_service": "2026-02-01"
  }'
```

---

### 7. TOGGLE ACTIVE STATUS - PATCH `/manual-whatsapp/{record_id}/toggle-active`

Toggle status aktif/tidak aktif.

**Path Parameter:**
- `record_id`: UUID dari record

**Response:** Updated record

**Example cURL:**
```bash
curl -X PATCH "http://localhost:8000/manual-whatsapp/550e8400-e29b-41d4-a716-446655440000/toggle-active" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"
```

---

### 8. DELETE - DELETE `/manual-whatsapp/{record_id}`

Delete record.

**Path Parameter:**
- `record_id`: UUID dari record

**Response:** 204 No Content

**Example cURL:**
```bash
curl -X DELETE "http://localhost:8000/manual-whatsapp/550e8400-e29b-41d4-a716-446655440000" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"
```

---

### 9. SEND REMINDERS - POST `/manual-whatsapp/send-reminders`

Kirim reminder WhatsApp ke customer yang next_service dalam X hari.

**Request Body:**
```json
{
  "days_threshold": 3,
  "only_active": true
}
```

**Response:**
```json
{
  "total_records": 45,
  "reminder_sent": 12,
  "reminder_failed": 1,
  "details": [
    {
      "id": "550e8400-e29b-41d4-a716-446655440000",
      "customer_name": "Bapak Joko",
      "nopol": "B 1234 XYZ",
      "status": "sent",
      "message": "Halo Bapak Joko...",
      "api_response": "Success sent message"
    },
    {
      "id": "550e8400-e29b-41d4-a716-446655440001",
      "customer_name": "Ibu Siti",
      "nopol": "B 5678 ABC",
      "status": "skipped",
      "reason": "Next service tidak dalam 3 hari (dalam 5 hari)"
    }
  ]
}
```

**Example cURL:**
```bash
curl -X POST "http://localhost:8000/manual-whatsapp/send-reminders" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "days_threshold": 3,
    "only_active": true
  }'
```

---

### 10. SEND TO SPECIFIC CUSTOMER - POST `/manual-whatsapp/{record_id}/send-reminder`

Kirim reminder ke customer spesifik (tanpa melihat threshold tanggal).

**Path Parameter:**
- `record_id`: UUID dari record

**Response:**
```json
{
  "success": true,
  "data": {
    "id": "550e8400-e29b-41d4-a716-446655440000",
    "customer_name": "Bapak Joko",
    "nopol": "B 1234 XYZ",
    "status": "sent",
    "message": "Halo Bapak Joko...",
    "api_response": "Success sent message"
  },
  "message": "Reminder berhasil dikirim"
}
```

**Example cURL:**
```bash
curl -X POST "http://localhost:8000/manual-whatsapp/550e8400-e29b-41d4-a716-446655440000/send-reminder" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"
```

---

### 11. SEND CUSTOM MESSAGE - POST `/manual-whatsapp/send-custom-message`

Kirim custom WhatsApp message ke nomor yang ditentukan (tidak harus ada di database).

**Use Cases:**
- Kirim pesan promosi manual
- Kirim reminder custom dengan format bebas
- Kirim notifikasi khusus ke customer
- Testing pengiriman WhatsApp
- Kirim pesan ke nomor yang tidak ada di database

**Request Body:**
```json
{
  "no_hp": "08123456789",
  "message": "Halo Bapak John, kami ingin mengingatkan bahwa kendaraan B 1234 XYZ Anda perlu service rutin minggu depan. Hubungi kami di 08551000727."
}
```

**Parameters:**
| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `no_hp` | string | ✅ Yes | Nomor HP tujuan (format: 62xxx atau 08xxx) |
| `message` | string | ✅ Yes | Isi pesan WhatsApp (custom dari front-end, max 2000 karakter) |

**Response:**
```json
{
  "status": "sent",
  "no_hp": "628123456789",
  "message": "Halo Bapak John, kami ingin mengingatkan bahwa kendaraan B 1234 XYZ Anda perlu service rutin minggu depan. Hubungi kami di 08551000727.",
  "api_response": {
    "success": true,
    "data": {
      "message_id": 123456
    },
    "message": "Success sent message"
  }
}
```

**Example cURL:**
```bash
curl -X POST "http://localhost:8000/manual-whatsapp/send-custom-message" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "no_hp": "08123456789",
    "message": "Halo Bapak John, kendaraan B 1234 XYZ Anda perlu service minggu depan."
  }'
```

**Example Python:**
```python
import requests

headers = {
    'Authorization': 'Bearer YOUR_JWT_TOKEN',
    'Content-Type': 'application/json'
}

data = {
    "no_hp": "08123456789",
    "message": "Halo Bapak John, kendaraan B 1234 XYZ Anda perlu service minggu depan. Hubungi kami di 08551000727."
}

response = requests.post(
    'http://localhost:8000/manual-whatsapp/send-custom-message',
    headers=headers,
    json=data
)

result = response.json()
print(f"Status: {result['status']}")
print(f"Sent to: {result['no_hp']}")
```

**Features:**
- ✅ Tidak perlu nomor ada di database
- ✅ Message bebas/custom dari front-end
- ✅ Auto normalize nomor HP (08xxx → 62xxx)
- ✅ Validasi nomor dan message
- ✅ Real-time response dari WhatsApp API

---

### 12. GET STATISTICS - GET `/manual-whatsapp/stats/summary`

Get statistik manual WhatsApp customers.

**Response:**
```json
{
  "success": true,
  "data": {
    "total_customers": 45,
    "active_customers": 42,
    "inactive_customers": 3,
    "reminders_sent_total": 28,
    "customers_with_upcoming_service": 8
  }
}
```

**Example cURL:**
```bash
curl -X GET "http://localhost:8000/manual-whatsapp/stats/summary" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"
```

---

## Schemas

### ManualWhatsAppCreate
```python
{
    "customer_name": str,      # Required
    "nopol": str,              # Required, unique
    "no_hp": str,              # Required
    "last_service": date,      # Optional
    "next_service": date,      # Optional
    "notes": str               # Optional
}
```

### ManualWhatsAppUpdate
```python
{
    "customer_name": str,      # Optional
    "nopol": str,              # Optional
    "no_hp": str,              # Optional
    "last_service": date,      # Optional
    "next_service": date,      # Optional
    "is_active": int,          # Optional (1 or 0)
    "notes": str               # Optional
}
```

### ManualWhatsAppResponse
```python
{
    "id": str,
    "customer_name": str,
    "nopol": str,
    "no_hp": str,
    "last_service": str,
    "next_service": str,
    "is_active": int,
    "reminder_sent_count": int,
    "last_reminder_sent": str,
    "notes": str,
    "created_at": str,
    "updated_at": str
}
```

### SendCustomMessageRequest
```python
{
    "no_hp": str,              # Required (format: 62xxx atau 08xxx)
    "message": str             # Required (max 2000 karakter)
}
```

### SendCustomMessageResponse
```python
{
    "status": str,             # "sent" atau "failed"
    "no_hp": str,              # Normalized phone number
    "message": str,            # Message yang dikirim
    "api_response": dict       # Response dari WhatsApp API
}
```

---

## Service Functions

### create_manual_whatsapp()
```python
def create_manual_whatsapp(db: Session, data: ManualWhatsAppCreate) -> Dict[str, Any]
```
Create record baru. Auto-normalize phone number.

### get_manual_whatsapp_by_id()
```python
def get_manual_whatsapp_by_id(db: Session, record_id: str) -> Dict[str, Any]
```
Get by ID.

### get_manual_whatsapp_by_nopol()
```python
def get_manual_whatsapp_by_nopol(db: Session, nopol: str) -> Dict[str, Any]
```
Get by nopol.

### get_all_manual_whatsapp()
```python
def get_all_manual_whatsapp(db: Session, active_only: bool = False) -> Dict[str, Any]
```
Get semua records dengan summary.

### update_manual_whatsapp()
```python
def update_manual_whatsapp(db: Session, record_id: str, data: ManualWhatsAppUpdate) -> Dict[str, Any]
```
Update record. Partial update supported.

### delete_manual_whatsapp()
```python
def delete_manual_whatsapp(db: Session, record_id: str) -> bool
```
Delete record.

### send_reminder_to_manual_customers()
```python
def send_reminder_to_manual_customers(
    db: Session,
    days_threshold: int = 3,
    only_active: bool = True
) -> Dict[str, Any]
```
Kirim reminder WhatsApp ke customers. Auto-track reminder count & last sent time.

### bulk_import_manual_whatsapp()
```python
def bulk_import_manual_whatsapp(db: Session, records_data: List[ManualWhatsAppCreate]) -> Dict[str, Any]
```
Bulk import multiple records.

### send_custom_whatsapp_message()
```python
def send_custom_whatsapp_message(no_hp: str, message: str) -> Dict[str, Any]
```
Kirim custom WhatsApp message ke nomor manapun (tidak perlu ada di database). Auto-normalize phone number.

---

## Contoh Penggunaan

### Use Case 1: Tambah Customer Manual Satu Per Satu

```python
from services.services_manual_whatsapp import create_manual_whatsapp
from schemas.manual_whatsapp import ManualWhatsAppCreate
from models.database import SessionLocal

db = SessionLocal()

try:
    data = ManualWhatsAppCreate(
        customer_name="Bapak Joko",
        nopol="B 1234 XYZ",
        no_hp="08123456789",
        last_service="2025-10-15",
        next_service="2026-01-15",
        notes="Customer VIP dari workshop XYZ"
    )
    
    result = create_manual_whatsapp(db, data)
    print(f"✓ Customer {result['customer_name']} berhasil ditambah")
    print(f"  ID: {result['id']}")
    print(f"  Nopol: {result['nopol']}")
    print(f"  Phone: {result['no_hp']}")

finally:
    db.close()
```

---

### Use Case 2: Import Banyak Customer dari File Excel

```python
import pandas as pd
from services.services_manual_whatsapp import bulk_import_manual_whatsapp
from schemas.manual_whatsapp import ManualWhatsAppCreate
from models.database import SessionLocal

db = SessionLocal()

try:
    # Read from Excel
    df = pd.read_excel('manual_customers.xlsx')
    
    # Convert to schema
    records_data = []
    for _, row in df.iterrows():
        record = ManualWhatsAppCreate(
            customer_name=row['Nama'],
            nopol=row['No Pol'],
            no_hp=row['No HP'],
            last_service=pd.to_datetime(row['Last Service']).date() if pd.notna(row['Last Service']) else None,
            next_service=pd.to_datetime(row['Next Service']).date(),
            notes=row.get('Notes', '')
        )
        records_data.append(record)
    
    # Bulk import
    result = bulk_import_manual_whatsapp(db, records_data)
    
    print(f"Import completed:")
    print(f"  Total: {result['total']}")
    print(f"  Success: {result['imported']}")
    print(f"  Failed: {result['failed']}")
    
    if result['failures']:
        print("\nFailures:")
        for failure in result['failures']:
            print(f"  - {failure['customer_name']}: {failure['error']}")

finally:
    db.close()
```

---

### Use Case 3: Kirim Reminder Otomatis Setiap Hari

```python
# Di main.py atau startup event

from services.scheduler_maintenance_reminder import start_scheduler
from services.services_manual_whatsapp import send_reminder_to_manual_customers
from models.database import SessionLocal
from apscheduler.schedulers.background import BackgroundScheduler
import logging

logger = logging.getLogger(__name__)

def manual_whatsapp_reminder_job():
    """Job untuk kirim reminder manual whatsapp"""
    db = SessionLocal()
    try:
        result = send_reminder_to_manual_customers(db, days_threshold=3, only_active=True)
        logger.info(f"Manual WhatsApp reminder: {result['reminder_sent']}/{result['total_records']} sent")
    except Exception as e:
        logger.error(f"Error in manual_whatsapp_reminder_job: {str(e)}")
    finally:
        db.close()

# Create scheduler
scheduler = BackgroundScheduler()

# Add job - jalankan setiap hari jam 9 pagi
scheduler.add_job(
    manual_whatsapp_reminder_job,
    'cron',
    hour=9,
    minute=0,
    id='manual_whatsapp_reminder_job',
    name='Manual WhatsApp Reminder',
    replace_existing=True,
    max_instances=1
)

scheduler.start()
```

---

### Use Case 4: Kirim Custom Message Manual

```python
from services.services_manual_whatsapp import send_custom_whatsapp_message

try:
    result = send_custom_whatsapp_message(
        no_hp="08123456789",
        message="Halo Bapak John, kami ada promo service gratis untuk kendaraan B 1234 XYZ. Hubungi kami di 08551000727."
    )
    
    print(f"✓ Pesan berhasil dikirim ke {result['no_hp']}")
    print(f"  Status: {result['status']}")
    print(f"  API Response: {result['api_response']}")
    
except Exception as e:
    print(f"✗ Gagal mengirim pesan: {str(e)}")
```

**API Request:**
```bash
curl -X POST "http://localhost:8000/manual-whatsapp/send-custom-message" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "no_hp": "08123456789",
    "message": "Halo, ada promo service gratis minggu ini!"
  }'
```

---

### Use Case 5: Dashboard Monitoring

```python
# routes untuk dashboard

@app.get("/manual-whatsapp/dashboard")
def dashboard(db: Session = Depends(get_db), _=Depends(jwt_required)):
    """Dashboard untuk monitoring manual WhatsApp"""
    from datetime import date, timedelta
    from models.manual_whatsapp import ManualWhatsApp
    
    total = db.query(ManualWhatsApp).count()
    active = db.query(ManualWhatsApp).filter(ManualWhatsApp.is_active == 1).count()
    
    # Reminder di bulan ini
    month_start = date.today().replace(day=1)
    month_sent = db.query(ManualWhatsApp).filter(
        ManualWhatsApp.last_reminder_sent >= month_start
    ).count()
    
    # Top customers by reminder count
    top_customers = db.query(ManualWhatsApp).order_by(
        ManualWhatsApp.reminder_sent_count.desc()
    ).limit(5).all()
    
    return {
        "total_customers": total,
        "active_customers": active,
        "reminders_this_month": month_sent,
        "top_customers": [
            {
                "customer_name": c.customer_name,
                "nopol": c.nopol,
                "reminder_count": c.reminder_sent_count,
                "last_sent": c.last_reminder_sent.isoformat() if c.last_reminder_sent else None
            }
            for c in top_customers
        ]
    }
```

---

## Integrasi dengan Existing System

### Perbedaan Manual vs Integrated Customer

| Aspek | Manual WhatsApp | Integrated (getListCustomersWithvehicles) |
|-------|-----------------|-------------------------------------------|
| **Table** | manual_whatsapp | customer + vehicle |
| **Data Entry** | Manual via API | Auto dari customer registration |
| **Phone Format** | Manual normalization | From customer table |
| **Service Dates** | Manual input | Auto calculate (last_visit + 4 bulan) |
| **Tracking** | reminder_sent_count | None |
| **Use Case** | Customer tidak di DB utama | Terintegrasi penuh |
| **Endpoint** | /manual-whatsapp | /customers/send-maintenance-reminder |

### Hybrid Approach

Anda bisa menjalankan kedua sistem bersamaan:

```python
# Send reminder ke BOTH integrated dan manual customers

async def send_all_reminders():
    db = SessionLocal()
    
    # Send ke integrated customers
    integrated_result = send_maintenance_reminder_whatsapp(db)
    
    # Send ke manual customers
    manual_result = send_reminder_to_manual_customers(db)
    
    # Combine results
    total_sent = integrated_result['reminder_sent'] + manual_result['reminder_sent']
    total_failed = 0 + manual_result['reminder_failed']
    
    print(f"Total reminders sent: {total_sent}")
    print(f"Total failed: {total_failed}")
    
    db.close()
```

---

**Created**: January 3, 2026  
**Version**: 1.0.0  
**Status**: Production Ready
