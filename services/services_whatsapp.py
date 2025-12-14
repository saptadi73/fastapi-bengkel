"""
Service untuk mengirim pesan WhatsApp melalui StarSender API Gateway
Dokumentasi API: https://api.starsender.online/api/send
"""
import httpx
import json
from typing import Optional, Dict, Any
from schemas.service_whatsapp import WhatsAppMessageCreate, WhatsAppMessageResponse

# StarSender API Configuration
STARSENDER_API_URL = "https://api.starsender.online/api/send"
STARSENDER_API_KEY = "a234d49a-a181-4a83-964d-0d118b3a6e45"
REQUEST_TIMEOUT = 30


async def send_whatsapp_message(message_data: WhatsAppMessageCreate) -> Dict[str, Any]:
    """
    Mengirim pesan WhatsApp melalui StarSender API.
    
    Args:
        message_data: Data pesan WhatsApp (WhatsAppMessageCreate schema)
    
    Returns:
        Dict berisi response dari API dengan struktur:
        {
            "success": bool,
            "data": dict,
            "message": str
        }
    
    Raises:
        Exception: Jika request gagal atau API mengembalikan error
    """
    # Siapkan payload untuk API
    payload: Dict[str, Any] = {
        "messageType": message_data.message_type,
        "to": message_data.to,
        "body": message_data.body,
    }
    
    # Tambahkan field opsional jika ada
    if message_data.file:
        payload["file"] = message_data.file
    if message_data.delay:
        payload["delay"] = message_data.delay
    if message_data.schedule:
        payload["schedule"] = message_data.schedule
    
    # Siapkan headers
    headers = {
        "Content-Type": "application/json",
        "Authorization": STARSENDER_API_KEY
    }
    
    try:
        # Gunakan httpx untuk mengirim request
        async with httpx.AsyncClient(timeout=REQUEST_TIMEOUT) as client:
            response = await client.post(
                STARSENDER_API_URL,
                json=payload,
                headers=headers
            )
            
            # Check status code
            if response.status_code == 200:
                result = response.json()
                return result
            else:
                raise Exception(
                    f"API StarSender error: HTTP {response.status_code} - {response.text}"
                )
    
    except httpx.RequestError as e:
        raise Exception(f"Gagal menghubungi API StarSender: {str(e)}")
    except json.JSONDecodeError as e:
        raise Exception(f"Response API tidak valid JSON: {str(e)}")
    except Exception as e:
        raise Exception(f"Error mengirim pesan WhatsApp: {str(e)}")


def send_whatsapp_message_sync(message_data: WhatsAppMessageCreate) -> Dict[str, Any]:
    """
    Versi synchronous untuk mengirim pesan WhatsApp.
    Gunakan jika endpoint tidak async.
    
    Args:
        message_data: Data pesan WhatsApp
    
    Returns:
        Response dari API
    """
    # Siapkan payload untuk API
    payload: Dict[str, Any] = {
        "messageType": message_data.message_type,
        "to": message_data.to,
        "body": message_data.body,
    }
    
    # Tambahkan field opsional jika ada
    if message_data.file:
        payload["file"] = message_data.file
    if message_data.delay:
        payload["delay"] = message_data.delay
    if message_data.schedule:
        payload["schedule"] = message_data.schedule
    
    # Siapkan headers
    headers: Dict[str, str] = {
        "Content-Type": "application/json",
        "Authorization": STARSENDER_API_KEY
    }
    
    try:
        # Gunakan httpx untuk mengirim request (sync)
        with httpx.Client(timeout=REQUEST_TIMEOUT) as client:
            response = client.post(
                STARSENDER_API_URL,
                json=payload,
                headers=headers
            )
            
            # Check status code
            if response.status_code == 200:
                result = response.json()
                return result
            else:
                raise Exception(
                    f"API StarSender error: HTTP {response.status_code} - {response.text}"
                )
    
    except httpx.RequestError as e:
        raise Exception(f"Gagal menghubungi API StarSender: {str(e)}")
    except json.JSONDecodeError as e:
        raise Exception(f"Response API tidak valid JSON: {str(e)}")
    except Exception as e:
        raise Exception(f"Error mengirim pesan WhatsApp: {str(e)}")


def send_simple_message(phone: str, message: str) -> Dict[str, Any]:
    """
    Helper function untuk mengirim pesan text sederhana.
    
    Args:
        phone: Nomor WhatsApp tujuan
        message: Isi pesan
    
    Returns:
        Response dari API
    """
    msg_data = WhatsAppMessageCreate(
        message_type="text",
        to=phone,
        body=message
    )
    return send_whatsapp_message_sync(msg_data)


def send_message_with_file(phone: str, message: str, file_url: str) -> Dict[str, Any]:
    """
    Helper function untuk mengirim pesan dengan file.
    
    Args:
        phone: Nomor WhatsApp tujuan
        message: Isi pesan
        file_url: URL file yang akan dikirim
    
    Returns:
        Response dari API
    """
    msg_data = WhatsAppMessageCreate(
        message_type="text",
        to=phone,
        body=message,
        file=file_url
    )
    return send_whatsapp_message_sync(msg_data)


def send_scheduled_message(phone: str, message: str, schedule_timestamp_ms: int) -> Dict[str, Any]:
    """
    Helper function untuk mengirim pesan terjadwal.
    
    Args:
        phone: Nomor WhatsApp tujuan
        message: Isi pesan
        schedule_timestamp_ms: Timestamp schedule dalam milliseconds
    
    Returns:
        Response dari API
    """
    msg_data = WhatsAppMessageCreate(
        message_type="text",
        to=phone,
        body=message,
        schedule=schedule_timestamp_ms
    )
    return send_whatsapp_message_sync(msg_data)
