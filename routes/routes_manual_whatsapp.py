"""
Routes untuk Manual WhatsApp API
Endpoint untuk CRUD operations dan pengiriman WhatsApp manual customers
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from models.database import SessionLocal
from schemas.manual_whatsapp import (
    ManualWhatsAppCreate,
    ManualWhatsAppUpdate,
    ManualWhatsAppResponse,
    ManualWhatsAppListResponse,
    SendReminderRequest,
    SendReminderResponse,
    SendCustomMessageRequest,
    SendCustomMessageResponse
)
from services.services_manual_whatsapp import (
    create_manual_whatsapp,
    get_manual_whatsapp_by_id,
    get_manual_whatsapp_by_nopol,
    get_all_manual_whatsapp,
    update_manual_whatsapp,
    delete_manual_whatsapp,
    send_reminder_to_manual_customers,
    bulk_import_manual_whatsapp,
    send_custom_whatsapp_message
)
from supports.utils_json_response import success_response, error_response
from middleware.jwt_required import jwt_required
from typing import List

router = APIRouter(prefix="/manual-whatsapp", tags=["Manual WhatsApp"])


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# ============= CREATE OPERATIONS =============

@router.post("/", response_model=ManualWhatsAppResponse)
def create_manual_customer(
    data: ManualWhatsAppCreate,
    db: Session = Depends(get_db),
    _=Depends(jwt_required)
):
    """
    Create record manual WhatsApp baru untuk customer yang belum terintegrasi
    
    **Required fields:**
    - customer_name: Nama customer
    - nopol: Nomor polisi kendaraan (harus unik)
    - no_hp: Nomor HP customer (format: 08xxx atau 62xxx)
    
    **Optional fields:**
    - last_service: Tanggal service terakhir
    - next_service: Tanggal service berikutnya
    - notes: Catatan tambahan
    
    **Example Request:**
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
    """
    try:
        result = create_manual_whatsapp(db, data)
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/bulk-import", status_code=201)
def bulk_import_customers(
    records: List[ManualWhatsAppCreate],
    db: Session = Depends(get_db),
    _=Depends(jwt_required)
):
    """
    Bulk import multiple manual WhatsApp records sekaligus
    
    **Example Request:**
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
        }
    ]
    ```
    """
    try:
        if not records:
            raise ValueError("Records tidak boleh kosong")
        
        result = bulk_import_manual_whatsapp(db, records)
        return success_response(
            data=result,
            message=f"Import selesai. {result['imported']} berhasil, {result['failed']} gagal"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ============= READ OPERATIONS =============

@router.get("/", response_model=ManualWhatsAppListResponse)
def get_all_manual_customers(
    active_only: bool = False,
    db: Session = Depends(get_db),
    _=Depends(jwt_required)
):
    """
    Get semua record manual WhatsApp
    
    **Query Parameters:**
    - active_only: Hanya tampilkan customer aktif (default: false)
    
    **Response:**
    - total: Total records
    - active: Jumlah customer aktif
    - inactive: Jumlah customer tidak aktif
    - data: List dari records
    """
    try:
        result = get_all_manual_whatsapp(db, active_only)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{record_id}", response_model=ManualWhatsAppResponse)
def get_manual_customer_by_id(
    record_id: str,
    db: Session = Depends(get_db),
    _=Depends(jwt_required)
):
    """
    Get detail manual WhatsApp record by ID
    
    **Path Parameters:**
    - record_id: Record ID (UUID)
    """
    try:
        result = get_manual_whatsapp_by_id(db, record_id)
        if not result:
            raise HTTPException(status_code=404, detail="Record tidak ditemukan")
        return result
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/by-nopol/{nopol}", response_model=ManualWhatsAppResponse)
def get_manual_customer_by_nopol(
    nopol: str,
    db: Session = Depends(get_db),
    _=Depends(jwt_required)
):
    """
    Get detail manual WhatsApp record by nopol
    
    **Path Parameters:**
    - nopol: Nomor polisi kendaraan
    """
    try:
        result = get_manual_whatsapp_by_nopol(db, nopol)
        if not result:
            raise HTTPException(status_code=404, detail=f"Nopol {nopol} tidak ditemukan")
        return result
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ============= UPDATE OPERATIONS =============

@router.put("/{record_id}", response_model=ManualWhatsAppResponse)
def update_manual_customer(
    record_id: str,
    data: ManualWhatsAppUpdate,
    db: Session = Depends(get_db),
    _=Depends(jwt_required)
):
    """
    Update record manual WhatsApp
    
    **Path Parameters:**
    - record_id: Record ID (UUID)
    
    **Request Body:**
    Semua field opsional. Hanya field yang di-submit akan diupdate.
    
    **Example Request:**
    ```json
    {
        "next_service": "2026-02-01",
        "is_active": 1
    }
    ```
    """
    try:
        result = update_manual_whatsapp(db, record_id, data)
        if not result:
            raise HTTPException(status_code=404, detail="Record tidak ditemukan")
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.patch("/{record_id}/toggle-active", response_model=ManualWhatsAppResponse)
def toggle_active_status(
    record_id: str,
    db: Session = Depends(get_db),
    _=Depends(jwt_required)
):
    """
    Toggle status aktif/tidak aktif untuk customer
    
    **Path Parameters:**
    - record_id: Record ID (UUID)
    """
    try:
        record = get_manual_whatsapp_by_id(db, record_id)
        if not record:
            raise HTTPException(status_code=404, detail="Record tidak ditemukan")
        
        # Toggle status
        new_status = 0 if record['is_active'] == 1 else 1
        update_data = ManualWhatsAppUpdate(is_active=new_status)
        result = update_manual_whatsapp(db, record_id, update_data)
        
        return result
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ============= DELETE OPERATIONS =============

@router.delete("/{record_id}", status_code=204)
def delete_manual_customer(
    record_id: str,
    db: Session = Depends(get_db),
    _=Depends(jwt_required)
):
    """
    Delete record manual WhatsApp
    
    **Path Parameters:**
    - record_id: Record ID (UUID)
    """
    try:
        success = delete_manual_whatsapp(db, record_id)
        if not success:
            raise HTTPException(status_code=404, detail="Record tidak ditemukan")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ============= WHATSAPP OPERATIONS =============

@router.post("/send-reminders", response_model=SendReminderResponse)
def send_reminders(
    request: SendReminderRequest,
    db: Session = Depends(get_db),
    _=Depends(jwt_required)
):
    """
    Kirim reminder WhatsApp ke manual customers yang next_service dalam X hari
    
    **Request Body:**
    - days_threshold: Kirim reminder jika next_service dalam X hari (default: 3)
    - only_active: Hanya kirim ke customer aktif (default: true)
    
    **Example Request:**
    ```json
    {
        "days_threshold": 3,
        "only_active": true
    }
    ```
    
    **Response:**
    - total_records: Total records yang diproses
    - reminder_sent: Jumlah reminder berhasil dikirim
    - reminder_failed: Jumlah reminder gagal
    - details: Detail setiap pengiriman
    """
    try:
        result = send_reminder_to_manual_customers(
            db,
            days_threshold=request.days_threshold,
            only_active=request.only_active
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/{record_id}/send-reminder", status_code=200)
def send_reminder_to_specific_customer(
    record_id: str,
    db: Session = Depends(get_db),
    _=Depends(jwt_required)
):
    """
    Kirim reminder WhatsApp ke customer spesifik (tanpa melihat threshold tanggal)
    
    **Path Parameters:**
    - record_id: Record ID (UUID)
    
    **Useful for:**
    - Manual trigger reminder kapan saja
    - Testing pengiriman WhatsApp
    - Emergency reminder
    """
    try:
        from services.services_whatsapp import send_whatsapp_message_sync
        from schemas.service_whatsapp import WhatsAppMessageCreate
        
        # Get record
        record = get_manual_whatsapp_by_id(db, record_id)
        if not record:
            raise HTTPException(status_code=404, detail="Record tidak ditemukan")
        
        # Validate data
        if not all([record['customer_name'], record['no_hp'], record['nopol'], record['next_service']]):
            raise HTTPException(status_code=400, detail="Data customer tidak lengkap")
        
        # Prepare message
        from datetime import datetime
        next_service_date = datetime.fromisoformat(record['next_service']).date()
        
        message = f"""
Halo Bapak {record['customer_name']},

Kami mengingatkan bahwa kendaraan dengan nomor polisi {record['nopol']} Anda akan jatuh tempo untuk service maintenance pada:

📅 {next_service_date.strftime('%d %B %Y')}

Mohon segera menghubungi kami untuk melakukan penjadwalan service:
📞 08551000727

Terima kasih atas kepercayaan Anda.
        """.strip()
        
        # Send WhatsApp
        msg_data = WhatsAppMessageCreate(
            message_type="text",
            to=record['no_hp'],
            body=message,
            file=None,
            delay=None,
            schedule=None
        )
        result = send_whatsapp_message_sync(msg_data)
        
        # Update reminder count
        from datetime import datetime as dt
        from sqlalchemy import update as sqlalchemy_update
        from models.manual_whatsapp import ManualWhatsApp
        
        db.execute(
            sqlalchemy_update(ManualWhatsApp).where(ManualWhatsApp.id == record_id).values(
                reminder_sent_count=ManualWhatsApp.reminder_sent_count + 1,
                last_reminder_sent=dt.utcnow()
            )
        )
        db.commit()
        
        return success_response(
            data={
                "id": record_id,
                "customer_name": record['customer_name'],
                "nopol": record['nopol'],
                "status": "sent",
                "message": message,
                "api_response": result.get("message") if isinstance(result, dict) else str(result)
            },
            message="Reminder berhasil dikirim"
        )
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/send-custom-message", response_model=SendCustomMessageResponse)
def send_custom_message(
    request: SendCustomMessageRequest,
    _=Depends(jwt_required)
):
    """
    Kirim custom WhatsApp message ke nomor yang ditentukan (tidak harus ada di database)
    
    **Use Cases:**
    - Kirim pesan promosi manual
    - Kirim reminder custom
    - Kirim notifikasi khusus
    - Testing pengiriman WhatsApp
    
    **Request Body:**
    - no_hp: Nomor HP tujuan (format: 62xxx atau 08xxx)
    - message: Isi pesan WhatsApp (custom dari front-end)
    
    **Example Request:**
    ```json
    {
        "no_hp": "08123456789",
        "message": "Halo Bapak John, kami ingin mengingatkan bahwa kendaraan B 1234 XYZ Anda perlu service rutin minggu depan."
    }
    ```
    
    **Response:**
    - status: Status pengiriman ("sent" atau "failed")
    - no_hp: Nomor HP yang dikirim (sudah dinormalisasi)
    - message: Isi pesan yang dikirim
    - api_response: Response dari WhatsApp API
    """
    try:
        result = send_custom_whatsapp_message(
            no_hp=request.no_hp,
            message=request.message
        )
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Gagal mengirim pesan: {str(e)}")


# ============= STATISTICS & REPORTING =============

@router.get("/stats/summary", status_code=200)
def get_statistics(
    db: Session = Depends(get_db),
    _=Depends(jwt_required)
):
    """
    Get statistik manual WhatsApp customers
    
    **Response:**
    - total_customers: Total records
    - active_customers: Customer aktif
    - inactive_customers: Customer tidak aktif
    - reminders_sent_total: Total reminder yang sudah dikirim
    - customers_with_upcoming_service: Customer dengan service dalam 7 hari ke depan
    """
    try:
        from datetime import date, timedelta
        from models.manual_whatsapp import ManualWhatsApp
        
        total = db.query(ManualWhatsApp).count()
        active = db.query(ManualWhatsApp).filter(ManualWhatsApp.is_active == 1).count()
        inactive = total - active
        
        reminders_sent_total = db.query(ManualWhatsApp).filter(
            ManualWhatsApp.reminder_sent_count > 0
        ).count()
        
        # Customer dengan service dalam 7 hari
        today = date.today()
        week_later = today + timedelta(days=7)
        upcoming = db.query(ManualWhatsApp).filter(
            ManualWhatsApp.next_service.isnot(None),
            ManualWhatsApp.next_service >= today,
            ManualWhatsApp.next_service <= week_later,
            ManualWhatsApp.is_active == 1
        ).count()
        
        return success_response(
            data={
                "total_customers": total,
                "active_customers": active,
                "inactive_customers": inactive,
                "reminders_sent_total": reminders_sent_total,
                "customers_with_upcoming_service": upcoming
            }
        )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
