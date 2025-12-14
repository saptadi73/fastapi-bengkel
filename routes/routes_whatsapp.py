from fastapi import APIRouter, Depends
from schemas.service_whatsapp import WhatsAppSendRequest, WhatsAppMessageCreate, WhatsAppMessageResponse
from services.services_whatsapp import send_whatsapp_message_sync
from supports.utils_json_response import success_response, error_response
from middleware.jwt_required import jwt_required

router = APIRouter(prefix="/whatsapp", tags=["WhatsApp"])


@router.post("/send", response_model=WhatsAppMessageResponse, dependencies=[Depends(jwt_required)])
def send_whatsapp(data: WhatsAppSendRequest):
    """
    Endpoint untuk mengirim pesan WhatsApp melalui StarSender API.
    
    Body parameters:
    - to: Nomor WhatsApp tujuan (format: 62812345678 atau 08123456789)
    - body: Isi pesan
    - file: URL file (opsional)
    - delay: Delay pengiriman dalam detik (opsional)
    - schedule: Schedule timestamp dalam ms (opsional)
    
    Response:
    {
        "success": true/false,
        "data": {},
        "message": "Success sent message" atau pesan error
    }
    """
    try:
        # Konversi request ke WhatsAppMessageCreate
        message_data = WhatsAppMessageCreate(
            message_type="text",
            to=data.to,
            body=data.body,
            file=data.file,
            delay=data.delay,
            schedule=data.schedule
        )
        
        # Kirim pesan melalui service
        result = send_whatsapp_message_sync(message_data)
        
        # Return response dengan format yang sesuai
        return success_response(
            data=result.get("data", {}),
            message=result.get("message", "Pesan berhasil dikirim")
        )
    
    except Exception as e:
        return error_response(
            message=f"Gagal mengirim pesan WhatsApp: {str(e)}",
            status_code=400
        )


@router.post("/send-simple")
def send_simple_whatsapp(phone: str, message: str):
    """
    Endpoint sederhana untuk mengirim pesan text WhatsApp.
    
    Query parameters:
    - phone: Nomor WhatsApp tujuan
    - message: Isi pesan
    """
    try:
        from services.services_whatsapp import send_simple_message
        result = send_simple_message(phone, message)
        return success_response(
            data=result.get("data", {}),
            message=result.get("message", "Pesan berhasil dikirim")
        )
    except Exception as e:
        return error_response(
            message=f"Gagal mengirim pesan: {str(e)}",
            status_code=400
        )


@router.post("/send-with-file")
def send_whatsapp_file(phone: str, message: str, file_url: str):
    """
    Endpoint untuk mengirim pesan WhatsApp dengan file.
    
    Query parameters:
    - phone: Nomor WhatsApp tujuan
    - message: Isi pesan
    - file_url: URL file yang akan dikirim
    """
    try:
        from services.services_whatsapp import send_message_with_file
        result = send_message_with_file(phone, message, file_url)
        return success_response(
            data=result.get("data", {}),
            message=result.get("message", "Pesan dengan file berhasil dikirim")
        )
    except Exception as e:
        return error_response(
            message=f"Gagal mengirim pesan: {str(e)}",
            status_code=400
        )


@router.post("/send-scheduled")
def send_scheduled_whatsapp(phone: str, message: str, schedule_timestamp_ms: int):
    """
    Endpoint untuk mengirim pesan WhatsApp terjadwal.
    
    Query parameters:
    - phone: Nomor WhatsApp tujuan
    - message: Isi pesan
    - schedule_timestamp_ms: Timestamp schedule dalam milliseconds
    """
    try:
        from services.services_whatsapp import send_scheduled_message
        result = send_scheduled_message(phone, message, schedule_timestamp_ms)
        return success_response(
            data=result.get("data", {}),
            message=result.get("message", "Pesan terjadwal berhasil dikirim")
        )
    except Exception as e:
        return error_response(
            message=f"Gagal mengirim pesan: {str(e)}",
            status_code=400
        )
