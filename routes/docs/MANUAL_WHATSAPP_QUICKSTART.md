# Manual WhatsApp - Quick Start Guide

## 1️⃣ Setup (5 menit)

### Step 1: Create Table

```bash
cd c:\projek\fastapi-bengkel
python database/create_manual_whatsapp_table.py
```

Output yang diharapkan:
```
✓ Table 'manual_whatsapp' created successfully
```

### Step 2: Register Model (Optional, jika belum ada)

Edit `models/__init__.py`:
```python
from models.manual_whatsapp import ManualWhatsApp
```

### Step 3: Register Routes di main.py

```python
from routes.routes_manual_whatsapp import router as manual_whatsapp_router

app.include_router(manual_whatsapp_router)
```

### Step 4: Restart Server

```bash
uvicorn main:app --reload
```

---

## 2️⃣ Tambah Customer Manual

### Via API (cURL)

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

### Via Python Script

```python
import requests

headers = {
    'Authorization': 'Bearer YOUR_JWT_TOKEN',
    'Content-Type': 'application/json'
}

data = {
    "customer_name": "Bapak Joko",
    "nopol": "B 1234 XYZ",
    "no_hp": "08123456789",
    "next_service": "2026-01-15"
}

response = requests.post(
    'http://localhost:8000/manual-whatsapp/',
    headers=headers,
    json=data
)

print(response.json())
```

---

## 3️⃣ Bulk Import dari Excel

### Prepare Excel File: `manual_customers.xlsx`

| Nama | No Pol | No HP | Last Service | Next Service | Notes |
|------|--------|-------|--------------|--------------|-------|
| Bapak Joko | B 1234 XYZ | 08123456789 | 2025-10-15 | 2026-01-15 | VIP |
| Ibu Siti | B 5678 ABC | 08987654321 | | 2026-01-20 | |

### Script untuk Import

```python
import pandas as pd
import requests
from datetime import datetime

# Read Excel
df = pd.read_excel('manual_customers.xlsx')

# Prepare data
records = []
for _, row in df.iterrows():
    records.append({
        "customer_name": row['Nama'],
        "nopol": row['No Pol'],
        "no_hp": row['No HP'],
        "last_service": row['Last Service'] if pd.notna(row['Last Service']) else None,
        "next_service": row['Next Service'] if pd.notna(row['Next Service']) else None,
        "notes": row.get('Notes', '')
    })

# Import
headers = {
    'Authorization': 'Bearer YOUR_JWT_TOKEN',
    'Content-Type': 'application/json'
}

response = requests.post(
    'http://localhost:8000/manual-whatsapp/bulk-import',
    headers=headers,
    json=records
)

result = response.json()
print(f"Imported: {result['data']['imported']}/{result['data']['total']}")

if result['data']['failures']:
    print("\nFailures:")
    for failure in result['data']['failures']:
        print(f"  - {failure['customer_name']}: {failure['error']}")
```

---

## 4️⃣ Kirim Reminder WhatsApp

### Manual Trigger Semua Customer

```bash
curl -X POST "http://localhost:8000/manual-whatsapp/send-reminders" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "days_threshold": 3,
    "only_active": true
  }'
```

### Kirim ke Customer Spesifik

```bash
curl -X POST "http://localhost:8000/manual-whatsapp/550e8400-e29b-41d4-a716-446655440000/send-reminder" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"
```

---

## 5️⃣ View & Manage Customers

### Lihat Semua

```bash
curl -X GET "http://localhost:8000/manual-whatsapp/" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"
```

### Lihat Hanya Active

```bash
curl -X GET "http://localhost:8000/manual-whatsapp/?active_only=true" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"
```

### Lihat Detail by Nopol

```bash
curl -X GET "http://localhost:8000/manual-whatsapp/by-nopol/B%201234%20XYZ" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"
```

### Update Customer

```bash
curl -X PUT "http://localhost:8000/manual-whatsapp/550e8400-e29b-41d4-a716-446655440000" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "next_service": "2026-02-01"
  }'
```

### Deactivate Customer

```bash
curl -X PATCH "http://localhost:8000/manual-whatsapp/550e8400-e29b-41d4-a716-446655440000/toggle-active" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"
```

### Delete Customer

```bash
curl -X DELETE "http://localhost:8000/manual-whatsapp/550e8400-e29b-41d4-a716-446655440000" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"
```

---

## 6️⃣ Statistik & Monitoring

```bash
curl -X GET "http://localhost:8000/manual-whatsapp/stats/summary" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"
```

Response:
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

---

## 7️⃣ Setup Automatic Daily Reminder

Tambahkan di `main.py`:

```python
from apscheduler.schedulers.background import BackgroundScheduler
from services.services_manual_whatsapp import send_reminder_to_manual_customers
from models.database import SessionLocal
import logging

logger = logging.getLogger(__name__)

def manual_whatsapp_reminder_job():
    db = SessionLocal()
    try:
        result = send_reminder_to_manual_customers(db, days_threshold=3)
        logger.info(f"Manual WhatsApp: {result['reminder_sent']}/{result['total_records']} sent")
    except Exception as e:
        logger.error(f"Error: {str(e)}")
    finally:
        db.close()

# Create scheduler
scheduler = BackgroundScheduler()
scheduler.add_job(
    manual_whatsapp_reminder_job,
    'cron',
    hour=9,      # 9 AM
    minute=0,
    id='manual_whatsapp_reminder',
    replace_existing=True
)
scheduler.start()

# Di startup event
@app.on_event("startup")
def startup():
    # Scheduler sudah di-start di atas
    print("✓ Manual WhatsApp scheduler started")
```

---

## 📊 Common Tasks

### Task 1: Import Customer dari Text File

```python
# Jika data dalam format text (comma-separated)
lines = """
Bapak Joko,B 1234 XYZ,08123456789,2026-01-15
Ibu Siti,B 5678 ABC,08987654321,2026-01-20
Pak Budi,B 9999 DEF,08555123456,2026-01-25
"""

records = []
for line in lines.strip().split('\n'):
    name, nopol, phone, next_service = line.split(',')
    records.append({
        "customer_name": name.strip(),
        "nopol": nopol.strip(),
        "no_hp": phone.strip(),
        "next_service": next_service.strip()
    })

# Bulk import
requests.post(
    'http://localhost:8000/manual-whatsapp/bulk-import',
    headers=headers,
    json=records
)
```

### Task 2: Export Customers to CSV

```python
import requests
import csv

headers = {'Authorization': 'Bearer YOUR_JWT_TOKEN'}

response = requests.get(
    'http://localhost:8000/manual-whatsapp/',
    headers=headers
)

data = response.json()

# Export to CSV
with open('manual_customers_export.csv', 'w', newline='', encoding='utf-8') as f:
    writer = csv.writer(f)
    writer.writerow(['ID', 'Customer Name', 'Nopol', 'Phone', 'Next Service', 'Status'])
    
    for record in data['data']:
        writer.writerow([
            record['id'],
            record['customer_name'],
            record['nopol'],
            record['no_hp'],
            record['next_service'],
            'Active' if record['is_active'] == 1 else 'Inactive'
        ])

print("✓ Export completed: manual_customers_export.csv")
```

### Task 3: Send Reminder to Customers Due This Week

```python
from datetime import date, timedelta

headers = {'Authorization': 'Bearer YOUR_JWT_TOKEN'}

# Get all customers
response = requests.get(
    'http://localhost:8000/manual-whatsapp/',
    headers=headers
)

data = response.json()
today = date.today()
week_later = today + timedelta(days=7)

# Find customers with service this week
for record in data['data']:
    if record['next_service']:
        next_service = date.fromisoformat(record['next_service'])
        if today <= next_service <= week_later:
            # Send reminder
            requests.post(
                f"http://localhost:8000/manual-whatsapp/{record['id']}/send-reminder",
                headers=headers
            )
```

---

## ⚠️ Troubleshooting

### Error: "Record tidak ditemukan"
- Check record ID atau nopol benar
- Pastikan record exists dengan GET request terlebih dahulu

### Error: "Nopol sudah terdaftar"
- Nopol harus unik
- Cek apakah sudah ada yang sama

### Error: "Data customer tidak lengkap"
- Pastikan customer_name, nopol, no_hp, dan next_service terisi
- last_service opsional

### Reminder tidak terkirim
- Check WhatsApp API key valid
- Check phone number format (harus 62xxx)
- Check StarSender API status
- Lihat logs untuk detail error

---

**Happy Manual WhatsApp Sending! 🎉**
