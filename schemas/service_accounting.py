# https://chatgpt.com/share/68e2fcb5-b030-800e-a2f6-7dc01047e10b

# schemas_accounting.py
from typing import List, Optional
from decimal import Decimal
from pydantic import BaseModel, Field, condecimal
from datetime import date
from enum import Enum
from uuid import UUID




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
    entry_no: Optional[str] = None
    date: date
    memo: Optional[str] = None
    customer_id: Optional[UUID] = None
    supplier_id: Optional[UUID] = None
    workorder_id: Optional[UUID] = None
    purchase_id: Optional[UUID] = None


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
    entry_no: Optional[str] = None
    tanggal: date
    supplier_id: Optional[UUID] = None
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
    entry_no: Optional[str] = None
    tanggal: date
    customer_id: Optional[UUID] = None
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
    entry_no: Optional[str] = None
    tanggal: date
    customer_id: Optional[UUID] = None
    amount: Decimal
    kas_bank_code: str
    piutang_code: str = "1200"
    potongan_penjualan_code: Optional[str] = None
    discount: Decimal = Decimal("0.00")
    memo: Optional[str] = None
    created_by: Optional[str] = "system"


class PaymentAPCreate(BaseModel):
    entry_no: Optional[str] = None
    tanggal: date
    supplier_id: Optional[UUID] = None
    amount: Decimal
    kas_bank_code: str
    hutang_code: str = "2100"
    potongan_pembelian_code: Optional[str] = None
    discount: Decimal = Decimal("0.00")
    memo: Optional[str] = None
    created_by: Optional[str] = "system"


class ExpenseRecordCreate(BaseModel):
    entry_no: Optional[str] = None
    tanggal: date
    kas_bank_code: str
    expense_code: str
    amount: Decimal
    ppn: Optional[Decimal] = Decimal("0.00")
    ppn_masukan_code: Optional[str] = None
    memo: Optional[str] = None
    created_by: Optional[str] = "system"


class SalesJournalEntry(BaseModel):
    date: date
    memo: Optional[str]
    customer_id: Optional[UUID] = None
    workorder_id: Optional[UUID] = None
    harga_product: Decimal = Decimal("0.00")
    harga_service: Decimal = Decimal("0.00")
    hpp_product: Optional[Decimal] = None
    hpp_service: Optional[Decimal] = None
    pajak: Optional[Decimal] = Decimal("0.00")


class SalesPaymentJournalEntry(BaseModel):
    date: date
    memo: Optional[str]
    customer_id: Optional[UUID] = None
    workorder_id: Optional[UUID] = None
    amount: Decimal
    kas_bank_code: str
    piutang_code: str = "1200"
    discount: Decimal = Decimal("0.00")
    potongan_penjualan_code: Optional[str] = None


class PurchaseJournalEntry(BaseModel):
    date: date
    memo: Optional[str]
    supplier_id: Optional[UUID] = None
    purchase_id: Optional[UUID] = None
    workorder_id: Optional[UUID] = None
    harga_product: Decimal = Decimal("0.00")
    harga_service: Decimal = Decimal("0.00")
    hpp_product: Optional[Decimal] = None
    hpp_service: Optional[Decimal] = None
    pajak: Optional[Decimal] = Decimal("0.00")


class PurchasePaymentJournalEntry(BaseModel):
    date: date
    memo: Optional[str]
    supplier_id: Optional[UUID] = None
    workorder_id: Optional[UUID] = None
    amount: Decimal
    kas_bank_code: str
    hutang_code: str = "2100"
    discount: Decimal = Decimal("0.00")
    potongan_pembelian_code: Optional[str] = None


class ExpenseJournalEntry(BaseModel):
    date: date
    memo: Optional[str]
    expense_id: UUID
    amount: Decimal
    kas_bank_code: str
    expense_code: str
    pajak: Optional[Decimal] = Decimal("0.00")
    ppn_masukan_code: Optional[str] = None


class ExpensePaymentJournalEntry(BaseModel):
    date: date
    memo: Optional[str]
    expense_id: Optional[UUID] = None
    amount: Decimal
    kas_bank_code: str
    expense_code: str = "6000"
    discount: Decimal = Decimal("0.00")
    potongan_biaya_code: Optional[str] = None


class CashInCreate(BaseModel):
    entry_no: Optional[str] = None
    tanggal: date
    kas_bank_code: str
    credit_account_code: str
    amount: Decimal
    memo: Optional[str] = None
    created_by: Optional[str] = "system"


class CashOutCreate(BaseModel):
    entry_no: Optional[str] = None
    tanggal: date
    kas_bank_code: str
    debit_account_code: str
    amount: Decimal
    memo: Optional[str] = None
    created_by: Optional[str] = "system"


class CashBookReportRequest(BaseModel):
    account_id: UUID
    start_date: date
    end_date: date


class CashBookEntry(BaseModel):
    date: date
    memo: Optional[str]
    debit: Decimal = Decimal("0.00")
    credit: Decimal = Decimal("0.00")
    balance: Decimal = Decimal("0.00")


class CashBookReport(BaseModel):
    opening_balance: Decimal
    entries: List[CashBookEntry]


class ExpenseReportRequest(BaseModel):
    start_date: date
    end_date: date
    expense_type: Optional[str] = None  # Filter by expense type, e.g., "listrik"
    status: Optional[str] = None  # Filter by status, e.g., "dibayarkan"


class ExpenseReportItem(BaseModel):
    expense_type: str
    total_amount: Decimal
    count: int


class ExpenseReport(BaseModel):
    total_expenses: Decimal
    total_count: int
    items: List[ExpenseReportItem]








