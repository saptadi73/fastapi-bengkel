# WhatsApp Report - Quick Start Guide

## Setup dalam 3 Langkah

### 1️⃣ Buat Table
```bash
python database/create_whatsapp_report_table.py
```

### 2️⃣ Mulai Scheduler
```bash
curl -X POST "http://localhost:8000/scheduler/maintenance-reminder/start"
```

### 3️⃣ Tracking Otomatis Berjalan!
Setiap pesan WhatsApp yang terkirim otomatis tercatat di `whatsapp_report` table.

---

## Lihat Hasilnya

### 📊 Statistik Keseluruhan
```bash
curl http://localhost:8000/whatsapp-report/statistics
```

Response:
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

### 👤 Detail Per Customer+Vehicle
```bash
curl http://localhost:8000/whatsapp-report/detail
```

Response:
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

## Endpoints Tersedia

| Method | Endpoint | Keterangan |
|--------|----------|-----------|
| GET | `/whatsapp-report/` | List semua reports |
| GET | `/whatsapp-report/detail` | List reports dengan detail |
| GET | `/whatsapp-report/statistics` | Statistik agregat |
| GET | `/whatsapp-report/customer/{id}` | Reports untuk customer |
| GET | `/whatsapp-report/customer/{id}/vehicle/{id}` | Report spesifik |
| DELETE | `/whatsapp-report/{id}` | Hapus report |
| POST | `/whatsapp-report/reset-frequency` | Reset frequency |

---

## Apa yang Tercatat?

Setiap kali pesan WhatsApp berhasil terkirim via scheduler:

| Field | Nilai |
|-------|-------|
| `id_customer` | UUID customer yang menerima pesan |
| `id_vehicle` | UUID vehicle yang dirujuk dalam pesan |
| `last_message_date` | Tanggal pesan terakhir dikirim |
| `frequency` | Total berapa kali pesan dikirim |
| `created_at` | Kapan record pertama kali dibuat |
| `updated_at` | Kapan record terakhir di-update |

---

## Kode yang Dimodifikasi

### ✅ File Baru Dibuat:
- `models/whatsapp_report.py` - Model database
- `schemas/whatsapp_report.py` - Pydantic schemas
- `services/services_whatsapp_report.py` - Business logic
- `routes/routes_whatsapp_report.py` - API endpoints
- `database/create_whatsapp_report_table.py` - Table creation
- `WHATSAPP_REPORT_DOCUMENTATION.md` - Dokumentasi lengkap

### ✅ File yang Dimodifikasi:
- `services/services_customer.py` - Update `send_maintenance_reminder_whatsapp()` untuk track report
- `models/__init__.py` - Import WhatsappReport model

---

## Auto-Registration

✅ Routes otomatis ter-register di main.py (tidak perlu manual edit)
✅ Model otomatis ter-import di models/database.py

---

## Database Structure

```sql
CREATE TABLE whatsapp_report (
  id UUID PRIMARY KEY,
  id_customer UUID NOT NULL (FK → customer.id),
  id_vehicle UUID NOT NULL (FK → vehicle.id),
  last_message_date DATETIME,
  frequency INTEGER DEFAULT 0,
  created_at DATETIME DEFAULT now(),
  updated_at DATETIME DEFAULT now(),
  
  FOREIGN KEY (id_customer) REFERENCES customer(id),
  FOREIGN KEY (id_vehicle) REFERENCES vehicle(id)
);
```

---

## Use Cases

### 📱 Monitor Pengiriman WhatsApp
Lihat berapa pesan yang sudah terkirim ke setiap customer+vehicle.

### 📈 Analisis Engagement
Cek customer mana yang paling sering menerima pesan (highest frequency).

### 🔄 Reset Bulanan
Reset frequency setiap bulan untuk tracking yang akurat.

### 🎯 Target Marketing
Identifikasi customer yang belum pernah dikirim pesan atau jarang dikirim.

---

## Notes

- ⚙️ Tracking berjalan otomatis saat scheduler aktif
- 🛡️ Error handling yang baik (tidak akan stop pengiriman pesan)
- 📊 Data selalu up-to-date setiap kali ada pengiriman
- 🔑 Gunakan UUID dari customer dan vehicle untuk query yang akurat
- 💾 Jangan lupa backup sebelum reset frequency

---

## Referensi Lengkap

Untuk dokumentasi detail, lihat: [WHATSAPP_REPORT_DOCUMENTATION.md](./WHATSAPP_REPORT_DOCUMENTATION.md)
