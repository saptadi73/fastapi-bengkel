from pydantic import BaseModel
from uuid import UUID
from decimal import Decimal
from typing import List, Optional

class UpdateProductOrder(BaseModel):
    product_id: UUID
    quantity: Decimal

class UpdateServiceOrder(BaseModel):
    service_id: UUID
    notes: Optional[str] = None

class UpdateWorkorderOrders(BaseModel):
    workorder_id: UUID
    products: Optional[List[UpdateProductOrder]] = None
    services: Optional[List[UpdateServiceOrder]] = None
    performed_by: Optional[str] = 'system'
