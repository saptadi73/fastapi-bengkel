from pydantic import BaseModel, Field, model_validator
from typing import Any, List, Literal, Optional
from uuid import UUID
from decimal import Decimal
from datetime import date,datetime

class CreateProduct(BaseModel):
    name: str
    type: Optional[str] = None
    description: Optional[str] = None
    price: Decimal
    cost: Optional[Decimal] = None
    min_stock: Decimal
    brand_id: UUID
    satuan_id: UUID
    category_id: UUID
    supplier_id: Optional[UUID] = None
    is_consignment: bool = False
    consignment_commission: Optional[Decimal] = None
    is_internal_consumption: Optional[bool] = False


class UpdateProduct(BaseModel):
    name: Optional[str] = Field(default=None, min_length=1, max_length=255)
    type: Optional[str] = None
    description: Optional[str] = None
    price: Optional[Decimal] = Field(default=None, ge=0)
    cost: Optional[Decimal] = Field(default=None, ge=0)
    min_stock: Optional[Decimal] = Field(default=None, ge=0)
    brand_id: Optional[UUID] = None
    satuan_id: Optional[UUID] = None
    category_id: Optional[UUID] = None
    supplier_id: Optional[UUID] = None
    is_consignment: Optional[bool] = None
    consignment_commission: Optional[Decimal] = Field(default=None, ge=0)
    is_internal_consumption: Optional[bool] = None

    @model_validator(mode="after")
    def require_at_least_one_field(self):
        if not self.model_fields_set:
            raise ValueError("At least one product field must be provided")
        return self
class UpdateProductCost(BaseModel):
    product_id: UUID
    cost: Decimal

class ProductResponse(BaseModel):
    id: UUID
    name: str
    type: Optional[str] = None
    description: Optional[str] = None
    price: Decimal
    cost: Optional[Decimal]
    min_stock: Decimal
    brand_id: UUID
    satuan_id: UUID
    category_id: UUID
    supplier_id: Optional[UUID] = None
    is_consignment: bool = False
    consignment_commission: Optional[Decimal] = None
    is_internal_consumption: Optional[bool] = False

    model_config = {
        "from_attributes": True
    }


class InventoryProductResponse(BaseModel):
    id: UUID
    name: str
    type: Optional[str] = None
    description: Optional[str] = None
    brand_id: Optional[UUID] = None
    brand_name: Optional[str] = None
    category_id: Optional[UUID] = None
    category_name: Optional[str] = None
    satuan_id: Optional[UUID] = None
    satuan_name: Optional[str] = None
    supplier_id: Optional[UUID] = None
    vendor_code: Optional[str] = None
    supplier_name: Optional[str] = None
    price: Optional[Decimal] = None
    purchase_price: Optional[Decimal] = None
    hpp: Optional[Decimal] = None
    cost: Optional[Decimal] = Field(default=None, deprecated=True)
    margin: Optional[Decimal] = None
    margin_percentage: Optional[Decimal] = None
    total_stock: Decimal
    min_stock: Decimal
    stock_status: Literal["safe", "reorder"]
    is_consignment: bool = False


class InventoryPaginationResponse(BaseModel):
    page: int
    limit: int
    total: int
    total_pages: int
    has_previous: bool
    has_next: bool


class InventoryListResponse(BaseModel):
    status: Literal["success"] = "success"
    message: str = "Inventory retrieved successfully"
    data: List[InventoryProductResponse]
    pagination: InventoryPaginationResponse


class ProductMutationResponse(BaseModel):
    status: Literal["success"] = "success"
    message: str
    data: Optional[ProductResponse] = None


class ProductDeleteResponse(BaseModel):
    status: Literal["success"] = "success"
    message: str
    data: None = None


class ApiErrorResponse(BaseModel):
    status: Literal["error"] = "error"
    message: str
    data: Optional[Any] = None

class BrandResponse(BaseModel):
    id: UUID
    name: str

    model_config = {
        "from_attributes": True
    }

class SatuanResponse(BaseModel):
    id: UUID
    name: str

    model_config = {
        "from_attributes": True
    }

class CategoryResponse(BaseModel):
    id: UUID
    name: str

    model_config = {
        "from_attributes": True
    }

class CreateService(BaseModel):
    name: str
    description: Optional[str] = None
    price: Optional[Decimal]
    cost: Optional[Decimal]

class ServiceResponse(BaseModel):
    id: UUID
    name: str
    description: Optional[str] = None
    price: Decimal
    cost: Decimal

    model_config = {
        "from_attributes": True
    }

class CreateCategory(BaseModel):
    name: str

class CreateSatuan(BaseModel):
    name: str

class CreateBrand(BaseModel):
    name: str

class ProductCostHistoryResponse(BaseModel):
    id: UUID
    product_id: UUID
    product_name: Optional[str] = None
    old_cost: Optional[Decimal] = None
    new_cost: Decimal
    old_quantity: Optional[Decimal] = None
    new_quantity: Decimal
    purchase_quantity: Optional[Decimal] = None
    purchase_price: Optional[Decimal] = None
    calculation_method: str
    notes: Optional[str] = None
    created_at: datetime
    created_by: str

    model_config = {
        "from_attributes": True
    }

class ProductCostHistoryRequest(BaseModel):
    product_id: Optional[UUID] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    calculation_method: Optional[str] = None
