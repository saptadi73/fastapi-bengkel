from pydantic import BaseModel, ConfigDict, field_serializer
from decimal import Decimal


class DecimalModel(BaseModel):
    model_config = ConfigDict()

    @field_serializer("*")
    def _serialize_decimal(self, v, info):
        if isinstance(v, Decimal):
            return float(v)
        return v
from uuid import UUID
from decimal import Decimal
from typing import Optional, List
from datetime import datetime, date

class CreateProductMovedHistory(BaseModel):
    product_id: UUID
    type: str  # e.g., 'added', 'removed', 'updated'
    quantity: Decimal
    timestamp: Optional[datetime] = None
    performed_by: str
    notes: Optional[str] = None


class ProductMoveHistoryReportRequest(BaseModel):
    start_date: date
    end_date: date

class ProductMoveHistoryReportItem(BaseModel):
    product_id: str
    product_name: str
    type: str
    quantity: Decimal
    timestamp: datetime
    performed_by: str
    notes: Optional[str] = None
    customer_name: Optional[str] = None
    supplier_name: Optional[str] = None

class ProductMoveHistoryReport(DecimalModel):
    total_entries: int
    items: List[ProductMoveHistoryReportItem]

    model_config = ConfigDict()

class ManualAdjustment(BaseModel):
    product_id: UUID
    quantity: Decimal
    performed_by: str
    notes: Optional[str] = None
    timestamp: Optional[datetime] = None

class PurchaseOrderUpdateCost(BaseModel):
    product_id: UUID
    quantity: Decimal
    price: Decimal


