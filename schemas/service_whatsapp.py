from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

class WhatsAppMessageCreate(BaseModel):
    """Schema untuk mengirim pesan WhatsApp melalui StarSender API"""
    message_type: str = Field(default="text", description="Tipe pesan: text")
    to: str = Field(..., description="Nomor WhatsApp tujuan (format: 62812345678 atau 08123456789)")
    body: str = Field(..., description="Isi pesan WhatsApp")
    file: Optional[str] = Field(None, description="URL file untuk dikirim (opsional)")
    delay: Optional[int] = Field(None, description="Delay pengiriman dalam detik (opsional)")
    schedule: Optional[int] = Field(None, description="Schedule pengiriman (timestamp dalam ms, opsional)")


class WhatsAppMessageResponse(BaseModel):
    """Response dari API StarSender"""
    success: bool
    data: dict
    message: str


class WhatsAppSendRequest(BaseModel):
    """Request body untuk endpoint mengirim WhatsApp"""
    to: str = Field(..., description="Nomor WhatsApp tujuan")
    body: str = Field(..., description="Isi pesan")
    file: Optional[str] = Field(None, description="URL file (opsional)")
    delay: Optional[int] = Field(None, description="Delay dalam detik (opsional)")
    schedule: Optional[int] = Field(None, description="Schedule timestamp (opsional)")
