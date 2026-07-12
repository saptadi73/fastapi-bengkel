from pydantic import BaseModel, ConfigDict, Field, field_serializer, model_validator
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
from typing import Any, Literal, Optional, List
from datetime import datetime, date

class CreateProductMovedHistory(BaseModel):
    product_id: UUID
    type: str  # e.g., 'added', 'removed', 'updated'
    quantity: Decimal
    timestamp: Optional[datetime] = None
    performed_by: str
    notes: Optional[str] = None
    reference_type: Optional[str] = None
    reference_id: Optional[UUID] = None
    purchase_order_id: Optional[UUID] = None
    workorder_id: Optional[UUID] = None
    supplier_id: Optional[UUID] = None
    customer_id: Optional[UUID] = None
    vehicle_id: Optional[UUID] = None
    purchase_price: Optional[Decimal] = None
    selling_price: Optional[Decimal] = None
    hpp_snapshot: Optional[Decimal] = None


class ProductMoveHistoryReportRequest(BaseModel):
    start_date: date
    end_date: date
    product_id: Optional[UUID] = None
    movement_type: Optional[Literal['income', 'outcome', 'adjustment', 'loss', 'internal_consumption']] = None
    reference_type: Optional[Literal['purchase_order', 'workorder', 'consignment_receipt', 'adjustment', 'loss', 'internal_consumption']] = None
    supplier_id: Optional[UUID] = None
    customer_id: Optional[UUID] = None
    search: Optional[str] = Field(default=None, min_length=1, max_length=100)
    page: int = Field(default=1, ge=1)
    limit: int = Field(default=25, ge=1, le=100)
    sort_order: Literal['asc', 'desc'] = 'asc'

    @model_validator(mode='after')
    def validate_date_range(self):
        if self.end_date < self.start_date:
            raise ValueError('end_date must be greater than or equal to start_date')
        return self


class ProductMoveHistorySummary(DecimalModel):
    opening_balance: Decimal = Decimal('0.00')
    total_in: Decimal = Decimal('0.00')
    total_out: Decimal = Decimal('0.00')
    total_adjustment: Decimal = Decimal('0.00')
    closing_balance: Decimal = Decimal('0.00')


class ProductMoveHistoryPagination(BaseModel):
    page: int
    limit: int
    total: int
    total_pages: int
    has_previous: bool
    has_next: bool

class ProductMoveHistoryReportItem(DecimalModel):
    movement_id: str
    product_id: str
    product_name: str
    type: str
    quantity: Decimal
    timestamp: datetime
    performed_by: str
    notes: Optional[str] = None
    price: Optional[Decimal] = None
    hpp: Optional[Decimal] = None
    customer_name: Optional[str] = None
    vendor_name: Optional[str] = None
    nopol: Optional[str] = None
    quantity_in: Decimal = Decimal('0.00')
    quantity_out: Decimal = Decimal('0.00')
    balance_before: Decimal = Decimal('0.00')
    balance_after: Decimal = Decimal('0.00')
    purchase_price: Optional[Decimal] = None
    selling_price: Optional[Decimal] = None
    reference_type: Optional[str] = None
    reference_id: Optional[str] = None
    reference_no: Optional[str] = None
    purchase_order_id: Optional[str] = None
    purchase_order_no: Optional[str] = None
    workorder_id: Optional[str] = None
    workorder_no: Optional[str] = None
    supplier_id: Optional[str] = None
    vendor_code: Optional[str] = None
    customer_id: Optional[str] = None
    vehicle_id: Optional[str] = None

class ProductMoveHistoryReport(DecimalModel):
    summary: ProductMoveHistorySummary = Field(default_factory=ProductMoveHistorySummary)
    total_entries: int
    items: List[ProductMoveHistoryReportItem]
    pagination: ProductMoveHistoryPagination

    model_config = ConfigDict()


class ProductMoveHistoryReportResponse(BaseModel):
    status: Literal['success'] = 'success'
    message: str
    data: ProductMoveHistoryReport


class InventoryReportErrorResponse(BaseModel):
    status: Literal['error'] = 'error'
    message: str
    data: Optional[Any] = None

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

class CreateProductMovedHistories(BaseModel):
    items: List[CreateProductMovedHistory]


