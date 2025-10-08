from pydantic import BaseModel
from typing import Optional
from uuid import UUID
from datetime import date

class CreateSupplier(BaseModel):
    nama: str
    hp: str
    alamat: Optional[str] = None
    email: Optional[str] = None
    npwp: Optional[str] = None
    perusahaan: Optional[str] = None
    toko: Optional[str] = None

class UpdateSupplier(BaseModel):
    nama: Optional[str] = None
    hp: Optional[str] = None
    alamat: Optional[str] = None
    email: Optional[str] = None
    npwp: Optional[str] = None
    perusahaan: Optional[str] = None
    toko: Optional[str] = None

class SupplierResponse(BaseModel):
    id: UUID
    nama: str
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
