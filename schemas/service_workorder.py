from pydantic import BaseModel
from uuid import UUID
from typing import Optional

class CreateWorkorderOnly(BaseModel):
    customer_id: UUID
    vehicle_id: UUID
    status: Optional[str] = 'open'
    # Tambahkan field lain jika perlu
