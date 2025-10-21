from pydantic import BaseModel, field_validator
from typing import List, Optional
from uuid import UUID
from decimal import Decimal
from datetime import date

class CreateKaryawan(BaseModel):
    nama: str
    hp: str
    alamat: Optional[str] = None
    email: Optional[str] = None
    tanggal_lahir: Optional[date] = None
    posisi: Optional[str] = None
    gaji: Optional[Decimal] = None

    @field_validator('tanggal_lahir', mode='before')
    @classmethod
    def validate_tanggal_lahir(cls, v):
        if v == "":
            return None
        return v
