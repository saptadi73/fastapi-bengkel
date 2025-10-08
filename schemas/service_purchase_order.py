from __future__ import annotations

from pydantic import BaseModel
from uuid import UUID
from typing import Optional, List
from datetime import date, datetime
from decimal import Decimal
from enum import Enum

class PurchaseOrderStatus(str, Enum):
    draft = "draft"
    dijalankan = "dijalankan"
    diterima = "diterima"
    dibayarkan = "dibayarkan"

class CreatePurchaseOrderLine(BaseModel):
    product_id: UUID
    quantity: Decimal
    price: Decimal
    discount: Optional[Decimal] = Decimal("0.00")
    subtotal: Decimal

class CreatePurchaseOrder(BaseModel):
    supplier_id: UUID
    date: date
    pajak: Optional[Decimal]=None
    total: Decimal
    pembayaran: Decimal
    status: Optional[PurchaseOrderStatus] = PurchaseOrderStatus.draft
    bukti_transfer: Optional[str] = None
    lines: List[CreatePurchaseOrderLine]

class UpdatePurchaseOrder(BaseModel):
    supplier_id: Optional[UUID] = None
    date: Optional[date] = None
    pajak: Optional[Decimal] = None
    pembayaran: Optional[Decimal] = None
    status: Optional[PurchaseOrderStatus] = None
    bukti_transfer: Optional[str] = None
    lines: Optional[List[CreatePurchaseOrderLine]] = None

class PurchaseOrderLineResponse(BaseModel):
    id: UUID
    product_id: UUID
    quantity: Decimal
    price: Decimal
    discount: Decimal
    subtotal: Decimal

class PurchaseOrderResponse(BaseModel):
    id: UUID
    po_no: str
    supplier_id: UUID
    date: date
    total: Decimal
    pajak: Decimal
    pembayaran: Optional[Decimal]
    status: PurchaseOrderStatus
    bukti_transfer: Optional[str]
    created_at: datetime
    updated_at: datetime
    lines: List[PurchaseOrderLineResponse]

    model_config = {
        "from_attributes": True
    }
