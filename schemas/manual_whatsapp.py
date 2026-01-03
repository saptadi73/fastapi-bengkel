"""
Schemas untuk Manual WhatsApp API
"""
from pydantic import BaseModel, Field
from typing import Optional
from datetime import date, datetime


class ManualWhatsAppCreate(BaseModel):
    """Schema untuk create manual WhatsApp record"""
    customer_name: str = Field(..., description="Nama customer", min_length=1, max_length=255)
    nopol: str = Field(..., description="Nomor polisi kendaraan", min_length=1, max_length=20)
    no_hp: str = Field(..., description="Nomor HP customer (format: 62xxx atau 08xxx)", min_length=10, max_length=20)
    last_service: Optional[date] = Field(None, description="Tanggal service terakhir (format: YYYY-MM-DD)")
    next_service: Optional[date] = Field(None, description="Tanggal service berikutnya (format: YYYY-MM-DD)")
    notes: Optional[str] = Field(None, description="Catatan tambahan", max_length=500)
    
    class Config:
        json_schema_extra = {
            "example": {
                "customer_name": "Bapak Joko",
                "nopol": "B 1234 XYZ",
                "no_hp": "08123456789",
                "last_service": "2025-10-15",
                "next_service": "2026-01-15",
                "notes": "Customer VIP"
            }
        }


class ManualWhatsAppUpdate(BaseModel):
    """Schema untuk update manual WhatsApp record"""
    customer_name: Optional[str] = Field(default=None, description="Nama customer", max_length=255)
    nopol: Optional[str] = Field(default=None, description="Nomor polisi kendaraan", max_length=20)
    no_hp: Optional[str] = Field(default=None, description="Nomor HP customer", max_length=20)
    last_service: Optional[date] = Field(default=None, description="Tanggal service terakhir")
    next_service: Optional[date] = Field(default=None, description="Tanggal service berikutnya")
    is_active: Optional[int] = Field(default=None, description="Status aktif (1=active, 0=inactive)")
    notes: Optional[str] = Field(default=None, description="Catatan tambahan", max_length=500)
    
    class Config:
        json_schema_extra = {
            "example": {
                "next_service": "2026-02-01"
            }
        }


class ManualWhatsAppResponse(BaseModel):
    """Schema untuk response manual WhatsApp record"""
    id: str
    customer_name: str
    nopol: str
    no_hp: str
    last_service: Optional[str]
    next_service: Optional[str]
    is_active: int
    reminder_sent_count: int
    last_reminder_sent: Optional[str]
    notes: Optional[str]
    created_at: str
    updated_at: str
    
    class Config:
        from_attributes = True


class ManualWhatsAppListResponse(BaseModel):
    """Schema untuk list response"""
    total: int
    active: int
    inactive: int
    data: list[ManualWhatsAppResponse]


class SendReminderRequest(BaseModel):
    """Schema untuk request send reminder"""
    days_threshold: int = Field(default=3, description="Kirim reminder jika next_service dalam X hari", ge=1, le=30)
    only_active: bool = Field(default=True, description="Hanya kirim ke customer aktif")
    
    class Config:
        json_schema_extra = {
            "example": {
                "days_threshold": 3,
                "only_active": True
            }
        }


class SendReminderResponse(BaseModel):
    """Schema untuk response send reminder"""
    total_records: int
    reminder_sent: int
    reminder_failed: int
    details: list[dict]
    
    class Config:
        json_schema_extra = {
            "example": {
                "total_records": 10,
                "reminder_sent": 8,
                "reminder_failed": 2,
                "details": [
                    {
                        "id": "uuid",
                        "customer_name": "Bapak Joko",
                        "nopol": "B 1234 XYZ",
                        "status": "sent",
                        "message": "Bapak Joko..."
                    }
                ]
            }
        }
