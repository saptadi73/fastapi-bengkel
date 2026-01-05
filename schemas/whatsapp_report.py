from pydantic import BaseModel
from datetime import datetime
from typing import Optional
from uuid import UUID


class WhatsappReportBase(BaseModel):
    id_customer: UUID
    id_vehicle: UUID
    last_message_date: Optional[datetime] = None
    frequency: int = 0


class WhatsappReportCreate(WhatsappReportBase):
    pass


class WhatsappReportUpdate(BaseModel):
    last_message_date: Optional[datetime] = None
    frequency: Optional[int] = None


class WhatsappReportResponse(WhatsappReportBase):
    id: UUID
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class WhatsappReportStatistics(BaseModel):
    total_customers_with_vehicles: int
    total_messages_sent: int
    average_messages_per_customer: float
    customers_by_frequency: dict  # {frequency: count}


class WhatsappReportDetail(BaseModel):
    id: UUID
    customer_name: str
    customer_phone: str
    vehicle_model: str
    vehicle_nopol: str
    last_message_date: Optional[datetime]
    frequency: int
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True
