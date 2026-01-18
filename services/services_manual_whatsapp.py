"""
Service untuk Manual WhatsApp
Menangani CRUD operations dan pengiriman WhatsApp untuk manual customers
"""
from sqlalchemy.orm import Session
from models.manual_whatsapp import ManualWhatsApp
from schemas.manual_whatsapp import ManualWhatsAppCreate, ManualWhatsAppUpdate
from datetime import datetime, date, timedelta
from typing import List, Dict, Any, Optional
from sqlalchemy import update as sqlalchemy_update
from supports.utils_json_response import success_response, error_response
import logging

logger = logging.getLogger(__name__)


def normalize_phone_number(phone: str) -> str:
    """
    Normalize nomor HP ke format 62xxx
    
    Args:
        phone: Nomor HP (format: 08xxx atau 62xxx)
    
    Returns:
        Nomor HP yang sudah dibersihkan tanpa memaksa konversi 62xxx
    """
    phone = phone.strip()

    # Remove common separators but biarkan prefix apa adanya (08xx atau 62xx)
    phone = phone.replace(" ", "").replace("-", "")

    # Jika user menaruh "+62", hilangkan plus saja agar tetap 62xxx
    if phone.startswith("+62"):
        phone = phone[1:]

    # Kembalikan apa adanya (boleh 08xxx atau 62xxx sesuai permintaan user)
    return phone


def create_manual_whatsapp(db: Session, data: ManualWhatsAppCreate) -> Dict[str, Any]:
    """
    Create record manual WhatsApp baru
    
    Args:
        db: Database session
        data: ManualWhatsAppCreate schema
    
    Returns:
        Dict dari created record
    """
    try:
        # Normalize phone number
        normalized_phone = normalize_phone_number(data.no_hp)
        
        # Check jika nopol sudah exist
        existing = db.query(ManualWhatsApp).filter(
            ManualWhatsApp.nopol == data.nopol
        ).first()
        
        if existing:
            raise ValueError(f"Nopol {data.nopol} sudah terdaftar")
        
        # Create new record
        new_record = ManualWhatsApp(
            customer_name=data.customer_name,
            nopol=data.nopol,
            no_hp=normalized_phone,
            last_service=data.last_service,
            next_service=data.next_service,
            notes=data.notes,
            is_active=1
        )
        
        db.add(new_record)
        db.commit()
        db.refresh(new_record)
        
        logger.info(f"Created manual WhatsApp record for {data.customer_name} ({data.nopol})")
        
        return to_dict(new_record)
    
    except Exception as e:
        db.rollback()
        logger.error(f"Error creating manual WhatsApp: {str(e)}")
        raise


def get_manual_whatsapp_by_id(db: Session, record_id: str) -> Optional[Dict[str, Any]]:
    """
    Get record manual WhatsApp by ID
    
    Args:
        db: Database session
        record_id: Record ID
    
    Returns:
        Dict dari record atau None jika tidak ditemukan
    """
    record = db.query(ManualWhatsApp).filter(ManualWhatsApp.id == record_id).first()
    return to_dict(record) if record else None


def get_manual_whatsapp_by_nopol(db: Session, nopol: str) -> Optional[Dict[str, Any]]:
    """
    Get record manual WhatsApp by nopol
    
    Args:
        db: Database session
        nopol: Nomor polisi
    
    Returns:
        Dict dari record atau None
    """
    record = db.query(ManualWhatsApp).filter(ManualWhatsApp.nopol == nopol).first()
    return to_dict(record) if record else None


def get_all_manual_whatsapp(db: Session, active_only: bool = False) -> Dict[str, Any]:
    """
    Get semua record manual WhatsApp
    
    Args:
        db: Database session
        active_only: Hanya get record yang aktif
    
    Returns:
        Dict dengan summary dan list records
    """
    query = db.query(ManualWhatsApp)
    
    if active_only:
        query = query.filter(ManualWhatsApp.is_active == 1)
    
    records = query.order_by(ManualWhatsApp.created_at.desc()).all()
    
    total = db.query(ManualWhatsApp).count()
    active = db.query(ManualWhatsApp).filter(ManualWhatsApp.is_active == 1).count()
    inactive = total - active
    
    return {
        "total": total,
        "active": active,
        "inactive": inactive,
        "data": [to_dict(r) for r in records]
    }


def update_manual_whatsapp(db: Session, record_id: str, data: ManualWhatsAppUpdate) -> Dict[str, Any]:
    """
    Update record manual WhatsApp
    
    Args:
        db: Database session
        record_id: Record ID
        data: ManualWhatsAppUpdate schema
    
    Returns:
        Dict dari updated record
    """
    try:
        record: Optional[ManualWhatsApp] = db.query(ManualWhatsApp).filter(ManualWhatsApp.id == record_id).first()
        
        if not record:
            raise ValueError("Record tidak ditemukan")

        # Build update payload to avoid direct attribute assignment issues in type checker
        update_fields: Dict[str, Any] = {}
        if data.customer_name:
            update_fields["customer_name"] = data.customer_name
        if data.nopol:
            # Check jika nopol sudah exist
            existing = db.query(ManualWhatsApp).filter(
                ManualWhatsApp.nopol == data.nopol,
                ManualWhatsApp.id != record_id
            ).first()
            if existing:
                raise ValueError(f"Nopol {data.nopol} sudah terdaftar")
            update_fields["nopol"] = data.nopol
        if data.no_hp:
            update_fields["no_hp"] = normalize_phone_number(data.no_hp)
        if data.last_service is not None:
            update_fields["last_service"] = data.last_service
        if data.next_service is not None:
            update_fields["next_service"] = data.next_service
        if data.is_active is not None:
            update_fields["is_active"] = data.is_active
        if data.notes is not None:
            update_fields["notes"] = data.notes

        # Always touch updated_at when we actually update something
        if update_fields:
            update_fields["updated_at"] = datetime.utcnow()
            db.execute(
                sqlalchemy_update(ManualWhatsApp)
                .where(ManualWhatsApp.id == record_id)
                .values(**update_fields)
            )
            db.commit()
            db.refresh(record)
        
        logger.info(f"Updated manual WhatsApp record {record_id}")
        
        return to_dict(record)
    
    except Exception as e:
        db.rollback()
        logger.error(f"Error updating manual WhatsApp: {str(e)}")
        raise


def delete_manual_whatsapp(db: Session, record_id: str) -> bool:
    """
    Delete record manual WhatsApp
    
    Args:
        db: Database session
        record_id: Record ID
    
    Returns:
        True jika berhasil, False jika record tidak ditemukan
    """
    try:
        record = db.query(ManualWhatsApp).filter(ManualWhatsApp.id == record_id).first()
        
        if not record:
            return False
        
        db.delete(record)
        db.commit()
        
        logger.info(f"Deleted manual WhatsApp record {record_id}")
        
        return True
    
    except Exception as e:
        db.rollback()
        logger.error(f"Error deleting manual WhatsApp: {str(e)}")
        raise


def send_reminder_to_manual_customers(
    db: Session,
    days_threshold: int = 3,
    only_active: bool = True
) -> Dict[str, Any]:
    """
    Kirim reminder WhatsApp ke manual customers yang next_service dalam X hari
    
    Args:
        db: Database session
        days_threshold: Kirim reminder jika next_service dalam X hari (default: 3)
        only_active: Hanya kirim ke customer aktif (default: True)
    
    Returns:
        Dict dengan summary pengiriman
    """
    from services.services_whatsapp import send_whatsapp_message_sync
    from schemas.service_whatsapp import WhatsAppMessageCreate
    
    try:
        # Query records
        query = db.query(ManualWhatsApp)
        
        if only_active:
            query = query.filter(ManualWhatsApp.is_active == 1)
        
        records = query.all()
        
        if not records:
            return {
                "total_records": 0,
                "reminder_sent": 0,
                "reminder_failed": 0,
                "details": []
            }
        
        today = date.today()
        reminder_sent = 0
        reminder_failed = 0
        details = []
        
        for record in records:
            # Validate data
            if not all([record.customer_name, record.no_hp, record.nopol, record.next_service]):
                details.append({
                    "id": record.id,
                    "customer_name": record.customer_name,
                    "nopol": record.nopol,
                    "status": "skipped",
                    "reason": "Data tidak lengkap"
                })
                continue
            
            # Check jika next_service dalam threshold
            days_until_service = (record.next_service - today).days
            
            if not (0 <= days_until_service < days_threshold):
                details.append({
                    "id": record.id,
                    "customer_name": record.customer_name,
                    "nopol": record.nopol,
                    "status": "skipped",
                    "reason": f"Next service tidak dalam {days_threshold} hari (dalam {days_until_service} hari)"
                })
                continue
            
            # Prepare message
            try:
                message = f"""
Halo Bapak {record.customer_name},

Kami mengingatkan bahwa kendaraan dengan nomor polisi {record.nopol} Anda akan jatuh tempo untuk service maintenance pada:

📅 {record.next_service.strftime('%d %B %Y')}

Mohon segera menghubungi kami untuk melakukan penjadwalan service:
📞 087740659525

Terima kasih atas kepercayaan Anda.
                """.strip()
                
                # Send WhatsApp
                msg_data = WhatsAppMessageCreate(
                    message_type="text",
                    to=str(record.no_hp or ""),
                    body=message,
                    file=None,
                    delay=None,
                    schedule=None
                )
                result = send_whatsapp_message_sync(msg_data)
                
                # Update record safely via SQLAlchemy update to satisfy type checker
                db.execute(
                    sqlalchemy_update(ManualWhatsApp)
                    .where(ManualWhatsApp.id == record.id)
                    .values(
                        reminder_sent_count=ManualWhatsApp.reminder_sent_count + 1,
                        last_reminder_sent=datetime.utcnow()
                    )
                )
                db.commit()
                db.refresh(record)
                
                reminder_sent += 1
                details.append({
                    "id": record.id,
                    "customer_name": record.customer_name,
                    "nopol": record.nopol,
                    "status": "sent",
                    "message": message,
                    "api_response": result.get("message") if isinstance(result, dict) else str(result)
                })
                
                logger.info(f"Reminder sent to {record.customer_name} ({record.nopol})")
            
            except Exception as e:
                reminder_failed += 1
                details.append({
                    "id": record.id,
                    "customer_name": record.customer_name,
                    "nopol": record.nopol,
                    "status": "failed",
                    "reason": str(e)
                })
                logger.error(f"Failed to send reminder to {record.customer_name}: {str(e)}")
        
        return {
            "total_records": len(records),
            "reminder_sent": reminder_sent,
            "reminder_failed": reminder_failed,
            "details": details
        }
    
    except Exception as e:
        logger.error(f"Error in send_reminder_to_manual_customers: {str(e)}")
        raise


def bulk_import_manual_whatsapp(db: Session, records_data: List[ManualWhatsAppCreate]) -> Dict[str, Any]:
    """
    Bulk import manual WhatsApp records
    
    Args:
        db: Database session
        records_data: List of ManualWhatsAppCreate
    
    Returns:
        Dict dengan summary import
    """
    imported = 0
    failed = 0
    failures = []
    
    for data in records_data:
        try:
            create_manual_whatsapp(db, data)
            imported += 1
        except Exception as e:
            failed += 1
            failures.append({
                "customer_name": data.customer_name,
                "nopol": data.nopol,
                "error": str(e)
            })
    
    return {
        "total": len(records_data),
        "imported": imported,
        "failed": failed,
        "failures": failures
    }


def to_dict(record: Optional[ManualWhatsApp]) -> Dict[str, Any]:
    """Convert ManualWhatsApp model to dict"""
    if record is None:
        return {}
    
    return {
        "id": record.id,
        "customer_name": record.customer_name,
        "nopol": record.nopol,
        "no_hp": record.no_hp,
        "last_service": record.last_service.isoformat() if record.last_service is not None else None,
        "next_service": record.next_service.isoformat() if record.next_service is not None else None,
        "is_active": record.is_active,
        "reminder_sent_count": record.reminder_sent_count,
        "last_reminder_sent": record.last_reminder_sent.isoformat() if record.last_reminder_sent is not None else None,
        "notes": record.notes,
        "created_at": record.created_at.isoformat(),
        "updated_at": record.updated_at.isoformat()
    }


# ============= JSON RESPONSE WRAPPERS =============

def create_manual_whatsapp_json(db: Session, data: ManualWhatsAppCreate):
    try:
        record = create_manual_whatsapp(db, data)
        return success_response(
            data=record,
            message="Manual WhatsApp berhasil dibuat",
            status_code=201
        )
    except ValueError as e:
        return error_response(message=str(e), status_code=400)
    except Exception as e:
        logger.error(f"Error creating manual WhatsApp: {str(e)}")
        return error_response(message="Gagal membuat manual WhatsApp", status_code=500, data={"error": str(e)})


def get_manual_whatsapp_by_id_json(db: Session, record_id: str):
    try:
        record = get_manual_whatsapp_by_id(db, record_id)
        if not record:
            return error_response(message="Record tidak ditemukan", status_code=404)
        return success_response(data=record, message="Record ditemukan")
    except Exception as e:
        logger.error(f"Error fetching manual WhatsApp by id: {str(e)}")
        return error_response(message="Gagal mengambil record", status_code=500, data={"error": str(e)})


def get_manual_whatsapp_by_nopol_json(db: Session, nopol: str):
    try:
        record = get_manual_whatsapp_by_nopol(db, nopol)
        if not record:
            return error_response(message=f"Nopol {nopol} tidak ditemukan", status_code=404)
        return success_response(data=record, message="Record ditemukan")
    except Exception as e:
        logger.error(f"Error fetching manual WhatsApp by nopol: {str(e)}")
        return error_response(message="Gagal mengambil record", status_code=500, data={"error": str(e)})


def get_all_manual_whatsapp_json(db: Session, active_only: bool = False):
    try:
        result = get_all_manual_whatsapp(db, active_only)
        return success_response(data=result, message="Berhasil mengambil data manual WhatsApp")
    except Exception as e:
        logger.error(f"Error fetching all manual WhatsApp: {str(e)}")
        return error_response(message="Gagal mengambil data manual WhatsApp", status_code=500, data={"error": str(e)})


def update_manual_whatsapp_json(db: Session, record_id: str, data: ManualWhatsAppUpdate):
    try:
        record = update_manual_whatsapp(db, record_id, data)
        if not record:
            return error_response(message="Record tidak ditemukan", status_code=404)
        return success_response(data=record, message="Record berhasil diupdate")
    except ValueError as e:
        return error_response(message=str(e), status_code=400)
    except Exception as e:
        logger.error(f"Error updating manual WhatsApp: {str(e)}")
        return error_response(message="Gagal mengupdate record", status_code=500, data={"error": str(e)})


def delete_manual_whatsapp_json(db: Session, record_id: str):
    try:
        success = delete_manual_whatsapp(db, record_id)
        if not success:
            return error_response(message="Record tidak ditemukan", status_code=404)
        return success_response(data=None, message="Record berhasil dihapus", status_code=204)
    except Exception as e:
        logger.error(f"Error deleting manual WhatsApp: {str(e)}")
        return error_response(message="Gagal menghapus record", status_code=500, data={"error": str(e)})


def bulk_import_manual_whatsapp_json(db: Session, records_data: List[ManualWhatsAppCreate]):
    try:
        if not records_data:
            return error_response(message="Records tidak boleh kosong", status_code=400)
        result = bulk_import_manual_whatsapp(db, records_data)
        return success_response(
            data=result,
            message=f"Import selesai. {result['imported']} berhasil, {result['failed']} gagal",
            status_code=201
        )
    except Exception as e:
        logger.error(f"Error bulk import manual WhatsApp: {str(e)}")
        return error_response(message="Gagal import data", status_code=500, data={"error": str(e)})


def send_reminder_to_manual_customers_json(
    db: Session,
    days_threshold: int = 3,
    only_active: bool = True
):
    try:
        result = send_reminder_to_manual_customers(db, days_threshold=days_threshold, only_active=only_active)
        return success_response(data=result, message="Pengiriman reminder selesai")
    except Exception as e:
        logger.error(f"Error sending reminders: {str(e)}")
        return error_response(message="Gagal mengirim reminder", status_code=500, data={"error": str(e)})


def send_custom_whatsapp_message(no_hp: str, message: str) -> Dict[str, Any]:
    """
    Kirim custom WhatsApp message ke nomor yang ditentukan
    
    Args:
        no_hp: Nomor HP tujuan (format: 62xxx atau 08xxx)
        message: Isi pesan WhatsApp custom dari front-end
    
    Returns:
        Dict dengan status pengiriman dan response dari API
    """
    from services.services_whatsapp import send_whatsapp_message_sync
    from schemas.service_whatsapp import WhatsAppMessageCreate
    
    try:
        # Normalize phone number
        normalized_phone = normalize_phone_number(no_hp)
        
        # Convert 08xxx to 62xxx for WhatsApp API
        if normalized_phone.startswith("08"):
            normalized_phone = "62" + normalized_phone[1:]
        
        # Validate
        if not normalized_phone or len(normalized_phone) < 10:
            raise ValueError("Nomor HP tidak valid")
        
        if not message or len(message.strip()) == 0:
            raise ValueError("Message tidak boleh kosong")
        
        # Send WhatsApp
        msg_data = WhatsAppMessageCreate(
            message_type="text",
            to=normalized_phone,
            body=message.strip(),
            file=None,
            delay=None,
            schedule=None
        )
        
        result = send_whatsapp_message_sync(msg_data)
        
        logger.info(f"Custom message sent to {normalized_phone}")
        
        return {
            "status": "sent",
            "no_hp": normalized_phone,
            "message": message.strip(),
            "api_response": result
        }
    
    except Exception as e:
        logger.error(f"Failed to send custom message to {no_hp}: {str(e)}")
        raise
