from pydantic import BaseModel
from uuid import UUID
from typing import Optional

class CreateVehicle(BaseModel):
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
