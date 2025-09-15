from datetime import datetime
# ...existing code...

class CreateProductMove(BaseModel):
    product_id: UUID
    type: str  # 'incoming' atau 'outgoing'
    quantity: Decimal
    performed_by: str
    notes: Optional[str] = None
    timestamp: Optional[datetime] = None
from pydantic import BaseModel
from typing import List, Optional
from uuid import UUID
from decimal import Decimal
from datetime import date

class CreateProduct(BaseModel):
    name: str
    type: str
    description: Optional[str] = None
    price: Decimal
    min_stock: Decimal
    brand_id: UUID
    satuan_id: UUID
    category_id: UUID

class ProductResponse(BaseModel):
    id: UUID
    name: str
    type: str
    description: Optional[str] = None
    price: Decimal
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
    price: Decimal
    cost: Decimal

class ServiceResponse(BaseModel):
    id: UUID
    name: str
    description: Optional[str] = None
    price: Decimal
    cost: Decimal

    model_config = {
        "from_attributes": True
    }
