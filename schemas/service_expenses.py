from pydantic import BaseModel, Field, field_validator
from uuid import UUID
from typing import Optional
import datetime
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
    expense_type: str = Field(min_length=1, max_length=100)
    status: ExpenseStatus
    amount: Decimal
    date: datetime.date
    bukti_transfer: Optional[str] = None

    @field_validator("expense_type", mode="before")
    @classmethod
    def validate_expense_type(cls, value):
        if not isinstance(value, str) or not value.strip():
            raise ValueError("Expense type cannot be empty")
        return value.strip()


class UpdateExpenses(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    expense_type: Optional[str] = Field(default=None, min_length=1, max_length=100)
    status: Optional[ExpenseStatus] = None
    amount: Optional[Decimal] = None
    date: Optional[datetime.date] = None
    bukti_transfer: Optional[str] = None

    @field_validator("expense_type", mode="before")
    @classmethod
    def validate_expense_type(cls, value):
        if value is None:
            return None
        if not isinstance(value, str) or not value.strip():
            raise ValueError("Expense type cannot be empty")
        return value.strip()


class ExpensesResponse(BaseModel):
    id: UUID
    name: str
    description: str
    expense_type: str
    status: ExpenseStatus
    amount: Decimal
    date: datetime.date
    bukti_transfer: Optional[str]
    created_at: datetime.datetime
    updated_at: datetime.datetime

    model_config = {
        "from_attributes": True
    }
