# Dokumentasi: WhatsApp Maintenance Reminder Otomatis

## Deskripsi

Fitur ini memungkinkan sistem untuk mengirim reminder WhatsApp secara otomatis kepada pelanggan 3 hari sebelum jadwal maintenance rutin mereka. 

**Format Pesan:**
```
Bapak {nama_pelanggan} untuk nomor kendaraan {no_pol} sebentar lagi tiba saat pemeliharaan rutin pada tanggal {next_visit_date}, daftarkan segera melalui nomor pelayanan kami 087740659525
```

## Komponen Sistem

### 1. **Service Function** (`services/services_customer.py`)

**Function:** `send_maintenance_reminder_whatsapp(db: Session)`

```python
def send_maintenance_reminder_whatsapp(db: Session):
    """
    Mengirim reminder WhatsApp ke customer yang jadwal maintenance-nya
    kurang dari 3 hari.
    """
    # Returns:
    # {
    #     "total_customers": int,
    #     "reminder_sent": int,
    #     "details": list of dicts with vehicle info dan status pengiriman
    # }
```

**Logic:**
1. Mengambil list customer dengan vehicle dari `getListCustomersWithvehicles()`
2. Untuk setiap vehicle, mengecek apakah `next_visit_date` kurang dari 3 hari dari hari ini
3. Jika kondisi terpenuhi:
   - Format nomor HP ke format internasional (62xxx)
   - Siapkan pesan dengan format yang ditentukan
   - Kirim via WhatsApp menggunakan `send_whatsapp_message_sync()`
   - Log detail pengiriman (berhasil/gagal)

### 2. **Scheduler** (`services/scheduler_maintenance_reminder.py`)

**Functions:**
- `start_scheduler(hour: int = 7, minute: int = 0)` - Mulai scheduler
- `stop_scheduler()` - Hentikan scheduler
- `get_scheduler_status()` - Cek status scheduler
- `maintenance_reminder_job()` - Job yang dijalankan scheduler

**Features:**
- Menggunakan APScheduler dengan background thread
- Configurable waktu eksekusi (jam dan menit)
- Max 1 instance job untuk menghindari duplikasi
- Logging untuk setiap eksekusi

### 3. **Routes** (`routes/routes_scheduler.py`)

#### a. Start Scheduler
```
POST /scheduler/maintenance-reminder/start
Query Parameters:
  - hour: 0-23 (default: 7)
  - minute: 0-59 (default: 0)

Response:
{
  "success": true,
  "data": {
    "message": "Scheduler dimulai. Job akan berjalan setiap hari jam 07:00"
  }
}
```

#### b. Stop Scheduler
```
POST /scheduler/maintenance-reminder/stop

Response:
{
  "success": true,
  "data": {
    "message": "Scheduler dihentikan"
  }
}
```

#### c. Get Status
```
GET /scheduler/maintenance-reminder/status

Response:
{
  "success": true,
  "data": {
    "running": true,
    "jobs": [
      {
        "id": "maintenance_reminder_job",
        "name": "Maintenance Reminder WhatsApp",
        "next_run_time": "2025-12-15T07:00:00+07:00",
        "trigger": "cron[hour='7', minute='0']"
      }
    ]
  }
}
```

#### d. Run Now (Manual Trigger)
```
POST /scheduler/maintenance-reminder/run-now

Response:
{
  "success": true,
  "data": {
    "total_customers": 50,
    "reminder_sent": 5,
    "details": [
      {
        "no_pol": "B 1234 ABC",
        "customer_nama": "Budi Santoso",
        "customer_hp": "08551234567",
        "next_visit_date": "2025-12-18",
        "days_until_visit": 1,
        "status": "sent",
        "message": "Bapak Budi Santoso untuk nomor kendaraan B 1234 ABC sebentar lagi tiba saat pemeliharaan rutin pada tanggal 18-12-2025, daftarkan segera melalui nomor pelayanan kami 087740659525",
        "api_response": "Message sent successfully"
      },
      ...
    ]
  }
}
```

### 4. **Customer Route** (`routes/routes_customer.py`)

Manual trigger tanpa scheduler:
```
POST /customers/send-maintenance-reminder

Response: Sama seperti Run Now
```

## Cara Penggunaan

### Option 1: Auto-Start Scheduler

Uncomment baris berikut di `main.py`:

```python
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    print("🚀 FastAPI Aplikasi sedang startup...")
    from services.scheduler_maintenance_reminder import start_scheduler
    start_scheduler(hour=7, minute=0)  # Setiap hari jam 7 pagi
    print("✓ Aplikasi siap digunakan")
    ...
```

### Option 2: Manual Start via API

```bash
# Start scheduler (jam 7 pagi)
curl -X POST "http://localhost:8000/scheduler/maintenance-reminder/start?hour=7&minute=0" \
  -H "Authorization: Bearer YOUR_TOKEN"

# Cek status
curl -X GET "http://localhost:8000/scheduler/maintenance-reminder/status" \
  -H "Authorization: Bearer YOUR_TOKEN"

# Run sekarang
curl -X POST "http://localhost:8000/scheduler/maintenance-reminder/run-now" \
  -H "Authorization: Bearer YOUR_TOKEN"

# Stop scheduler
curl -X POST "http://localhost:8000/scheduler/maintenance-reminder/stop" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

### Option 3: Manual Trigger (Tidak Perlu Scheduler)

```bash
curl -X POST "http://localhost:8000/customers/send-maintenance-reminder" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

## Detail Implementasi

### Logika Penentuan Recipient

Reminder dikirim jika **0 ≤ days_until_visit < 3**, artinya:
- **0 hari:** Maintenance hari ini
- **1 hari:** Maintenance besok
- **2 hari:** Maintenance lusa

### Format Nomor Telepon

Sistem otomatis mengkonversi nomor HP ke format internasional:
- Input: `08551234567` → Output: `628551234567`
- Input: `628551234567` → Output: `628551234567`
- Input: `+628551234567` → Output: `628551234567`

### Handling Error

Jika ada error saat mengirim ke satu customer, sistem akan:
1. Log error dengan detail customer
2. Lanjut ke customer berikutnya (tidak stop keseluruhan)
3. Return dalam `details` dengan `status: "failed"` dan `reason: "error message"`

### Database Query

Sistem query:
1. Vehicle dengan `next_visit_date` (dihitung dari `last_visit_date + 4 bulan`)
2. Customer info untuk setiap vehicle
3. Nomor HP dari `customer.hp`

## Dependencies

- `apscheduler`: Background job scheduler
- `httpx`: HTTP client untuk WhatsApp API
- `fastapi`: Web framework
- `sqlalchemy`: ORM
- `pydantic`: Data validation
- `python-dotenv`: Environment variables loader

Install:
```bash
pip install apscheduler httpx fastapi sqlalchemy pydantic python-dotenv
```

## Konfigurasi

### Environment Variables

Buat file `.env` di root project:

```env
# WhatsApp API Configuration
STARSENDER_API_KEY=your_api_key_here

# Database Configuration
DATABASE_URL=postgresql+psycopg2://username:password@localhost:5432/database_name
```

Setup:
1. Copy `.env.example` ke `.env`
2. Isi nilai sesuai konfigurasi Anda
3. File `.env` otomatis diabaikan oleh git (sudah ada di `.gitignore`)

## Catatan Penting

1. **JWT Authentication:** Semua endpoint scheduler memerlukan JWT token
2. **Timezone:** Scheduler menggunakan timezone lokal sistem
3. **Database Connection:** Scheduler membuat koneksi DB baru setiap kali job dijalankan
4. **Environment Variables:** API key dan DATABASE_URL sekarang menggunakan file `.env` untuk keamanan
5. **Multiple Instances:** Jika menjalankan multiple instances aplikasi, gunakan scheduler external (seperti systemd timer atau cron) daripada built-in scheduler

## Troubleshooting

### Scheduler tidak jalan
- Cek apakah scheduler sudah di-start: `GET /scheduler/maintenance-reminder/status`
- Lihat logs untuk error message

### Pesan tidak terkirim
- Verify WhatsApp API key di file `.env` valid dan terdaftar
- Cek format nomor HP customer (harus ada di database)
- Lihat response detail di `status: "failed"` untuk error message
- Pastikan `python-dotenv` sudah terinstall

### Database Connection Error
- Pastikan `DATABASE_URL` di `.env` sudah benar
- Format: `postgresql+psycopg2://user:password@host:port/database`
- Pastikan database server sudah running

### Job berjalan lebih dari 1x
- Max instances sudah set ke 1, jika masih ada issue check APScheduler version

## Contoh Data Customer

```json
{
  "customer_nama": "Budi Santoso",
  "customer_hp": "08551234567",
  "no_pol": "B 1234 ABC",
  "next_visit_date": "2025-12-18",
  "last_visit_date": "2025-08-18"
}
```

Jika hari ini adalah 2025-12-16, maka customer ini akan menerima reminder karena `next_visit_date - today = 2 hari`.
