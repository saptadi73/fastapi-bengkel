from pydantic import BaseModel
from uuid import UUID
from typing import Optional

class CreateServiceLinePacketOrder(BaseModel):
    service_id: UUID
    quantity: float
    price: float
    discount: Optional[float] = None
    subtotal: float

class CreateProductLinePacketOrder(BaseModel):
    product_id: UUID
    quantity: float
    price: float
    satuan_id: UUID
    discount: Optional[float] = None
    subtotal: float

class CreatePacketOrder(BaseModel):
    name: str
    product_line_packet_order: Optional[list[CreateProductLinePacketOrder]] = None
    service_line_packet_order: Optional[list[CreateServiceLinePacketOrder]] = None