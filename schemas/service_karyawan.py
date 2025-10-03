from pydantic import BaseModel
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