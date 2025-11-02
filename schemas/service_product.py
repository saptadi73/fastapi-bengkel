from pydantic import BaseModel
from typing import List, Optional
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

    model_config = {
        "from_attributes": True
    }

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
