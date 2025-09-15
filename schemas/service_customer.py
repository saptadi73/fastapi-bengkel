from pydantic import BaseModel
from typing import List, Optional
from uuid import UUID
from decimal import Decimal
from datetime import date

class CreateCustomerWithVehicles(BaseModel):
    nama: str
    hp: str
    alamat: str
    email: str
    merk: str
    model: str
    brand_id: UUID
    type: str
    kapasitas: str
    no_pol: str
    tahun: int
    warna: str

class VehicleResponse(BaseModel):
    id: UUID
    merk: str
    model: str
    brand_id: UUID
    type: str
    kapasitas: str
    no_pol: str
    tahun: int
    warna: str
    customer_id: UUID

    model_config = {
        "from_attributes": True
    }

class CustomerResponse(BaseModel):
    id: UUID
    nama: str
    hp: str
    alamat: str
    email: str

    model_config = {
        "from_attributes": True
    }

class CustomerWithVehicleResponse(BaseModel):
    customer: CustomerResponse
    vehicle: VehicleResponse

    model_config = {
        "from_attributes": True
    }