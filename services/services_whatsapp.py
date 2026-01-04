"""
Service untuk mengirim pesan WhatsApp melalui StarSender API Gateway
Dokumentasi API: https://api.starsender.online/api/send
"""
import httpx
import json
import logging
import os
from logging.handlers import RotatingFileHandler
from typing import Optional, Dict, Any
from dotenv import load_dotenv

from schemas.service_whatsapp import WhatsAppMessageCreate, WhatsAppMessageResponse

# Load environment variables from .env file
load_dotenv()

# StarSender API Configuration
STARSENDER_API_URL = "https://api.starsender.online/api/send"
STARSENDER_API_KEY = os.getenv('STARSENDER_API_KEY', '')
REQUEST_TIMEOUT = 30

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

LOG_DIR = "logs"
LOG_FILE = os.path.join(LOG_DIR, "starsender.log")


def _ensure_file_logger() -> None:
    """Attach rotating file handler for StarSender logs if not already present."""
    # Logging disabled temporarily - already working fine
    pass
    # os.makedirs(LOG_DIR, exist_ok=True)
    # exists = any(isinstance(h, RotatingFileHandler) and getattr(h, "baseFilename", "") == os.path.abspath(LOG_FILE) for h in logger.handlers)
    # if exists:
    #     return
    # handler = RotatingFileHandler(LOG_FILE, maxBytes=1_000_000, backupCount=3, encoding="utf-8")
    # handler.setLevel(logging.DEBUG)
    # formatter = logging.Formatter("%(asctime)s | %(levelname)s | %(name)s | %(message)s")
    # handler.setFormatter(formatter)
    # logger.addHandler(handler)
    # logger.propagate = False


_ensure_file_logger()


def _mask_key(key: str) -> str:
    """Mask API key for safe logging."""
    if not key:
        return "<empty>"
    if len(key) <= 8:
        return "***"
    return key[:4] + "***" + key[-4:]


def _as_json(data: Any) -> str:
    """Safe JSON stringify for logging."""
    try:
        return json.dumps(data, ensure_ascii=False)
    except Exception:
        return str(data)


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

    logger.debug(
        "StarSender request (async) url=%s auth=%s payload=%s",
        STARSENDER_API_URL,
        _mask_key(STARSENDER_API_KEY),
        _as_json(payload)
    )
    
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
                logger.debug(
                    "StarSender response (async) status=%s body=%s",
                    response.status_code,
                    _as_json(result)
                )
                return result
            else:
                logger.error(
                    "StarSender HTTP error (async) status=%s url=%s payload=%s response=%s",
                    response.status_code,
                    STARSENDER_API_URL,
                    _as_json(payload),
                    response.text
                )
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

    logger.debug(
        "StarSender request (sync) url=%s auth=%s payload=%s",
        STARSENDER_API_URL,
        _mask_key(STARSENDER_API_KEY),
        _as_json(payload)
    )
    
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
                logger.debug(
                    "StarSender response (sync) status=%s body=%s",
                    response.status_code,
                    _as_json(result)
                )
                return result
            else:
                logger.error(
                    "StarSender HTTP error (sync) status=%s url=%s payload=%s response=%s",
                    response.status_code,
                    STARSENDER_API_URL,
                    _as_json(payload),
                    response.text
                )
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
        body=message,
        file=None,
        delay=None,
        schedule=None
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
        file=file_url,
        delay=None,
        schedule=None
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
        file=None,
        delay=None,
        schedule=schedule_timestamp_ms
    )
    return send_whatsapp_message_sync(msg_data)
