from pydantic import BaseModel, Field, field_validator
from typing import List, Optional
from uuid import UUID
from decimal import Decimal
from datetime import date

class CreateCustomerWithVehicles(BaseModel):
    nama: str = Field(min_length=1)
    hp: str = Field(min_length=1)
    alamat: str = Field(min_length=1)
    email: Optional[str] = None
    tanggal_lahir: Optional[date] = None
    model: Optional[str] = None
    brand_id: Optional[UUID] = None
    type: Optional[str] = None
    kapasitas: Optional[str] = None
    no_pol: Optional[str] = None
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

    @field_validator('nama', 'hp', 'alamat', mode='before')
    @classmethod
    def validate_required_text(cls, v):
        if v is None:
            raise ValueError("Field is required")
        if isinstance(v, str):
            v = v.strip()
        if v == "":
            raise ValueError("Field cannot be empty")
        return v

    @field_validator('email', 'model', 'type', 'kapasitas', 'no_pol', 'warna', 'no_mesin', 'no_rangka', mode='before')
    @classmethod
    def empty_optional_to_none(cls, v):
        if isinstance(v, str):
            v = v.strip()
        return v or None

class CreateCustomer(BaseModel):
    nama: str = Field(min_length=1)
    hp: str = Field(min_length=1)
    alamat: str = Field(min_length=1)
    email: Optional[str] = None
    tanggal_lahir: Optional[date] = None

    @field_validator('tanggal_lahir', mode='before')
    @classmethod
    def validate_tanggal_lahir(cls, v):
        if v == "":
            return None
        return v

    @field_validator('nama', 'hp', 'alamat', mode='before')
    @classmethod
    def validate_required_customer_text(cls, v):
        if v is None:
            raise ValueError("Field is required")
        if isinstance(v, str):
            v = v.strip()
        if v == "":
            raise ValueError("Field cannot be empty")
        return v

    @field_validator('email', mode='before')
    @classmethod
    def empty_email_to_none(cls, v):
        if isinstance(v, str):
            v = v.strip()
        return v or None

class CreateVehicle(BaseModel):
    model: Optional[str] = None
    brand_id: Optional[UUID] = None
    type: Optional[str] = None
    kapasitas: Optional[str] = None
    no_pol: Optional[str] = None
    tahun: Optional[int] = None
    warna: Optional[str] = None
    no_mesin: Optional[str] = None
    no_rangka: Optional[str] = None
    customer_id: UUID

class VehicleResponse(BaseModel):
    id: UUID
    model: Optional[str] = None
    brand_id: Optional[UUID] = None
    type: Optional[str] = None
    kapasitas: Optional[str] = None
    no_pol: Optional[str] = None
    tahun: Optional[int] = None
    warna: Optional[str] = None
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
