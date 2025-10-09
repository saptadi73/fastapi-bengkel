from pydantic import BaseModel
from uuid import UUID
from typing import Optional
from datetime import date, datetime
from decimal import Decimal
from enum import Enum

class ExpenseType(str, Enum):
    listrik = "listrik"
    gaji = "gaji"
    air = "air"
    internet = "internet"
    transportasi = "transportasi"
    komunikasi = "komunikasi"
    konsumsi = "konsumsi"
    entertaint = "entertaint"
    umum = "umum"
    lain_lain = "lain-lain"

class ExpenseStatus(str, Enum):
    open = "open"
    dibayarkan = "dibayarkan"

class CreateExpenses(BaseModel):
    name: str
    description: str
    expense_type: ExpenseType
    status: ExpenseStatus
    amount: Decimal
    date: date
    bukti_transfer: Optional[str] = None


class UpdateExpenses(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    expense_type: Optional[ExpenseType] = None
    status: Optional[ExpenseStatus] = None
    amount: Optional[Decimal] = None
    date: Optional[date] = None
    bukti_transfer: Optional[str] = None


class ExpensesResponse(BaseModel):
    id: UUID
    name: str
    description: str
    expense_type: ExpenseType
    status: ExpenseStatus
    amount: Decimal
    date: date
    bukti_transfer: Optional[str]
    created_at: datetime
    updated_at: datetime

    model_config = {
        "from_attributes": True
    }
