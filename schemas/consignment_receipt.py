"""
Schemas untuk Consignment Receipt
"""

from pydantic import BaseModel
from typing import Optional, List
from datetime import date, datetime
from decimal import Decimal
from uuid import UUID

class ConsignmentReceiptBase(BaseModel):
    product_id: UUID
    supplier_id: UUID
    receipt_number: str
    receipt_date: date
    quantity_received: Decimal
    unit_price: Optional[Decimal] = None
    total_value: Optional[Decimal] = None
    notes: Optional[str] = None
    received_by: str

class ConsignmentReceiptCreate(ConsignmentReceiptBase):
    pass

class ConsignmentReceiptUpdate(BaseModel):
    receipt_date: Optional[date] = None
    quantity_received: Optional[Decimal] = None
    unit_price: Optional[Decimal] = None
    total_value: Optional[Decimal] = None
    notes: Optional[str] = None

class ConsignmentReceiptResponse(ConsignmentReceiptBase):
    id: UUID
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    # Related data
    product_name: Optional[str] = None
    supplier_name: Optional[str] = None
    
    class Config:
        from_attributes = True

class ConsignmentReceiptListResponse(BaseModel):
    id: UUID
    receipt_number: str
    receipt_date: date
    product_name: Optional[str] = None
    supplier_name: Optional[str] = None
    quantity_received: Decimal
    unit_price: Optional[Decimal] = None
    total_value: Optional[Decimal] = None
    received_by: str
    created_at: datetime
    
    class Config:
        from_attributes = True
