from pydantic import BaseModel
from typing import List, Optional
from uuid import UUID
from decimal import Decimal
from datetime import date,datetime

class CreateProduct(BaseModel):
    name: str
    type: str
    description: Optional[str] = None
    price: Decimal
    cost: Optional[Decimal] = None
    min_stock: Decimal
    brand_id: UUID
    satuan_id: UUID
    category_id: UUID

class UpdateProductCost(BaseModel):
    product_id: UUID
    cost: Decimal

class ProductResponse(BaseModel):
    id: UUID
    name: str
    type: str
    description: Optional[str] = None
    price: Decimal
    cost: Optional[Decimal]
    min_stock: Decimal
    brand_id: UUID
    satuan_id: UUID
    category_id: UUID

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
