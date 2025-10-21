from pydantic import BaseModel, field_validator
from typing import List, Optional
from uuid import UUID
from decimal import Decimal
from datetime import date

class CreateCustomerWithVehicles(BaseModel):
    nama: str
    hp: str
    alamat: Optional[str] = None
    email: Optional[str] = None
    tanggal_lahir: Optional[date] = None
    model: Optional[str] = None
    brand_id: UUID
    type: Optional[str] = None
    kapasitas: Optional[str] = None
    no_pol: str
    tahun: Optional[int] = None
    warna: Optional[str] = None
    no_mesin: Optional[str] = None
    no_rangka: Optional[str] = None

    @field_validator('tanggal_lahir', mode='before')
    @classmethod
    def validate_tanggal_lahir(cls, v):
        if v == "":
            return None
        return v

class CreateCustomer(BaseModel):
    nama: str
    hp: str
    alamat: Optional[str] = None
    email: Optional[str] = None
    tanggal_lahir: Optional[date] = None

    @field_validator('tanggal_lahir', mode='before')
    @classmethod
    def validate_tanggal_lahir(cls, v):
        if v == "":
            return None
        return v

class CreateVehicle(BaseModel):
    model: Optional[str] = None
    brand_id: UUID
    type: Optional[str]
    kapasitas: Optional[str]
    no_pol: str
    tahun: Optional[int] = None
    warna: Optional[str]
    no_mesin: Optional[str] = None
    no_rangka: Optional[str] = None
    customer_id: UUID

class VehicleResponse(BaseModel):
    id: UUID
    model: str
    brand_id: UUID
    type: str
    kapasitas: str
    no_pol: str
    tahun: int
    warna: str
    no_mesin: Optional[str] = None
    no_rangka: Optional[str] = None
    customer_id: UUID

    model_config = {
        "from_attributes": True
    }

class CustomerResponse(BaseModel):
    id: UUID
    nama: str
    hp: str
    alamat: Optional[str] = None
    email: Optional[str] = None
    tanggal_lahir: Optional[date] = None

    model_config = {
        "from_attributes": True
    }

class CustomerWithVehicleResponse(BaseModel):
    customer: CustomerResponse
    vehicle: VehicleResponse

    model_config = {
        "from_attributes": True
    }