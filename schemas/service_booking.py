from pydantic import BaseModel
from typing import List, Optional
from uuid import UUID
from decimal import Decimal
from datetime import date
from datetime import datetime
from datetime import time

class CreateBooking(BaseModel):
    nama: str
    hp: str
    model: Optional[str] = None
    type: Optional[str] = None
    no_pol: str
    warna: Optional[str] = None
    tanggal_booking: Optional[date] = None
    jam_booking: Optional[time] = None
    vehicle_id: Optional[UUID] = None
    customer_id: Optional[UUID] = None

class BookingResponse(BaseModel):
    id: UUID
    nama: str
    hp: str
    model: Optional[str] = None
    type: Optional[str] = None
    no_pol: str
    warna: Optional[str] = None
    tanggal_booking: Optional[date] = None
    jam_booking: Optional[time] = None
    vehicle_id: Optional[UUID] = None
    customer_id: Optional[UUID] = None
    created_at: datetime
    updated_at: datetime

    model_config = {
        "from_attributes": True
    }