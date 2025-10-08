from pydantic import BaseModel
from uuid import UUID
from typing import Optional
from datetime import date, datetime
from decimal import Decimal


class CreateExpenses(BaseModel):
    description: str
    amount: Decimal
    date: date
    bukti_transfer: Optional[str] = None


class UpdateExpenses(BaseModel):
    description: Optional[str] = None
    amount: Optional[Decimal] = None
    date: Optional[date] = None
    bukti_transfer: Optional[str] = None


class ExpensesResponse(BaseModel):
    id: UUID
    description: str
    amount: Decimal
    date: date
    bukti_transfer: Optional[str]
    created_at: datetime
    updated_at: datetime

    model_config = {
        "from_attributes": True
    }
