# Dokumentasi API WhatsApp - FastAPI Bengkel

## Daftar Isi

- [Ringkasan](#ringkasan)
- [Konfigurasi](#konfigurasi)
- [API Endpoints](#api-endpoints)
  - [WhatsApp Send Endpoints](#whatsapp-send-endpoints)
  - [Maintenance Reminder Endpoints](#maintenance-reminder-endpoints)
  - [Manual WhatsApp Endpoints](#manual-whatsapp-endpoints)
  - [WhatsApp Report Endpoints](#whatsapp-report-endpoints)
- [Schemas](#schemas)
- [Service Functions](#service-functions)
- [Maintenance Reminder System](#maintenance-reminder-system)
  - [Scheduler Configuration](#scheduler-configuration)
  - [Service Logic](#service-logic)
  - [Routes Integration](#routes-integration)
- [WhatsApp Report Tracking System](#whatsapp-report-tracking-system)
- [Manual WhatsApp System](#manual-whatsapp-system)
- [Contoh Penggunaan](#contoh-penggunaan)
- [Error Handling](#error-handling)

---

## Ringkasan

Fitur pengiriman WhatsApp di aplikasi FastAPI Bengkel menggunakan **StarSender API Gateway** untuk mengirim pesan WhatsApp secara programatik. Fitur ini mencakup empat sistem utama:

### 1. WhatsApp Messaging System

- Pengiriman pesan teks sederhana
- Pengiriman pesan dengan file/media
- Pengiriman pesan terjadwal (scheduled messages)
- Delay pengiriman pesan
- Autentikasi JWT pada endpoint utama

### 2. Maintenance Reminder System (Automated)

- **Scheduler otomatis** yang berjalan setiap hari
- Mengirim reminder WhatsApp ke customer yang kendaraannya akan jatuh tempo service
- Deteksi otomatis berdasarkan `next_visit_date` (kurang dari 3 hari)
- Manual trigger melalui API endpoint
- Logging lengkap untuk monitoring

### 3. Manual WhatsApp System (Manual Customers)

- CRUD data customer manual (tidak ada di tabel utama)
- Kirim reminder manual berbasis `next_service`
- Bulk import data (CSV/Excel → JSON payload)
- Toggle aktif/non-aktif per customer
- Statistik ringkas (total/active/inactive)

### 4. WhatsApp Report Tracking System (NEW)

- **Auto tracking** setiap pengiriman WhatsApp ke customer+vehicle
- Update frequency dan last_message_date otomatis
- Statistik agregat (total pesan, average, breakdown by frequency)
- Detail report dengan customer & vehicle info
- Reset frequency untuk analisis berkala
- Integration seamless dengan maintenance reminder scheduler

**Gateway API**: [https://api.starsender.online/api/send](https://api.starsender.online/api/send)

---

## Konfigurasi

### Environment Variables

**File `.env`** (di root project):

```env
# WhatsApp API Configuration
STARSENDER_API_KEY=your_api_key_here

# Database Configuration
DATABASE_URL=postgresql+psycopg2://username:password@localhost:5432/database_name
```

**Setup:**

1. Copy file `.env.example` menjadi `.env`
2. Isi `STARSENDER_API_KEY` dengan API key dari StarSender
3. Sesuaikan `DATABASE_URL` dengan konfigurasi database Anda
4. Install dependency: `pip install python-dotenv`

**Implementasi** (`services/services_whatsapp.py`):

```python
from dotenv import load_dotenv
import os

load_dotenv()

STARSENDER_API_URL = "https://api.starsender.online/api/send"
STARSENDER_API_KEY = os.getenv('STARSENDER_API_KEY', '')
REQUEST_TIMEOUT = 30  # timeout dalam detik
```

✅ **Security**: API Key dan DATABASE_URL sekarang tersimpan aman di file `.env` yang tidak ter-commit ke repository (ada di `.gitignore`).

---

## API Endpoints

### WhatsApp Send Endpoints

#### 1. POST `/whatsapp/send`

Endpoint utama untuk mengirim pesan WhatsApp dengan berbagai opsi.

**Authentication**: ✅ Memerlukan JWT Token

**Request Body**:

```json
{
  "to": "628123456789",
  "body": "Halo, ini pesan dari bengkel",
  "file": "https://example.com/invoice.pdf",
  "delay": 5,
  "schedule": 1704067200000
}
```

**Parameters**:

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `to` | string | ✅ Yes | Nomor WhatsApp tujuan (format: 62xxx atau 08xxx) |
| `body` | string | ✅ Yes | Isi pesan WhatsApp |
| `file` | string | ❌ No | URL file/media yang akan dikirim |
| `delay` | integer | ❌ No | Delay pengiriman dalam detik |
| `schedule` | integer | ❌ No | Timestamp jadwal pengiriman (dalam milliseconds) |

**Response Success**:

```json
{
  "success": true,
  "data": {
    "messageId": "msg_12345",
    "status": "sent"
  },
  "message": "Pesan berhasil dikirim"
}
```

**Response Error**:

```json
{
  "success": false,
  "data": {},
  "message": "Gagal mengirim pesan WhatsApp: [error detail]"
}
```

**Example cURL**:

```bash
curl -X POST "http://localhost:8000/whatsapp/send" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "to": "628123456789",
    "body": "Terima kasih telah menggunakan layanan kami"
  }'
```

---

#### 2. POST `/whatsapp/send-simple`

Endpoint sederhana untuk mengirim pesan teks tanpa autentikasi.

**Authentication**: ❌ Tidak memerlukan JWT Token

**Query Parameters**:

- `phone` (string, required): Nomor WhatsApp tujuan
- `message` (string, required): Isi pesan

**Response**: Sama dengan endpoint `/send`

**Example cURL**:

```bash
curl -X POST "http://localhost:8000/whatsapp/send-simple?phone=628123456789&message=Hello%20World"
```

**Example JavaScript (fetch)**:

```javascript
fetch('http://localhost:8000/whatsapp/send-simple?phone=628123456789&message=Hello', {
  method: 'POST'
})
.then(res => res.json())
.then(data => console.log(data));
```

---

#### 3. POST `/whatsapp/send-with-file`

Endpoint untuk mengirim pesan dengan attachment file/media.

**Authentication**: ❌ Tidak memerlukan JWT Token

**Query Parameters**:

- `phone` (string, required): Nomor WhatsApp tujuan
- `message` (string, required): Isi pesan
- `file_url` (string, required): URL publik dari file yang akan dikirim

**Supported File Types**:

- Gambar: JPG, PNG, GIF
- Dokumen: PDF, DOC, DOCX, XLS, XLSX
- Video: MP4, AVI
- Audio: MP3, WAV

**Example cURL**:

```bash
curl -X POST "http://localhost:8000/whatsapp/send-with-file?phone=628123456789&message=Invoice%20Anda&file_url=https://example.com/invoice.pdf"
```

**Example Python**:

```python
import requests

response = requests.post(
    'http://localhost:8000/whatsapp/send-with-file',
    params={
        'phone': '628123456789',
        'message': 'Berikut invoice service Anda',
        'file_url': 'https://example.com/invoices/INV-001.pdf'
    }
)
print(response.json())
```

---

#### 4. POST `/whatsapp/send-scheduled`

Endpoint untuk mengirim pesan terjadwal (scheduled message).

**Authentication**: ❌ Tidak memerlukan JWT Token

**Query Parameters**:

- `phone` (string, required): Nomor WhatsApp tujuan
- `message` (string, required): Isi pesan
- `schedule_timestamp_ms` (integer, required): Timestamp dalam milliseconds

**Cara Mendapatkan Timestamp**:

```python
# Python
from datetime import datetime, timedelta

# Jadwalkan 1 jam dari sekarang
future_time = datetime.now() + timedelta(hours=1)
timestamp_ms = int(future_time.timestamp() * 1000)
```

```javascript
// JavaScript
// Jadwalkan 1 jam dari sekarang
const futureTime = new Date();
futureTime.setHours(futureTime.getHours() + 1);
const timestamp_ms = futureTime.getTime();
```

**Example cURL**:

```bash
curl -X POST "http://localhost:8000/whatsapp/send-scheduled?phone=628123456789&message=Reminder%20Service&schedule_timestamp_ms=1704067200000"
```

---

### Maintenance Reminder Endpoints

#### 5. POST `/customers/send-maintenance-reminder`

Endpoint untuk mengirim reminder WhatsApp secara manual ke semua customer yang kendaraannya akan jatuh tempo service (kurang dari 3 hari).

**Authentication**: ✅ Memerlukan JWT Token

**Request**: Tidak ada body/parameter

**Response Success**:

```json
{
  "success": true,
  "data": {
    "total_customers": 45,
    "reminder_sent": 12,
    "details": [
      {
        "no_pol": "B 1234 XYZ",
        "customer_nama": "John Doe",
        "customer_hp": "628123456789",
        "next_visit_date": "2026-01-05",
        "days_until_visit": 2,
        "status": "sent",
        "message": "Bapak John Doe untuk nomor kendaraan B 1234 XYZ...",
        "api_response": "Success sent message"
      },
      {
        "no_pol": "B 5678 ABC",
        "customer_nama": "Jane Smith",
        "status": "skipped",
        "reason": "Data tidak lengkap"
      },
      {
        "no_pol": "D 9999 DEF",
        "customer_nama": "Bob Wilson",
        "status": "failed",
        "reason": "Gagal menghubungi API StarSender"
      }
    ]
  },
  "message": "Success"
}
```

**Response Fields**:

- `total_customers`: Total customer dengan kendaraan dalam database
- `reminder_sent`: Jumlah reminder yang berhasil dikirim
- `details`: Array berisi detail setiap kendaraan dengan status:
  - `sent`: Berhasil dikirim
  - `skipped`: Dilewati (tidak memenuhi kriteria atau data tidak lengkap)
  - `failed`: Gagal kirim (error API)

**Logic Pengiriman**:

1. Mengambil semua customer dengan vehicle dari database
2. Cek setiap vehicle untuk `next_visit_date`
3. Jika `next_visit_date` kurang dari 3 hari dari hari ini (0-2 hari), kirim reminder
4. Format nomor HP otomatis (08xxx → 62xxx)
5. Kirim WhatsApp dengan format standar maintenance reminder

**Format Pesan**:

```
Bapak {customer_nama} untuk nomor kendaraan {no_pol} 
sebentar lagi tiba saat pemeliharaan rutin pada tanggal {dd-mm-yyyy}, 
daftarkan segera melalui nomor pelayanan kami 08551000727
```

**Example cURL**:

```bash
curl -X POST "http://localhost:8000/customers/send-maintenance-reminder" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -H "Content-Type: application/json"
```

**Example Python**:

```python
import requests

headers = {
    'Authorization': 'Bearer YOUR_JWT_TOKEN'
}

response = requests.post(
    'http://localhost:8000/customers/send-maintenance-reminder',
    headers=headers
)

result = response.json()
print(f"Reminder terkirim: {result['data']['reminder_sent']}/{result['data']['total_customers']}")
```

**Use Case**:

- Manual trigger saat ingin mengirim reminder di luar jadwal scheduler
- Testing sistem reminder sebelum deploy scheduler
- Emergency reminder saat ada banyak kendaraan jatuh tempo

---

### Manual WhatsApp Endpoints

Endpoint untuk pelanggan manual (tidak ada di tabel customer utama). Semua endpoint memerlukan JWT kecuali disebutkan berbeda.

- **POST `/manual-whatsapp/`** — Buat customer manual
- **GET `/manual-whatsapp/`** — List semua customer (dapat difilter aktif via query `active_only` bila ditambahkan)
- **GET `/manual-whatsapp/{record_id}`** — Detail by ID
- **GET `/manual-whatsapp/by-nopol/{nopol}`** — Detail by nopol
- **PUT `/manual-whatsapp/{record_id}`** — Update data
- **PATCH `/manual-whatsapp/{record_id}/toggle-active`** — Toggle aktif/non-aktif
- **DELETE `/manual-whatsapp/{record_id}`** — Hapus data
- **POST `/manual-whatsapp/send-reminders`** — Kirim reminder ke semua customer manual yang `next_service` jatuh dalam threshold (default 3 hari); request body:

    ```json
    {"days_threshold": 3, "only_active": true}
    ```

- **POST `/manual-whatsapp/{record_id}/send-reminder`** — Kirim reminder ke satu customer manual
- **POST `/manual-whatsapp/bulk-import`** — Bulk import array JSON; setiap item mengikuti schema `ManualWhatsAppCreate`
- **GET `/manual-whatsapp/stats/summary`** — Statistik ringkas (total/active/inactive)

**Catatan penting**:

- Nomor HP otomatis dinormalisasi ke format 62xxx
- `next_service` dipakai sebagai acuan reminder manual
- `reminder_sent_count` dan `last_reminder_sent` otomatis ter-update saat pengiriman reminder

---

## Schemas

### WhatsAppMessageCreate

Schema untuk data pesan WhatsApp internal.

```python
class WhatsAppMessageCreate(BaseModel):
    message_type: str = "text"  # Default: "text"
    to: str  # Required
    body: str  # Required
    file: Optional[str] = None
    delay: Optional[int] = None
    schedule: Optional[int] = None
```

### WhatsAppSendRequest

Schema untuk request body endpoint `/send`.

```python
class WhatsAppSendRequest(BaseModel):
    to: str  # Required
    body: str  # Required
    file: Optional[str] = None
    delay: Optional[int] = None
    schedule: Optional[int] = None
```

### WhatsAppMessageResponse

Schema untuk response API.

```python
class WhatsAppMessageResponse(BaseModel):
    success: bool
    data: dict
    message: str
```

---

## Service Functions

File: `services/services_whatsapp.py`

### 1. `send_whatsapp_message()` - Async

Fungsi asynchronous untuk mengirim pesan WhatsApp.

```python
async def send_whatsapp_message(message_data: WhatsAppMessageCreate) -> Dict[str, Any]
```

**Parameters**:

- `message_data`: Instance dari WhatsAppMessageCreate

**Returns**: Dictionary dengan struktur response API

**Usage Example**:

```python
from services.services_whatsapp import send_whatsapp_message
from schemas.service_whatsapp import WhatsAppMessageCreate

async def send_reminder():
    message = WhatsAppMessageCreate(
        message_type="text",
        to="628123456789",
        body="Reminder: Service kendaraan Anda besok jam 10:00"
    )
    result = await send_whatsapp_message(message)
    return result
```

---

### 2. `send_whatsapp_message_sync()` - Synchronous

Versi synchronous dari fungsi pengiriman pesan.

```python
def send_whatsapp_message_sync(message_data: WhatsAppMessageCreate) -> Dict[str, Any]
```

**Parameters**: Sama dengan versi async

**Returns**: Dictionary dengan struktur response API

**Usage Example**:

```python
from services.services_whatsapp import send_whatsapp_message_sync
from schemas.service_whatsapp import WhatsAppMessageCreate

def send_invoice():
    message = WhatsAppMessageCreate(
        message_type="text",
        to="628123456789",
        body="Invoice service Anda telah siap",
        file="https://example.com/invoices/INV-123.pdf"
    )
    result = send_whatsapp_message_sync(message)
    return result
```

---

### 3. `send_simple_message()` - Helper

Helper function untuk mengirim pesan text sederhana.

```python
def send_simple_message(phone: str, message: str) -> Dict[str, Any]
```

**Parameters**:

- `phone`: Nomor WhatsApp tujuan
- `message`: Isi pesan

**Returns**: Dictionary response API

**Usage Example**:

```python
from services.services_whatsapp import send_simple_message

result = send_simple_message("628123456789", "Terima kasih!")
```

---

### 4. `send_message_with_file()` - Helper

Helper function untuk mengirim pesan dengan file attachment.

```python
def send_message_with_file(phone: str, message: str, file_url: str) -> Dict[str, Any]
```

**Parameters**:

- `phone`: Nomor WhatsApp tujuan
- `message`: Isi pesan
- `file_url`: URL file publik

**Returns**: Dictionary response API

**Usage Example**:

```python
from services.services_whatsapp import send_message_with_file

result = send_message_with_file(
    phone="628123456789",
    message="Berikut invoice Anda",
    file_url="https://example.com/invoice.pdf"
)
```

---

### 5. `send_scheduled_message()` - Helper

Helper function untuk mengirim pesan terjadwal.

```python
def send_scheduled_message(phone: str, message: str, schedule_timestamp_ms: int) -> Dict[str, Any]
```

**Parameters**:

- `phone`: Nomor WhatsApp tujuan
- `message`: Isi pesan
- `schedule_timestamp_ms`: Timestamp dalam milliseconds

**Returns**: Dictionary response API

**Usage Example**:

```python
from services.services_whatsapp import send_scheduled_message
from datetime import datetime, timedelta

# Jadwalkan 24 jam dari sekarang
future = datetime.now() + timedelta(days=1)
timestamp = int(future.timestamp() * 1000)

result = send_scheduled_message(
    phone="628123456789",
    message="Reminder: Service besok jam 10:00",
    schedule_timestamp_ms=timestamp
)
```

---

### 6. `send_maintenance_reminder_whatsapp()` - Maintenance System

Fungsi utama untuk sistem maintenance reminder otomatis.

**File**: `services/services_customer.py`

```python
def send_maintenance_reminder_whatsapp(db: Session) -> Dict[str, Any]
```

**Parameters**:

- `db`: Database session SQLAlchemy

**Returns**: Dictionary dengan struktur:

```python
{
    "total_customers": int,  # Total customer dengan vehicle
    "reminder_sent": int,    # Jumlah reminder terkirim
    "details": [            # Detail setiap customer/vehicle
        {
            "no_pol": str,
            "customer_nama": str,
            "customer_hp": str,
            "next_visit_date": str,  # ISO format: "YYYY-MM-DD"
            "days_until_visit": int,
            "status": str,  # "sent", "skipped", atau "failed"
            "message": str,
            "api_response": str
        }
    ]
}
```

**Logic**:

1. Mengambil semua customer dengan vehicle dari `getListCustomersWithvehicles(db)`
2. Iterasi setiap vehicle, cek `next_visit_date`
3. Hitung selisih hari: `days_until_visit = (next_visit_date - today).days`
4. Jika `0 <= days_until_visit < 3`, kirim reminder WhatsApp
5. Format nomor HP otomatis (08xxx → 62xxx)
6. Kirim menggunakan `send_whatsapp_message_sync()`
7. Return hasil dengan detail status setiap pengiriman

**Format Pesan**:

```
Bapak {customer_nama} untuk nomor kendaraan {no_pol} 
sebentar lagi tiba saat pemeliharaan rutin pada tanggal {dd-mm-yyyy}, 
daftarkan segera melalui nomor pelayanan kami 08551000727
```

**Usage Example**:

```python
from services.services_customer import send_maintenance_reminder_whatsapp
from models.database import SessionLocal

db = SessionLocal()
try:
    result = send_maintenance_reminder_whatsapp(db)
    print(f"Reminder sent: {result['reminder_sent']}/{result['total_customers']}")
    
    # Print details
    for detail in result['details']:
        if detail['status'] == 'sent':
            print(f"✓ {detail['no_pol']} - {detail['customer_nama']}")
        elif detail['status'] == 'failed':
            print(f"✗ {detail['no_pol']} - Error: {detail['reason']}")
finally:
    db.close()
```

**Error Handling**:

- Customer tanpa data lengkap (nama, HP, no_pol, next_visit_date) → status `skipped`
- Format `next_visit_date` tidak valid → status `skipped`
- Error saat kirim WhatsApp API → status `failed` dengan detail error
- Exception global → raise `Exception` dengan pesan error

---

## Maintenance Reminder System

Sistem reminder maintenance otomatis adalah fitur yang mengirim notifikasi WhatsApp ke customer yang kendaraannya akan jatuh tempo service dalam waktu kurang dari 3 hari.

### Scheduler Configuration

**File**: `services/scheduler_maintenance_reminder.py`

Menggunakan **APScheduler** (Advanced Python Scheduler) untuk menjalankan job di background.

#### Setup Scheduler

```python
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger

scheduler = BackgroundScheduler()
```

#### Function: `start_scheduler()`

Memulai scheduler untuk menjalankan job secara otomatis setiap hari.

```python
def start_scheduler(hour: int = 7, minute: int = 0) -> BackgroundScheduler
```

**Parameters**:

- `hour`: Jam untuk menjalankan job (default: 7 = jam 7 pagi)
- `minute`: Menit untuk menjalankan job (default: 0)

**Returns**: Instance BackgroundScheduler

**Configuration**:

```python
scheduler.add_job(
    maintenance_reminder_job,           # Function yang akan dijalankan
    CronTrigger(hour=7, minute=0),     # Trigger: setiap hari jam 07:00
    id='maintenance_reminder_job',      # Job ID (unique)
    name='Maintenance Reminder WhatsApp',
    replace_existing=True,              # Replace jika job sudah ada
    max_instances=1                     # Hanya 1 instance yang berjalan
)
```

**Usage Example**:

```python
from services.scheduler_maintenance_reminder import start_scheduler

# Start dengan default (jam 7 pagi)
scheduler = start_scheduler()

# Custom jam
scheduler = start_scheduler(hour=8, minute=30)  # Jam 8:30 pagi
scheduler = start_scheduler(hour=6, minute=0)   # Jam 6 pagi
```

**Integration di main.py**:

```python
from fastapi import FastAPI
from services.scheduler_maintenance_reminder import start_scheduler

app = FastAPI()

@app.on_event("startup")
def startup_event():
    """Start scheduler saat aplikasi dimulai"""
    start_scheduler(hour=7, minute=0)
    print("✓ Maintenance reminder scheduler started (runs daily at 07:00)")

@app.on_event("shutdown")
def shutdown_event():
    """Stop scheduler saat aplikasi shutdown"""
    from services.scheduler_maintenance_reminder import stop_scheduler
    stop_scheduler()
    print("✓ Scheduler stopped")
```

#### Function: `stop_scheduler()`

Menghentikan scheduler.

```python
def stop_scheduler() -> None
```

**Usage**:

```python
from services.scheduler_maintenance_reminder import stop_scheduler

stop_scheduler()
```

#### Function: `get_scheduler_status()`

Mendapatkan status scheduler dan daftar job yang terdaftar.

```python
def get_scheduler_status() -> Dict[str, Any]
```

**Returns**:

```python
{
    "running": bool,  # True jika scheduler berjalan
    "jobs": [
        {
            "id": "maintenance_reminder_job",
            "name": "Maintenance Reminder WhatsApp",
            "next_run_time": "2026-01-04T07:00:00+07:00",  # ISO format
            "trigger": "cron[hour='7', minute='0']"
        }
    ]
}
```

**Usage Example**:

```python
from services.scheduler_maintenance_reminder import get_scheduler_status

status = get_scheduler_status()
if status['running']:
    for job in status['jobs']:
        print(f"Job: {job['name']}")
        print(f"Next run: {job['next_run_time']}")
```

#### Function: `maintenance_reminder_job()`

Job function yang dijalankan oleh scheduler. Function ini tidak dipanggil langsung, tapi dipanggil otomatis oleh scheduler sesuai jadwal.

```python
def maintenance_reminder_job() -> Dict[str, Any]
```

**Flow**:

1. Buat database session baru
2. Panggil `send_maintenance_reminder_whatsapp(db)`
3. Log hasil (berapa reminder terkirim)
4. Close database session
5. Return hasil

**Logging**:

```
[2026-01-03 07:00:00] Memulai job send_maintenance_reminder...
[2026-01-03 07:00:15] Job selesai. Reminder terkirim: 12/45
```

---

### Service Logic

**File**: `services/services_customer.py`

**Function**: `send_maintenance_reminder_whatsapp(db: Session)`

#### Detailed Flow

```
1. Get all customers with vehicles
   ↓
2. Loop each vehicle
   ↓
3. Validate data completeness
   - customer_nama
   - customer_hp
   - no_pol
   - next_visit_date
   ↓
4. Parse next_visit_date (ISO format)
   ↓
5. Calculate days_until_visit
   days_until_visit = (next_visit_date - today).days
   ↓
6. Check if 0 <= days_until_visit < 3
   ↓
7. Format phone number (08xxx → 62xxx)
   ↓
8. Compose WhatsApp message
   ↓
9. Send via send_whatsapp_message_sync()
   ↓
10. Collect result (sent/failed/skipped)
   ↓
11. Return summary with details
```

#### Kriteria Pengiriman

Reminder **AKAN** dikirim jika:

- ✅ Customer memiliki data lengkap (nama, HP, no_pol)
- ✅ `next_visit_date` valid dan ter-parse
- ✅ `next_visit_date` antara **0-2 hari** dari hari ini
  - 0 hari = hari ini
  - 1 hari = besok
  - 2 hari = lusa

Reminder **TIDAK** dikirim jika:

- ❌ Data customer tidak lengkap → status `skipped`
- ❌ `next_visit_date` lebih dari 3 hari → tidak masuk kriteria
- ❌ `next_visit_date` sudah lewat (negatif) → tidak masuk kriteria
- ❌ Format `next_visit_date` tidak valid → status `skipped`
- ❌ Error API WhatsApp → status `failed`

#### Phone Number Normalization

```python
phone = customer_hp.strip()
if phone.startswith('0'):
    phone = '62' + phone[1:]  # 081234 → 621234
elif not phone.startswith('62'):
    phone = '62' + phone      # 81234 → 6281234
```

**Contoh**:

- `08123456789` → `628123456789` ✅
- `8123456789` → `628123456789` ✅
- `628123456789` → `628123456789` ✅
- `+628123456789` → `62+628123456789` ❌ (tidak valid)

---

### Routes Integration

**File**: `routes/routes_customer.py`

```python
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from middleware.jwt_required import jwt_required
from models.database import get_db

router = APIRouter(prefix="/customers", tags=["Customers"])

@router.post("/send-maintenance-reminder", dependencies=[Depends(jwt_required)])
def send_maintenance_reminder_router(db: Session = Depends(get_db)):
    """
    Endpoint untuk mengirim reminder WhatsApp maintenance ke customer
    yang jadwal maintenance-nya kurang dari 3 hari.
    """
    try:
        from services.services_customer import send_maintenance_reminder_whatsapp
        result = send_maintenance_reminder_whatsapp(db)
        return success_response(data=result)
    except Exception as e:
        return error_response(message=str(e))
```

**Features**:

- ✅ JWT Authentication required
- ✅ Database dependency injection
- ✅ Error handling dengan try-catch
- ✅ Response wrapper (success_response/error_response)

**Access Control**:

- Hanya user yang sudah login (punya JWT token valid) yang bisa trigger
- Berguna untuk membatasi akses endpoint sensitif

---

### Complete Integration Example

#### 1. Setup di main.py

```python
from fastapi import FastAPI
from routes import routes_customer, routes_whatsapp
from services.scheduler_maintenance_reminder import start_scheduler, get_scheduler_status

app = FastAPI(title="FastAPI Bengkel", version="1.0.0")

# Register routes
app.include_router(routes_customer.router)
app.include_router(routes_whatsapp.router)

@app.on_event("startup")
def startup():
    """Initialize scheduler on startup"""
    start_scheduler(hour=7, minute=0)
    print("✓ Maintenance reminder scheduler started")

@app.on_event("shutdown")
def shutdown():
    """Stop scheduler on shutdown"""
    from services.scheduler_maintenance_reminder import stop_scheduler
    stop_scheduler()

@app.get("/scheduler/status")
def scheduler_status():
    """Check scheduler status"""
    return get_scheduler_status()
```

#### 2. Testing Scheduler

```python
# test_scheduler.py
from services.scheduler_maintenance_reminder import (
    start_scheduler, 
    stop_scheduler, 
    get_scheduler_status,
    maintenance_reminder_job
)
import time

# Test 1: Start scheduler
print("Starting scheduler...")
scheduler = start_scheduler(hour=7, minute=0)
print("✓ Scheduler started")

# Test 2: Check status
status = get_scheduler_status()
print(f"Running: {status['running']}")
print(f"Jobs: {len(status['jobs'])}")

# Test 3: Manual run job (untuk testing)
print("\nManually running job...")
result = maintenance_reminder_job()
print(f"Result: {result['reminder_sent']}/{result['total_customers']} sent")

# Test 4: Stop scheduler
print("\nStopping scheduler...")
stop_scheduler()
print("✓ Scheduler stopped")
```

#### 3. Monitoring & Logging

```python
# monitoring_scheduler.py
import logging
from services.scheduler_maintenance_reminder import get_scheduler_status

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    filename='scheduler.log'
)

logger = logging.getLogger(__name__)

def monitor_scheduler():
    """Monitor scheduler status"""
    status = get_scheduler_status()
    
    if not status['running']:
        logger.error("⚠️ Scheduler is not running!")
        # Send alert (email, WhatsApp, etc.)
        return False
    
    for job in status['jobs']:
        logger.info(f"Job {job['name']} - Next run: {job['next_run_time']}")
    
    return True

# Run monitoring
if __name__ == "__main__":
    monitor_scheduler()
```

---

### Maintenance Reminder Scheduler API

**Prefix**: `/scheduler/maintenance-reminder`

| Method | Endpoint | Auth | Description |
| --- | --- | --- | --- |
| POST | `/start` | ✅ JWT | Start scheduler (default 07:00, configurable via `hour`/`minute`) |
| POST | `/stop` | ✅ JWT | Stop scheduler |
| GET | `/status` | ✅ JWT | Check scheduler status and next run |
| POST | `/run-now` | ✅ JWT | Manual trigger job sekali jalan |
| POST | `/customers/send-maintenance-reminder` | ✅ JWT | Manual trigger tanpa scheduler (prefix `/customers`) |

**Quick Usage (cURL)**:

```bash
# Start scheduler (jam 7 pagi)
curl -X POST "http://localhost:8000/scheduler/maintenance-reminder/start?hour=7&minute=0" \
    -H "Authorization: Bearer YOUR_TOKEN"

# Cek status
curl -X GET "http://localhost:8000/scheduler/maintenance-reminder/status" \
    -H "Authorization: Bearer YOUR_TOKEN"

# Run sekarang (tanpa menunggu jadwal)
curl -X POST "http://localhost:8000/scheduler/maintenance-reminder/run-now" \
    -H "Authorization: Bearer YOUR_TOKEN"

# Stop scheduler
curl -X POST "http://localhost:8000/scheduler/maintenance-reminder/stop" \
    -H "Authorization: Bearer YOUR_TOKEN"

# Manual trigger tanpa scheduler
curl -X POST "http://localhost:8000/customers/send-maintenance-reminder" \
    -H "Authorization: Bearer YOUR_TOKEN"
```

**Kriteria & Perilaku Utama**:

- Eligibility: reminder dikirim jika `0 <= days_until_visit < 3` (hari ini, besok, lusa)
- Phone normalization: `08xxx` → `62xxx`; `8123` → `628123`; `+62` tidak digunakan
- Error isolation: kegagalan satu customer tidak menghentikan job; status dikembalikan di `details`
- Max instances: scheduler diset 1 instance untuk hindari duplikasi
- DB session: tiap eksekusi job membuat sesi DB baru lalu ditutup

**Reference Lengkap**: lihat [WHATSAPP_MAINTENANCE_REMINDER.md](WHATSAPP_MAINTENANCE_REMINDER.md) untuk flow, contoh payload, dan troubleshooting detail.

---

## Contoh Penggunaan

### Use Case 1: Notifikasi Selesai Service

```python
from services.services_whatsapp import send_simple_message

def notify_service_complete(customer_phone: str, work_order_id: str):
    """Kirim notifikasi setelah service selesai"""
    message = f"""
Halo Pelanggan Setia Bengkel,

Service kendaraan Anda dengan Work Order #{work_order_id} telah selesai dikerjakan.

Kendaraan Anda siap diambil.

Terima kasih atas kepercayaan Anda!
    """.strip()
    
    try:
        result = send_simple_message(customer_phone, message)
        return result
    except Exception as e:
        print(f"Gagal mengirim notifikasi: {e}")
        return None
```

---

### Use Case 2: Kirim Invoice dengan PDF

```python
from services.services_whatsapp import send_message_with_file

def send_invoice_to_customer(customer_phone: str, invoice_url: str, total: float):
    """Kirim invoice ke customer via WhatsApp"""
    message = f"""
Invoice Service Kendaraan

Total: Rp {total:,.0f}

Silakan lakukan pembayaran sesuai invoice terlampir.

Terima kasih.
    """.strip()
    
    try:
        result = send_message_with_file(
            phone=customer_phone,
            message=message,
            file_url=invoice_url
        )
        return result
    except Exception as e:
        print(f"Gagal mengirim invoice: {e}")
        return None
```

---

### Use Case 3: Reminder Maintenance Terjadwal

```python
from services.services_whatsapp import send_scheduled_message
from datetime import datetime, timedelta

def schedule_maintenance_reminder(customer_phone: str, service_date: datetime):
    """Jadwalkan reminder H-1 sebelum service"""
    
    # Kirim reminder 1 hari sebelum tanggal service
    reminder_time = service_date - timedelta(days=1)
    timestamp_ms = int(reminder_time.timestamp() * 1000)
    
    message = f"""
Reminder Maintenance Kendaraan

Kami ingin mengingatkan bahwa kendaraan Anda terjadwal untuk service pada:
📅 {service_date.strftime('%d %B %Y, %H:%M')}

Harap datang tepat waktu.

Terima kasih!
    """.strip()
    
    try:
        result = send_scheduled_message(
            phone=customer_phone,
            message=message,
            schedule_timestamp_ms=timestamp_ms
        )
        return result
    except Exception as e:
        print(f"Gagal menjadwalkan reminder: {e}")
        return None
```

---

### Use Case 4: Integration dengan Work Order

```python
from fastapi import APIRouter, Depends
from services.services_whatsapp import send_simple_message
from models.model_workorder import WorkOrder

router = APIRouter()

@router.post("/workorder/{wo_id}/complete")
async def complete_work_order(wo_id: int, db = Depends(get_db)):
    """Complete work order dan kirim notifikasi WhatsApp"""
    
    # Update work order status
    work_order = db.query(WorkOrder).filter(WorkOrder.id == wo_id).first()
    if not work_order:
        return {"error": "Work order not found"}
    
    work_order.status = "completed"
    db.commit()
    
    # Kirim notifikasi WhatsApp
    customer_phone = work_order.customer.phone
    message = f"""
Service Selesai ✅

Work Order: #{work_order.id}
Kendaraan: {work_order.vehicle_plate}

Kendaraan Anda telah selesai diservice dan siap diambil.

Terima kasih!
    """
    
    try:
        send_simple_message(customer_phone, message)
    except Exception as e:
        print(f"Notifikasi WhatsApp gagal: {e}")
    
    return {
        "success": True,
        "message": "Work order completed",
        "data": work_order
    }
```

---

### Use Case 5: Automatic Maintenance Reminder (Scheduler)

```python
# main.py - Setup automatic reminder saat aplikasi start
from fastapi import FastAPI
from services.scheduler_maintenance_reminder import start_scheduler, get_scheduler_status

app = FastAPI()

@app.on_event("startup")
def startup_event():
    """Start scheduler saat aplikasi dimulai"""
    # Jalankan setiap hari jam 7 pagi
    start_scheduler(hour=7, minute=0)
    print("✓ Maintenance reminder scheduler started")

@app.on_event("shutdown")
def shutdown_event():
    """Stop scheduler saat aplikasi shutdown"""
    from services.scheduler_maintenance_reminder import stop_scheduler
    stop_scheduler()

@app.get("/api/scheduler/status")
def check_scheduler():
    """Endpoint untuk cek status scheduler"""
    return get_scheduler_status()
```

**Automatic Flow**:

1. Aplikasi start → Scheduler dimulai
2. Setiap hari jam 07:00 → Job `maintenance_reminder_job()` dijalankan
3. Job mengambil semua customer dengan vehicle
4. Filter yang `next_visit_date` < 3 hari
5. Kirim WhatsApp reminder otomatis
6. Log hasil pengiriman

---

### Use Case 6: Manual Trigger Maintenance Reminder

```python
# Trigger manual via API call
import requests

headers = {
    'Authorization': 'Bearer YOUR_JWT_TOKEN',
    'Content-Type': 'application/json'
}

response = requests.post(
    'http://localhost:8000/customers/send-maintenance-reminder',
    headers=headers
)

result = response.json()

# Display results
print(f"Total Customers: {result['data']['total_customers']}")
print(f"Reminders Sent: {result['data']['reminder_sent']}")
print("\nDetails:")

for detail in result['data']['details']:
    if detail['status'] == 'sent':
        print(f"✓ {detail['no_pol']} - {detail['customer_nama']} - {detail['days_until_visit']} days")
    elif detail['status'] == 'skipped':
        print(f"⊘ {detail['no_pol']} - Skipped: {detail['reason']}")
    elif detail['status'] == 'failed':
        print(f"✗ {detail['no_pol']} - Failed: {detail['reason']}")
```

---

### Use Case 7: Scheduled Reminder for Specific Customer

```python
from services.services_whatsapp import send_scheduled_message
from datetime import datetime, timedelta
from models.database import SessionLocal
from models.model_customer import Customer, Vehicle

def schedule_personal_reminder(customer_id: int):
    """Jadwalkan reminder personal untuk customer tertentu"""
    db = SessionLocal()
    try:
        # Get customer data
        customer = db.query(Customer).filter(Customer.id == customer_id).first()
        if not customer:
            return {"error": "Customer not found"}
        
        # Get vehicle
        vehicle = db.query(Vehicle).filter(Vehicle.customer_id == customer_id).first()
        if not vehicle or not vehicle.next_visit_date:
            return {"error": "Vehicle or next_visit_date not found"}
        
        # Schedule reminder H-3
        reminder_date = vehicle.next_visit_date - timedelta(days=3)
        reminder_time = datetime.combine(reminder_date, datetime.min.time().replace(hour=9, minute=0))
        timestamp_ms = int(reminder_time.timestamp() * 1000)
        
        # Format message
        message = f"""
Halo Bapak {customer.nama},

Reminder: Kendaraan {vehicle.no_pol} Anda terjadwal untuk maintenance pada:
📅 {vehicle.next_visit_date.strftime('%d %B %Y')}

Harap daftarkan melalui nomor pelayanan kami 08551000727

Terima kasih!
        """.strip()
        
        # Send scheduled message
        phone = customer.hp if customer.hp.startswith('62') else '62' + customer.hp[1:]
        result = send_scheduled_message(phone, message, timestamp_ms)
        
        return {
            "success": True,
            "customer": customer.nama,
            "vehicle": vehicle.no_pol,
            "scheduled_at": reminder_time.isoformat(),
            "api_response": result
        }
    finally:
        db.close()
```

---

### Use Case 8: Bulk Reminder dengan Rate Limiting

```python
from services.services_whatsapp import send_simple_message
from models.database import SessionLocal
from models.model_customer import Customer, Vehicle
from datetime import datetime, timedelta
import time

def send_bulk_reminders_with_throttle(days_threshold: int = 3, delay_seconds: int = 2):
    """
    Kirim reminder ke banyak customer dengan rate limiting
    untuk menghindari API throttling
    """
    db = SessionLocal()
    results = {
        "sent": [],
        "failed": [],
        "skipped": []
    }
    
    try:
        # Query vehicles yang akan jatuh tempo
        today = datetime.now().date()
        threshold_date = today + timedelta(days=days_threshold)
        
        vehicles = db.query(Vehicle).join(Customer).filter(
            Vehicle.next_visit_date <= threshold_date,
            Vehicle.next_visit_date >= today
        ).all()
        
        for vehicle in vehicles:
            customer = vehicle.customer
            
            # Validate data
            if not all([customer.nama, customer.hp, vehicle.no_pol]):
                results["skipped"].append({
                    "vehicle": vehicle.no_pol,
                    "reason": "Data tidak lengkap"
                })
                continue
            
            # Format message
            message = f"""
Bapak {customer.nama} untuk nomor kendaraan {vehicle.no_pol} 
sebentar lagi tiba saat pemeliharaan rutin pada tanggal {vehicle.next_visit_date.strftime('%d-%m-%Y')}, 
daftarkan segera melalui nomor pelayanan kami 08551000727
            """.strip()
            
            # Format phone
            phone = customer.hp if customer.hp.startswith('62') else '62' + customer.hp[1:]
            
            try:
                # Send message
                result = send_simple_message(phone, message)
                results["sent"].append({
                    "customer": customer.nama,
                    "vehicle": vehicle.no_pol,
                    "phone": phone
                })
                
                # Delay untuk rate limiting
                time.sleep(delay_seconds)
                
            except Exception as e:
                results["failed"].append({
                    "customer": customer.nama,
                    "vehicle": vehicle.no_pol,
                    "error": str(e)
                })
        
        return {
            "summary": {
                "total": len(vehicles),
                "sent": len(results["sent"]),
                "failed": len(results["failed"]),
                "skipped": len(results["skipped"])
            },
            "details": results
        }
    finally:
        db.close()

# Usage
result = send_bulk_reminders_with_throttle(days_threshold=7, delay_seconds=3)
print(f"Sent: {result['summary']['sent']}/{result['summary']['total']}")
```

---

### Use Case 9: Monitoring & Alert System

```python
from services.scheduler_maintenance_reminder import get_scheduler_status
from services.services_whatsapp import send_simple_message
import logging

logger = logging.getLogger(__name__)

ADMIN_PHONE = "628123456789"  # Nomor HP admin

def check_and_alert_scheduler():
    """
    Monitor scheduler status dan kirim alert ke admin jika ada masalah
    """
    status = get_scheduler_status()
    
    if not status['running']:
        # Scheduler mati - kirim alert
        alert_message = """
🚨 ALERT: Maintenance Reminder Scheduler MATI!

Scheduler tidak berjalan. Harap cek server dan restart scheduler segera.

Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
        """.strip()
        
        try:
            send_simple_message(ADMIN_PHONE, alert_message)
            logger.error("Scheduler down - Alert sent to admin")
        except Exception as e:
            logger.error(f"Failed to send alert: {e}")
        
        return {
            "status": "error",
            "message": "Scheduler is not running",
            "alert_sent": True
        }
    
    # Scheduler running - log info
    logger.info(f"Scheduler running with {len(status['jobs'])} jobs")
    
    for job in status['jobs']:
        logger.info(f"Job: {job['name']} - Next run: {job['next_run_time']}")
    
    return {
        "status": "ok",
        "scheduler": status
    }

# Run monitoring (bisa dijadwalkan dengan cron atau APScheduler lain)
check_and_alert_scheduler()
```

---

### Use Case 10: Dashboard Summary Report

```python
from services.services_customer import send_maintenance_reminder_whatsapp
from services.services_whatsapp import send_message_with_file
from models.database import SessionLocal
from datetime import datetime
import json

def generate_and_send_summary_report(admin_phone: str = "628123456789"):
    """
    Generate summary report dari job reminder dan kirim ke admin
    """
    db = SessionLocal()
    try:
        # Run reminder job
        result = send_maintenance_reminder_whatsapp(db)
        
        # Generate summary message
        summary = f"""
📊 MAINTENANCE REMINDER REPORT
Tanggal: {datetime.now().strftime('%d %B %Y, %H:%M')}

📈 Summary:
• Total Customers: {result['total_customers']}
• Reminders Sent: {result['reminder_sent']}
• Success Rate: {(result['reminder_sent']/result['total_customers']*100) if result['total_customers'] > 0 else 0:.1f}%

📋 Details:
        """.strip()
        
        # Add details
        sent_count = sum(1 for d in result['details'] if d['status'] == 'sent')
        failed_count = sum(1 for d in result['details'] if d['status'] == 'failed')
        skipped_count = sum(1 for d in result['details'] if d['status'] == 'skipped')
        
        summary += f"\n✓ Sent: {sent_count}"
        summary += f"\n✗ Failed: {failed_count}"
        summary += f"\n⊘ Skipped: {skipped_count}"
        
        # List sent reminders
        if sent_count > 0:
            summary += "\n\n📤 Sent to:"
            for detail in result['details']:
                if detail['status'] == 'sent':
                    summary += f"\n• {detail['customer_nama']} ({detail['no_pol']}) - {detail['days_until_visit']} days"
        
        # Send to admin
        send_simple_message(admin_phone, summary)
        
        return {
            "success": True,
            "report_sent": True,
            "summary": result
        }
    except Exception as e:
        # Send error notification
        error_msg = f"❌ Error generating reminder report: {str(e)}"
        send_simple_message(admin_phone, error_msg)
        return {
            "success": False,
            "error": str(e)
        }
    finally:
        db.close()

# Usage - bisa dijadwalkan setelah reminder job selesai
generate_and_send_summary_report(admin_phone="628123456789")
```

---

## Error Handling

### Common Errors

#### 1. API Connection Error

```json
{
  "success": false,
  "message": "Gagal menghubungi API StarSender: Connection timeout"
}
```

**Solusi**:

- Periksa koneksi internet
- Periksa apakah API StarSender sedang down
- Tingkatkan REQUEST_TIMEOUT jika perlu

---

#### 2. Invalid API Key

```json
{
  "success": false,
  "message": "API StarSender error: HTTP 401 - Unauthorized"
}
```

**Solusi**:

- Verifikasi API Key di konfigurasi
- Hubungi StarSender untuk mendapatkan API Key yang valid

---

#### 3. Invalid Phone Number

```json
{
  "success": false,
  "message": "API StarSender error: HTTP 400 - Invalid phone number format"
}
```

**Solusi**:

- Pastikan format nomor: `628123456789` (kode negara + nomor)
- Atau format: `08123456789` (akan dikonversi otomatis oleh API)

---

#### 4. Invalid JSON Response

```json
{
  "success": false,
  "message": "Response API tidak valid JSON: Expecting value: line 1 column 1"
}
```

**Solusi**:

- Periksa response dari API
- Log response untuk debugging

---

### Error Handling Best Practices

```python
from services.services_whatsapp import send_simple_message
import logging

logger = logging.getLogger(__name__)

def safe_send_whatsapp(phone: str, message: str):
    """Wrapper dengan error handling yang robust"""
    try:
        result = send_simple_message(phone, message)
        logger.info(f"WhatsApp terkirim ke {phone}")
        return result
    
    except Exception as e:
        logger.error(f"Gagal kirim WhatsApp ke {phone}: {str(e)}")
        # Jangan throw error, return None agar tidak mengganggu flow utama
        return None
```

---

## Format Nomor Telepon

### Format yang Didukung

1. **Format Internasional** (Recommended):
   - `628123456789` (Indonesia)
   - `60123456789` (Malaysia)

2. **Format Lokal**:
   - `08123456789` (akan dikonversi ke 628123456789)

### Validasi Nomor

```python
def validate_phone_number(phone: str) -> str:
    """Validasi dan normalisasi nomor telepon"""
    # Hapus spasi dan karakter khusus
    phone = phone.replace(" ", "").replace("-", "").replace("(", "").replace(")", "")
    
    # Konversi 08xxx ke 628xxx
    if phone.startswith("08"):
        phone = "62" + phone[1:]
    
    # Validasi panjang (Indonesia: 10-13 digit setelah kode negara)
    if not phone.startswith("62"):
        raise ValueError("Nomor harus dimulai dengan 62 atau 08")
    
    if len(phone) < 12 or len(phone) > 15:
        raise ValueError("Panjang nomor tidak valid")
    
    return phone
```

---

## Rate Limiting

⚠️ **Important**: StarSender API mungkin memiliki rate limit. Sebaiknya implementasikan:

1. **Throttling** pada aplikasi
2. **Queue system** untuk pengiriman massal
3. **Retry mechanism** dengan exponential backoff

### Contoh Queue Implementation

```python
from typing import List
import asyncio

async def send_bulk_messages(messages: List[dict], delay_between_messages: int = 2):
    """Kirim pesan secara bulk dengan delay"""
    results = []
    
    for msg in messages:
        try:
            result = send_simple_message(msg['phone'], msg['message'])
            results.append(result)
            
            # Delay untuk menghindari rate limit
            await asyncio.sleep(delay_between_messages)
        except Exception as e:
            print(f"Error sending to {msg['phone']}: {e}")
            results.append(None)
    
    return results
```

---

## Testing

### Unit Test Example

```python
import pytest
from unittest.mock import patch, MagicMock
from services.services_whatsapp import send_simple_message

def test_send_simple_message_success():
    """Test pengiriman pesan berhasil"""
    with patch('httpx.Client') as mock_client:
        # Mock response
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "success": True,
            "data": {"messageId": "123"},
            "message": "Success"
        }
        
        mock_client.return_value.__enter__.return_value.post.return_value = mock_response
        
        # Execute
        result = send_simple_message("628123456789", "Test message")
        
        # Assert
        assert result["success"] == True
        assert "messageId" in result["data"]


def test_send_simple_message_api_error():
    """Test handling error dari API"""
    with patch('httpx.Client') as mock_client:
        # Mock error response
        mock_response = MagicMock()
        mock_response.status_code = 400
        mock_response.text = "Bad Request"
        
        mock_client.return_value.__enter__.return_value.post.return_value = mock_response
        
        # Execute & Assert
        with pytest.raises(Exception) as exc_info:
            send_simple_message("628123456789", "Test")
        
        assert "API StarSender error" in str(exc_info.value)
```

---

## Security Considerations

### 1. API Key Management

❌ **Jangan**:

```python
STARSENDER_API_KEY = "a234d49a-a181-4a83-964d-0d118b3a6e45"  # Hardcoded
```

✅ **Lakukan**:

```python
import os
from dotenv import load_dotenv

load_dotenv()
STARSENDER_API_KEY = os.getenv("STARSENDER_API_KEY")
```

### 2. Rate Limiting Endpoint

Implementasikan rate limiting untuk mencegah abuse:

```python
from fastapi import APIRouter, Depends
from slowapi import Limiter
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)

@router.post("/whatsapp/send-simple")
@limiter.limit("10/minute")  # Max 10 requests per minute
async def send_simple_whatsapp(phone: str, message: str):
    # ... implementation
```

### 3. Input Validation

Validasi input untuk mencegah injection:

```python
from pydantic import validator

class WhatsAppSendRequest(BaseModel):
    to: str
    body: str
    
    @validator('to')
    def validate_phone(cls, v):
        if not v.replace("+", "").isdigit():
            raise ValueError("Phone number must contain only digits")
        return v
    
    @validator('body')
    def validate_message(cls, v):
        if len(v) > 4096:
            raise ValueError("Message too long (max 4096 chars)")
        return v
```

---

## Troubleshooting

### Problem: Pesan tidak terkirim

**Checklist**:

- [ ] Verifikasi API Key valid
- [ ] Cek koneksi internet
- [ ] Pastikan format nomor telepon benar
- [ ] Cek log error untuk detail
- [ ] Verifikasi StarSender API status

### Problem: File tidak muncul di WhatsApp

**Solusi**:

- Pastikan URL file dapat diakses publik (tidak ada authentication)
- Cek ukuran file (max biasanya 16MB untuk dokumen, 5MB untuk gambar)
- Verifikasi format file didukung

### Problem: Scheduled message tidak terkirim

**Solusi**:

- Pastikan timestamp dalam format milliseconds
- Verifikasi timestamp adalah waktu di masa depan
- Cek timezone server vs timestamp yang dikirim

---

## Troubleshooting

### Problem: Pesan tidak terkirim

**Checklist**:

- [ ] Verifikasi API Key valid
- [ ] Cek koneksi internet
- [ ] Pastikan format nomor telepon benar
- [ ] Cek log error untuk detail
- [ ] Verifikasi StarSender API status

### Problem: File tidak muncul di WhatsApp

**Solusi**:

- Pastikan URL file dapat diakses publik (tidak ada authentication)
- Cek ukuran file (max biasanya 16MB untuk dokumen, 5MB untuk gambar)
- Verifikasi format file didukung

### Problem: Scheduled message tidak terkirim

**Solusi**:

- Pastikan timestamp dalam format milliseconds
- Verifikasi timestamp adalah waktu di masa depan
- Cek timezone server vs timestamp yang dikirim

### Problem: Scheduler tidak berjalan

**Checklist**:

- [ ] Verifikasi `start_scheduler()` dipanggil di startup event
- [ ] Cek logs untuk error scheduler
- [ ] Test manual: `get_scheduler_status()`
- [ ] Pastikan APScheduler terinstall: `pip install apscheduler`

**Debug**:

```python
from services.scheduler_maintenance_reminder import get_scheduler_status

status = get_scheduler_status()
print(f"Running: {status['running']}")
print(f"Jobs: {status['jobs']}")
```

### Problem: Maintenance reminder tidak kirim ke customer tertentu

**Kemungkinan penyebab**:

1. **Data tidak lengkap** (nama, HP, atau no_pol kosong)
   - Solusi: Cek database, pastikan semua field terisi

2. **next_visit_date tidak valid**
   - Solusi: Pastikan format `YYYY-MM-DD` dan tanggal valid

3. **next_visit_date > 3 hari**
   - Solusi: Normal behavior, reminder hanya kirim untuk 0-2 hari ke depan

4. **Format nomor HP salah**
   - Solusi: Pastikan format `08xxx` atau `62xxx`

**Debug specific customer**:

```python
from services.services_customer import getListCustomersWithvehicles
from models.database import SessionLocal

db = SessionLocal()
vehicles = getListCustomersWithvehicles(db)

# Find specific customer
for v in vehicles:
    if v['no_pol'] == 'B 1234 XYZ':  # Replace with actual no_pol
        print(f"Customer: {v['customer_nama']}")
        print(f"HP: {v['customer_hp']}")
        print(f"Next Visit: {v['next_visit_date']}")
        
        # Calculate days
        from datetime import datetime
        if v['next_visit_date']:
            next_visit = datetime.fromisoformat(v['next_visit_date']).date()
            today = datetime.now().date()
            days = (next_visit - today).days
            print(f"Days until visit: {days}")
            print(f"Will send reminder: {0 <= days < 3}")

db.close()
```

### Problem: Too many reminders sent (duplicate)

**Penyebab**: Job berjalan multiple times atau scheduler di-restart berkali-kali

**Solusi**:

1. Pastikan `max_instances=1` di scheduler config
2. Implementasi deduplikasi berdasarkan tanggal pengiriman
3. Simpan log pengiriman di database

**Implementasi Anti-Duplicate**:

```python
# models/model_reminder_log.py
from sqlalchemy import Column, Integer, String, DateTime
from models.database import Base
from datetime import datetime

class ReminderLog(Base):
    __tablename__ = "reminder_logs"
    
    id = Column(Integer, primary_key=True)
    vehicle_id = Column(Integer)
    customer_phone = Column(String)
    sent_at = Column(DateTime, default=datetime.now)
    next_visit_date = Column(String)
    status = Column(String)  # 'sent', 'failed'

# services/services_customer.py - Update logic
def send_maintenance_reminder_whatsapp(db: Session):
    # ... existing code ...
    
    # Before sending, check if already sent today
    from models.model_reminder_log import ReminderLog
    today = datetime.now().date()
    
    for vehicle_data in customers_vehicles:
        # Check log
        existing_log = db.query(ReminderLog).filter(
            ReminderLog.vehicle_id == vehicle_data['vehicle_id'],
            ReminderLog.sent_at >= today
        ).first()
        
        if existing_log:
            details.append({
                "no_pol": vehicle_data['no_pol'],
                "status": "skipped",
                "reason": "Already sent today"
            })
            continue
        
        # Send message...
        # After successful send, log it
        log = ReminderLog(
            vehicle_id=vehicle_data['vehicle_id'],
            customer_phone=phone,
            next_visit_date=next_visit_date.isoformat(),
            status="sent"
        )
        db.add(log)
        db.commit()
```

---

## Best Practices

### 1. Error Logging

Implementasikan logging yang baik untuk monitoring:

```python
import logging
from datetime import datetime

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('whatsapp_reminders.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

# In service function
def send_maintenance_reminder_whatsapp(db: Session):
    logger.info("Starting maintenance reminder job")
    
    try:
        # ... logic ...
        logger.info(f"Reminder sent: {reminder_sent}/{total_customers}")
        
        # Log details
        for detail in details:
            if detail['status'] == 'failed':
                logger.error(f"Failed to send to {detail['no_pol']}: {detail['reason']}")
    
    except Exception as e:
        logger.exception("Error in reminder job")
        raise
```

### 2. Configuration Management

Gunakan environment variables untuk konfigurasi:

```python
# .env
STARSENDER_API_KEY=your_api_key_here
STARSENDER_API_URL=https://api.starsender.online/api/send
REMINDER_SCHEDULER_HOUR=7
REMINDER_SCHEDULER_MINUTE=0
REMINDER_DAYS_THRESHOLD=3
ADMIN_PHONE=628123456789

# config.py
import os
from dotenv import load_dotenv

load_dotenv()

class Settings:
    STARSENDER_API_KEY = os.getenv("STARSENDER_API_KEY")
    STARSENDER_API_URL = os.getenv("STARSENDER_API_URL")
    REMINDER_SCHEDULER_HOUR = int(os.getenv("REMINDER_SCHEDULER_HOUR", 7))
    REMINDER_SCHEDULER_MINUTE = int(os.getenv("REMINDER_SCHEDULER_MINUTE", 0))
    REMINDER_DAYS_THRESHOLD = int(os.getenv("REMINDER_DAYS_THRESHOLD", 3))
    ADMIN_PHONE = os.getenv("ADMIN_PHONE")

settings = Settings()

# Usage
from config import settings
start_scheduler(hour=settings.REMINDER_SCHEDULER_HOUR, minute=settings.REMINDER_SCHEDULER_MINUTE)
```

### 3. Health Check Endpoint

Buat endpoint untuk monitoring scheduler:

```python
from fastapi import APIRouter
from services.scheduler_maintenance_reminder import get_scheduler_status

router = APIRouter(prefix="/health", tags=["Health"])

@router.get("/scheduler")
def check_scheduler_health():
    """Health check for maintenance reminder scheduler"""
    status = get_scheduler_status()
    
    if not status['running']:
        return {
            "status": "unhealthy",
            "scheduler_running": False,
            "error": "Scheduler is not running"
        }
    
    return {
        "status": "healthy",
        "scheduler_running": True,
        "jobs": status['jobs']
    }
```

### 4. Testing Strategy

```python
# tests/test_maintenance_reminder.py
import pytest
from unittest.mock import Mock, patch
from services.services_customer import send_maintenance_reminder_whatsapp
from datetime import datetime, timedelta

def test_send_reminder_within_threshold():
    """Test reminder dikirim untuk vehicle dalam threshold"""
    # Mock database
    mock_db = Mock()
    
    # Mock data - vehicle with next_visit in 2 days
    future_date = (datetime.now() + timedelta(days=2)).date()
    mock_vehicles = [{
        'customer_nama': 'Test Customer',
        'customer_hp': '08123456789',
        'no_pol': 'B 1234 TEST',
        'next_visit_date': future_date.isoformat()
    }]
    
    with patch('services.services_customer.getListCustomersWithvehicles', return_value=mock_vehicles):
        with patch('services.services_customer.send_whatsapp_message_sync', return_value={"success": True}):
            result = send_maintenance_reminder_whatsapp(mock_db)
    
    assert result['total_customers'] == 1
    assert result['reminder_sent'] == 1
    assert result['details'][0]['status'] == 'sent'

def test_no_reminder_outside_threshold():
    """Test reminder tidak dikirim untuk vehicle di luar threshold"""
    mock_db = Mock()
    
    # Mock data - vehicle with next_visit in 5 days (outside threshold)
    future_date = (datetime.now() + timedelta(days=5)).date()
    mock_vehicles = [{
        'customer_nama': 'Test Customer',
        'customer_hp': '08123456789',
        'no_pol': 'B 1234 TEST',
        'next_visit_date': future_date.isoformat()
    }]
    
    with patch('services.services_customer.getListCustomersWithvehicles', return_value=mock_vehicles):
        result = send_maintenance_reminder_whatsapp(mock_db)
    
    assert result['total_customers'] == 1
    assert result['reminder_sent'] == 0  # Should not send
```

### 5. Performance Optimization

Untuk database besar, optimize query:

```python
def getListCustomersWithvehicles_optimized(db: Session):
    """Optimized version - only get vehicles with upcoming maintenance"""
    from datetime import datetime, timedelta
    
    today = datetime.now().date()
    threshold_date = today + timedelta(days=3)
    
    # Only query vehicles within threshold
    vehicles = db.query(Vehicle).join(Customer).filter(
        Vehicle.next_visit_date.isnot(None),
        Vehicle.next_visit_date >= today,
        Vehicle.next_visit_date < threshold_date
    ).all()
    
    return [{
        'customer_nama': v.customer.nama,
        'customer_hp': v.customer.hp,
        'no_pol': v.no_pol,
        'next_visit_date': v.next_visit_date.isoformat() if v.next_visit_date else None,
        'vehicle_id': v.id
    } for v in vehicles]
```

---

## Changelog

### v1.0.0 (Current)

**WhatsApp Messaging:**

- ✅ Implementasi pengiriman pesan text
- ✅ Support file attachment (image, PDF, document)
- ✅ Support scheduled messages
- ✅ Support delay pengiriman
- ✅ JWT authentication pada endpoint utama
- ✅ Error handling komprehensif
- ✅ 4 endpoints WhatsApp (send, send-simple, send-with-file, send-scheduled)

**Maintenance Reminder System:**

- ✅ Automatic scheduler dengan APScheduler
- ✅ Background job berjalan setiap hari (configurable)
- ✅ Deteksi otomatis kendaraan jatuh tempo (< 3 hari)
- ✅ Manual trigger endpoint dengan JWT auth
- ✅ Phone number normalization (08xxx → 62xxx)
- ✅ Comprehensive logging dan status tracking
- ✅ Detailed response dengan status per vehicle

**Services:**

- ✅ 6 service functions (5 WhatsApp + 1 Maintenance)
- ✅ Async dan sync variants
- ✅ Helper functions untuk use case umum

**Schemas:**

- ✅ WhatsAppMessageCreate
- ✅ WhatsAppSendRequest
- ✅ WhatsAppMessageResponse

**Documentation:**

- ✅ Complete API documentation
- ✅ 10 use case examples
- ✅ Error handling guide
- ✅ Troubleshooting section
- ✅ Best practices
- ✅ Testing examples

### Planned Features

**v1.1.0 (Upcoming)**

- 🔄 Database logging untuk message history
- 🔄 Anti-duplicate system untuk reminders
- 🔄 Webhook untuk delivery status
- 🔄 Template message management
- 🔄 Rate limiting per user/endpoint
- 🔄 Retry mechanism dengan exponential backoff
- 🔄 Dashboard untuk monitoring reminders
- 🔄 Custom message templates per customer
- 🔄 Multi-language support

**v2.0.0 (Future)**

- 🔄 Queue system dengan Redis/Celery untuk bulk messages
- 🔄 WhatsApp Business API integration
- 🔄 Media upload service
- 🔄 Campaign management system
- 🔄 Analytics & reporting dashboard
- 🔄 A/B testing untuk messages
- 🔄 Customer segmentation
- 🔄 Automated follow-up sequences

---

## Dependencies

### Required Python Packages

```bash
# Core
fastapi>=0.104.0
uvicorn>=0.24.0
sqlalchemy>=2.0.0
pydantic>=2.0.0

# WhatsApp & HTTP
httpx>=0.25.0

# Scheduler
apscheduler>=3.10.0

# Database (example)
psycopg2-binary>=2.9.0  # For PostgreSQL

# Authentication
python-jose[cryptography]>=3.3.0
passlib[bcrypt]>=1.7.4

# Environment
python-dotenv>=1.0.0
```

**Install all**:

```bash
pip install fastapi uvicorn sqlalchemy pydantic httpx apscheduler python-dotenv
```

### Optional Packages

```bash
# Testing
pytest>=7.4.0
pytest-asyncio>=0.21.0

# Code Quality
black>=23.0.0
flake8>=6.0.0
mypy>=1.5.0

# Monitoring
prometheus-client>=0.18.0
```

---

## Quick Start Guide

### 1. Installation

```bash
# Clone repository
git clone https://github.com/saptadi73/fastapi-bengkel.git
cd fastapi-bengkel

# Install dependencies
pip install -r requirements.txt

# Setup environment
cp .env.example .env
# Edit .env dan isi STARSENDER_API_KEY
```

### 2. Configuration

Edit `.env`:

```bash
# Database
DATABASE_URL=postgresql://user:password@localhost/dbname

# WhatsApp API
STARSENDER_API_KEY=your_api_key_here
STARSENDER_API_URL=https://api.starsender.online/api/send

# Scheduler
REMINDER_SCHEDULER_HOUR=7
REMINDER_SCHEDULER_MINUTE=0
REMINDER_DAYS_THRESHOLD=3

# Admin
ADMIN_PHONE=628123456789
```

### 3. Run Application

```bash
# Development
uvicorn main:app --reload --port 8000

# Production
uvicorn main:app --host 0.0.0.0 --port 8000 --workers 4
```

### 4. Test Endpoints

```bash
# Test WhatsApp send (need JWT token)
curl -X POST "http://localhost:8000/whatsapp/send" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"to": "628123456789", "body": "Test message"}'

# Test simple send (no auth)
curl -X POST "http://localhost:8000/whatsapp/send-simple?phone=628123456789&message=Hello"

# Check scheduler status
curl http://localhost:8000/health/scheduler
```

### 5. Enable Scheduler

Di `main.py`, tambahkan:

```python
from fastapi import FastAPI
from services.scheduler_maintenance_reminder import start_scheduler

app = FastAPI()

@app.on_event("startup")
def startup():
    start_scheduler(hour=7, minute=0)
    print("✓ Scheduler started")
```

### 6. Manual Test Reminder

```bash
# Via API (need JWT token)
curl -X POST "http://localhost:8000/customers/send-maintenance-reminder" \
  -H "Authorization: Bearer YOUR_TOKEN"

# Via Python
python -c "
from services.services_customer import send_maintenance_reminder_whatsapp
from models.database import SessionLocal

db = SessionLocal()
result = send_maintenance_reminder_whatsapp(db)
print(f'Sent: {result[\"reminder_sent\"]}/{result[\"total_customers\"]}')
db.close()
"
```

---

## API Reference Summary

| Endpoint | Method | Auth | Description |
|----------|--------|------|-------------|
| `/whatsapp/send` | POST | ✅ JWT | Kirim WhatsApp dengan semua opsi |
| `/whatsapp/send-simple` | POST | ❌ | Kirim text sederhana |
| `/whatsapp/send-with-file` | POST | ❌ | Kirim dengan attachment |
| `/whatsapp/send-scheduled` | POST | ❌ | Kirim terjadwal |
| `/customers/send-maintenance-reminder` | POST | ✅ JWT | Trigger reminder manual |
| `/health/scheduler` | GET | ❌ | Cek status scheduler |

---

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────┐
│                       FastAPI Application                    │
├─────────────────────────────────────────────────────────────┤
│                                                               │
│  ┌──────────────┐        ┌──────────────┐                   │
│  │   Routes     │        │  Middleware  │                   │
│  │              │        │              │                   │
│  │ - WhatsApp   │───────▶│ - JWT Auth   │                   │
│  │ - Customer   │        │ - CORS       │                   │
│  └──────┬───────┘        └──────────────┘                   │
│         │                                                     │
│         ▼                                                     │
│  ┌──────────────────────────────────────┐                   │
│  │           Services Layer             │                   │
│  │                                      │                   │
│  │  ┌─────────────────────────────┐    │                   │
│  │  │ services_whatsapp.py        │    │                   │
│  │  │ - send_whatsapp_message()   │────┼──┐                │
│  │  │ - send_simple_message()     │    │  │                │
│  │  └─────────────────────────────┘    │  │                │
│  │                                      │  │                │
│  │  ┌─────────────────────────────┐    │  │                │
│  │  │ services_customer.py        │    │  │                │
│  │  │ - send_maintenance_        │    │  │                │
│  │  │   reminder_whatsapp()       │────┼──┤                │
│  │  └─────────────────────────────┘    │  │                │
│  │                                      │  │                │
│  └──────────────────────────────────────┘  │                │
│                                             │                │
│  ┌──────────────────────────────────────┐  │                │
│  │        Background Scheduler          │  │                │
│  │                                      │  │                │
│  │  ┌─────────────────────────────┐    │  │                │
│  │  │ scheduler_maintenance_      │    │  │                │
│  │  │ reminder.py                 │    │  │                │
│  │  │                             │    │  │                │
│  │  │ - APScheduler               │    │  │                │
│  │  │ - CronTrigger (daily 7am)   │────┼──┘                │
│  │  │ - maintenance_reminder_job()│    │                   │
│  │  └─────────────────────────────┘    │                   │
│  └──────────────────────────────────────┘                   │
│                                                               │
│         │                           │                         │
│         ▼                           ▼                         │
│  ┌─────────────┐            ┌─────────────┐                 │
│  │  Database   │            │  StarSender │                 │
│  │             │            │     API     │                 │
│  │ - Customer  │            │             │                 │
│  │ - Vehicle   │            │  WhatsApp   │                 │
│  │ - Reminder  │            │  Gateway    │                 │
│  │   Log       │            │             │                 │
│  └─────────────┘            └─────────────┘                 │
│                                                               │
└─────────────────────────────────────────────────────────────┘
```

### Data Flow: Automatic Reminder

```
1. App Startup
   └─▶ start_scheduler() called in main.py
       └─▶ APScheduler initialized
           └─▶ Job scheduled (daily 7am)

2. Scheduled Time (7:00 AM)
   └─▶ maintenance_reminder_job() triggered
       └─▶ Create DB session
           └─▶ call send_maintenance_reminder_whatsapp(db)
               │
               ├─▶ Query all customers with vehicles
               │
               ├─▶ For each vehicle:
               │   ├─▶ Check next_visit_date
               │   ├─▶ Calculate days_until_visit
               │   ├─▶ If 0-2 days: prepare message
               │   └─▶ send_whatsapp_message_sync()
               │       └─▶ HTTP POST to StarSender API
               │           └─▶ WhatsApp delivered to customer
               │
               └─▶ [NEW] Update whatsapp_report tracking
                   ├─▶ Check existing record (customer_id + vehicle_id)
                   ├─▶ Create or update record
                   ├─▶ Increment frequency
                   └─▶ Update last_message_date
               
               └─▶ Return summary + details

3. Logging
   └─▶ Log results (sent/failed/skipped)
       └─▶ Optional: Alert admin if errors
```

---

## WhatsApp Report Tracking System

**WhatsApp Report** adalah fitur untuk tracking pengiriman pesan WhatsApp ke setiap kombinasi customer dan vehicle. Setiap kali pesan terkirim melalui scheduler maintenance reminder, sistem otomatis mencatat tracking data.

### Features

- ✅ Auto tracking setiap pengiriman WhatsApp
- ✅ Update frequency dan last_message_date otomatis  
- ✅ Statistik agregat (total pesan, average, breakdown)
- ✅ Detail report dengan customer & vehicle info
- ✅ Reset frequency untuk analisis berkala
- ✅ Integration seamless dengan scheduler

### WhatsApp Report Endpoints

**Prefix**: `/whatsapp-report`

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/` | List semua reports |
| GET | `/detail` | List reports dengan detail lengkap |
| GET | `/statistics` | Statistik agregat |
| GET | `/customer/{id}` | Reports untuk customer |
| GET | `/customer/{id}/vehicle/{id}` | Report spesifik |
| DELETE | `/{id}` | Hapus report |
| POST | `/reset-frequency` | Reset frequency |

**Dokumentasi Lengkap**: Lihat [WHATSAPP_REPORT_DOCUMENTATION.md](./WHATSAPP_REPORT_DOCUMENTATION.md)

**Quick Setup**:

```bash
# Create table
python database/create_whatsapp_report_table.py

# Check statistics
curl http://localhost:8000/whatsapp-report/statistics
```

---

## Manual WhatsApp System

**Manual WhatsApp** adalah sistem untuk mengelola customer yang **belum terintegrasi** dengan sistem customer utama (tidak ada di tabel `customer` utama).

### Features

- ✅ Table terpisah `manual_whatsapp` untuk customer manual
- ✅ CRUD operations lengkap
- ✅ Phone number normalization otomatis
- ✅ Bulk import untuk banyak customer
- ✅ Pengiriman reminder manual/otomatis
- ✅ Tracking reminder per customer
- ✅ Status aktif/tidak aktif
- ✅ Statistics dan reporting

### Manual WhatsApp Endpoints

**Prefix**: `/manual-whatsapp`

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/` | Buat customer manual |
| GET | `/` | List semua customer |
| GET | `/{id}` | Detail by ID |
| GET | `/by-nopol/{nopol}` | Detail by nopol |
| PUT | `/{id}` | Update data |
| PATCH | `/{id}/toggle-active` | Toggle aktif/non-aktif |
| DELETE | `/{id}` | Hapus data |
| POST | `/send-reminders` | Kirim reminder ke semua |
| POST | `/{id}/send-reminder` | Kirim reminder ke satu |
| POST | `/bulk-import` | Bulk import array JSON |
| GET | `/stats/summary` | Statistik ringkas |

**Dokumentasi Lengkap**: Lihat [MANUAL_WHATSAPP_DOCUMENTATION.md](./MANUAL_WHATSAPP_DOCUMENTATION.md)

**Quick Setup**:

```bash
# Create table
python database/create_manual_whatsapp_table.py

# Bulk import
curl -X POST "http://localhost:8000/manual-whatsapp/bulk-import" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "customers": [
      {
        "customer_name": "John Doe",
        "nopol": "B 1234 XYZ",
        "no_hp": "08123456789",
        "next_service": "2026-04-01"
      }
    ]
  }'
```

---

## Support & Contact

Jika ada pertanyaan atau masalah terkait implementasi WhatsApp API:

1. Cek dokumentasi ini terlebih dahulu
2. Review error logs aplikasi
3. Cek dokumentasi StarSender: [https://api.starsender.online](https://api.starsender.online)
4. Hubungi tim development

---

**Last Updated**: January 3, 2026  
**Version**: 1.0.0  
**Maintained by**: FastAPI Bengkel Development Team
