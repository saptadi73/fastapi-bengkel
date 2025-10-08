# https://chatgpt.com/share/68e2fcb5-b030-800e-a2f6-7dc01047e10b

# schemas_accounting.py
from typing import List, Optional
from decimal import Decimal
from pydantic import BaseModel, Field, condecimal
from datetime import date
from enum import Enum


class JournalType(str, Enum):
    PURCHASE = "purchase"
    SALE = "sale"
    AR_RECEIPT = "ar_receipt"
    AP_PAYMENT = "ap_payment"
    EXPENSE = "expense"
    GENERAL = "general"


class JournalLineCreate(BaseModel):
    account_code: str = Field(..., description="Kode COA, contoh: 1100")
    description: Optional[str] = None
    debit: Decimal = Decimal("0.00")
    credit: Decimal = Decimal("0.00")


class JournalEntryBase(BaseModel):
    entry_no: str
    date: date
    memo: Optional[str] = None
    customer_id: Optional[str] = None
    supplier_id: Optional[str] = None
    workorder_id: Optional[str] = None


class JournalEntryCreate(JournalEntryBase):
    journal_type: JournalType
    lines: List[JournalLineCreate]


class JournalLineOut(BaseModel):
    account_code: str
    account_name: str
    description: Optional[str]
    debit: Decimal
    credit: Decimal

class CreateAccount(BaseModel):
    code: str
    name: str
    normal_balance: str  # 'debit' or 'credit'
    account_type: str  # e.g., 'asset', 'liability', 'equity', 'revenue', 'expense'
    is_active: Optional[bool] = True

class JournalEntryOut(BaseModel):
    id: str
    entry_no: str
    date: date
    memo: Optional[str]
    journal_type: JournalType
    lines: List[JournalLineOut]

    class Config:
        from_attributes = True


class PurchaseRecordCreate(BaseModel):
    entry_no: str
    tanggal: date
    supplier_id: Optional[str] = None
    total_bruto: Decimal
    ppn: Decimal = Decimal("0.00")
    potongan: Decimal = Decimal("0.00")
    kas_bank_code: Optional[str] = None
    hutang_code: str = "2100"
    persediaan_code: str = "1300"
    ppn_masukan_code: str = "1510"
    memo: Optional[str] = None
    created_by: Optional[str] = "system"


class SaleRecordCreate(BaseModel):
    entry_no: str
    tanggal: date
    customer_id: Optional[str] = None
    total_penjualan: Decimal
    ppn: Decimal = Decimal("0.00")
    potongan: Decimal = Decimal("0.00")
    kas_bank_code: Optional[str] = None
    piutang_code: str = "1200"
    penjualan_code: str = "4000"
    ppn_keluaran_code: str = "2410"
    hpp_code: Optional[str] = "5100"
    persediaan_code: Optional[str] = "1300"
    hpp: Optional[Decimal] = None
    memo: Optional[str] = None
    created_by: Optional[str] = "system"


class PaymentARCreate(BaseModel):
    entry_no: str
    tanggal: date
    customer_id: Optional[str] = None
    amount: Decimal
    kas_bank_code: str
    piutang_code: str = "1200"
    potongan_penjualan_code: Optional[str] = None
    discount: Decimal = Decimal("0.00")
    memo: Optional[str] = None
    created_by: Optional[str] = "system"


class PaymentAPCreate(BaseModel):
    entry_no: str
    tanggal: date
    supplier_id: Optional[str] = None
    amount: Decimal
    kas_bank_code: str
    hutang_code: str = "2100"
    potongan_pembelian_code: Optional[str] = None
    discount: Decimal = Decimal("0.00")
    memo: Optional[str] = None
    created_by: Optional[str] = "system"


class ExpenseRecordCreate(BaseModel):
    entry_no: str
    tanggal: date
    kas_bank_code: str
    expense_code: str
    amount: Decimal
    ppn: Decimal = Decimal("0.00")
    ppn_masukan_code: Optional[str] = None
    memo: Optional[str] = None
    created_by: Optional[str] = "system"
