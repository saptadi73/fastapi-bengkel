from pydantic import BaseModel
from uuid import UUID
from decimal import Decimal
from typing import Optional
from datetime import datetime

class CreateProductMovedHistory(BaseModel):
    product_id: UUID
    type: str  # e.g., 'added', 'removed', 'updated'
    quantity: Decimal
    timestamp: Optional[datetime] = None
    performed_by: str
    notes: Optional[str] = None


