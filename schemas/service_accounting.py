# https://chatgpt.com/share/68e2fcb5-b030-800e-a2f6-7dc01047e10b

# schemas_accounting.py
from typing import List, Optional
from decimal import Decimal
from pydantic import BaseModel, Field, condecimal, ConfigDict, field_serializer
from datetime import date
from enum import Enum
from uuid import UUID




class JournalType(str, Enum):
    PURCHASE = "purchase"
    SALE = "sale"
    AR_RECEIPT = "ar_receipt"
    AP_PAYMENT = "ap_payment"
    CONSIGNMENT = "consignment"
    EXPENSE = "expense"
    GENERAL = "general"


# Reusable model for serializing Decimal fields to floats when dumping models.
# Placed early so other models can inherit from it.
class DecimalModel(BaseModel):
    model_config = ConfigDict()

    @field_serializer("*")
    def _serialize_decimal(self, v, info):
        if isinstance(v, Decimal):
            return float(v)
        return v

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


class JournalLineOut(DecimalModel):
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

class JournalEntryOut(DecimalModel):
    id: str
    entry_no: str
    date: date
    memo: Optional[str]
    journal_type: JournalType
    lines: List[JournalLineOut]

    model_config = ConfigDict(from_attributes=True)


class SalesWithConsignments(DecimalModel):
    sale: JournalEntryOut
    consignments: List[JournalEntryOut]

    model_config = ConfigDict(from_attributes=True)


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


class ConsignmentPaymentCreate(BaseModel):
    entry_no: Optional[str] = None
    tanggal: date
    supplier_id: Optional[UUID] = None
    amount: Decimal
    kas_bank_code: str
    hutang_konsinyasi_code: str = "3002"
    potongan_konsinyasi_code: Optional[str] = None
    discount: Optional[Decimal] = Decimal("0.00")
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
    piutang_code: str = "2001"


class PurchaseJournalEntry(BaseModel):
    date: date
    memo: Optional[str]
    supplier_id: Optional[UUID] = None
    purchase_id: Optional[UUID] = None
    
    harga_product: Decimal = Decimal("0.00")
    harga_service: Decimal = Decimal("0.00")
    hpp_product: Optional[Decimal] = None
    hpp_service: Optional[Decimal] = None
    pajak: Optional[Decimal] = Decimal("0.00")


class PurchasePaymentJournalEntry(BaseModel):
    date: date
    memo: Optional[str]
    supplier_id: Optional[UUID] = None
    purchase_id: Optional[UUID] = None
    amount: Decimal
    kas_bank_code: str
    hutang_code: str = "3001"


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


class LostGoodsJournalEntry(BaseModel):
    date: date
    memo: Optional[str]
    product_id: UUID
    quantity: Decimal
    loss_account_code: str = "6003"  # Kerugian Barang
    inventory_account_code: str = "2002"  # Persediaan Barang
    


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


class CashBookEntry(DecimalModel):
    date: date
    memo: Optional[str]
    debit: Decimal = Decimal("0.00")
    credit: Decimal = Decimal("0.00")
    balance: Decimal = Decimal("0.00")


class CashBookReport(DecimalModel):
    opening_balance: Decimal
    entries: List[CashBookEntry]

    model_config = ConfigDict()


class ExpenseReportRequest(BaseModel):
    start_date: date
    end_date: date
    expense_type: Optional[str] = None  # Filter by expense type, e.g., "listrik"
    status: Optional[str] = None  # Filter by status, e.g., "dibayarkan"


class ExpenseReportItem(DecimalModel):
    expense_type: str
    total_amount: Decimal
    count: int


class ExpenseReport(DecimalModel):
    total_expenses: Decimal
    total_count: int
    items: List[ExpenseReportItem]

    model_config = ConfigDict()


class ProfitLossReportRequest(BaseModel):
    start_date: date
    end_date: date


class ProfitLossReportItem(DecimalModel):
    account_code: str
    account_name: str
    amount: Decimal


class ProfitLossReport(DecimalModel):
    total_revenue: Decimal
    total_expenses: Decimal
    net_profit: Decimal
    revenues: List[ProfitLossReportItem]
    expenses: List[ProfitLossReportItem]

    model_config = ConfigDict()


class CashReportRequest(BaseModel):
    start_date: date
    end_date: date
    account_ids: Optional[List[UUID]] = None  # Filter by specific cash/bank accounts
    transaction_type: Optional[str] = None  # "cash_in", "cash_out", or None for both


class CashReportEntry(DecimalModel):
    date: date
    memo: Optional[str]
    account_code: str
    account_name: str
    amount: Decimal
    transaction_type: str  # "cash_in" or "cash_out"


class CashReport(DecimalModel):
    total_cash_in: Decimal
    total_cash_out: Decimal
    net_cash_flow: Decimal
    entries: List[CashReportEntry]

    model_config = ConfigDict()


class ReceivablePayableReportRequest(BaseModel):
    start_date: date
    end_date: date


class ReceivablePayableItem(DecimalModel):
    entity_id: str  # customer_id or supplier_id
    entity_name: str  # customer.nama or supplier.nama
    entity_type: str  # "customer" or "supplier"
    customer_id: Optional[str] = None  # customer_id if entity_type is customer
    supplier_id: Optional[str] = None  # supplier_id if entity_type is supplier
    total_receivable: Decimal  # for customers
    total_payable: Decimal  # for suppliers
    balance: Decimal  # receivable - payable (positive = receivable, negative = payable)


class ReceivablePayableReport(DecimalModel):
    total_receivable: Decimal
    total_payable: Decimal
    net_balance: Decimal
    items: List[ReceivablePayableItem]

    model_config = ConfigDict()


class ConsignmentPayableItem(DecimalModel):
    supplier_id: str
    supplier_name: str
    total_payable: Decimal


class ConsignmentPayableReport(DecimalModel):
    total_payable: Decimal
    items: List[ConsignmentPayableItem]

    model_config = ConfigDict()


class ProductSalesReportRequest(BaseModel):
    start_date: date
    end_date: date
    product_id: Optional[UUID] = None
    customer_id: Optional[UUID] = None


class ProductSalesReportItem(DecimalModel):
    workorder_no: str
    workorder_date: date
    customer_name: str
    product_name: str
    quantity: Decimal
    price: Decimal
    subtotal: Decimal
    discount: Decimal


class ProductSalesReport(DecimalModel):
    total_quantity: Decimal
    total_sales: Decimal
    items: List[ProductSalesReportItem]

    model_config = ConfigDict()


class ServiceSalesReportRequest(BaseModel):
    start_date: date
    end_date: date
    service_id: Optional[UUID] = None
    customer_id: Optional[UUID] = None


class ServiceSalesReportItem(DecimalModel):
    workorder_no: str
    workorder_date: date
    customer_name: str
    service_name: str
    quantity: Decimal
    price: Decimal
    subtotal: Decimal
    discount: Decimal


class ServiceSalesReport(DecimalModel):
    total_quantity: Decimal
    total_sales: Decimal
    items: List[ServiceSalesReportItem]

    model_config = ConfigDict()


class DailyReportRequest(BaseModel):
    date: date


class WorkOrderSummaryItem(DecimalModel):
    workorder_no: str
    customer_name: str
    total_biaya: Decimal
    status: str


class WorkOrderSummary(DecimalModel):
    total_workorders: int
    total_revenue: Decimal
    items: List[WorkOrderSummaryItem]

    model_config = ConfigDict()


class DailyReport(DecimalModel):
    date: date
    cash_book: CashBookReport
    product_sales: ProductSalesReport
    service_sales: ServiceSalesReport
    profit_loss: ProfitLossReport
    work_orders: WorkOrderSummary

    model_config = ConfigDict()













