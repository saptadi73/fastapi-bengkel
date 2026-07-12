from pydantic import BaseModel, Field, field_validator
from typing import Optional
from uuid import UUID
from datetime import date

class CreateSupplier(BaseModel):
    supplier_code: Optional[str] = None
    nama: str = Field(min_length=1)
    hp: str = Field(min_length=1)
    alamat: str = Field(min_length=1)
    email: Optional[str] = None
    npwp: Optional[str] = None
    perusahaan: Optional[str] = None
    toko: Optional[str] = None

    @field_validator("nama", "hp", "alamat", mode="before")
    @classmethod
    def validate_required_text(cls, value):
        if value is None:
            raise ValueError("Field is required")
        if isinstance(value, str):
            value = value.strip()
        if value == "":
            raise ValueError("Field cannot be empty")
        return value

    @field_validator("supplier_code", "email", "npwp", "perusahaan", "toko", mode="before")
    @classmethod
    def empty_optional_to_none(cls, value):
        if isinstance(value, str):
            value = value.strip()
        return value or None

class UpdateSupplier(BaseModel):
    supplier_code: Optional[str] = None
    nama: Optional[str] = None
    hp: Optional[str] = None
    alamat: Optional[str] = None
    email: Optional[str] = None
    npwp: Optional[str] = None
    perusahaan: Optional[str] = None
    toko: Optional[str] = None

    @field_validator("nama", "hp", "alamat", mode="before")
    @classmethod
    def validate_optional_required_text(cls, value):
        if value is None:
            return None
        if isinstance(value, str):
            value = value.strip()
        if value == "":
            raise ValueError("Field cannot be empty")
        return value

    @field_validator("supplier_code", "email", "npwp", "perusahaan", "toko", mode="before")
    @classmethod
    def empty_optional_update_to_none(cls, value):
        if isinstance(value, str):
            value = value.strip()
        return value or None

class SupplierResponse(BaseModel):
    id: UUID
    nama: str
    supplier_code: Optional[str] = None
    hp: str
    alamat: Optional[str] = None
    email: Optional[str] = None
    npwp: Optional[str] = None
    perusahaan: Optional[str] = None
    toko: Optional[str] = None
    created_at: date
    updated_at: date

    model_config = {
        "from_attributes": True
    }
