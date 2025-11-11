# services_accounting.py
import uuid
from decimal import Decimal
from typing import Iterable, List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import func, select, Date
from datetime import date
import decimal
import datetime
from models.expenses import Expenses
from models.workorder import Workorder, ProductOrdered, Product, ServiceOrdered, Service
from models.customer import Customer
from models.supplier import Supplier

from models.accounting import Account, JournalEntry, JournalLine, JournalType
from schemas.service_accounting import (
    JournalEntryCreate,
    JournalEntryOut,
    JournalLineCreate,
    JournalType as JT,
    PurchaseRecordCreate,
    SaleRecordCreate,
    PaymentARCreate,
    PaymentAPCreate,
    ExpenseRecordCreate,
    ConsignmentPaymentCreate,
    CreateAccount,
    SalesJournalEntry,
    SalesPaymentJournalEntry,
    PurchaseJournalEntry,
    PurchasePaymentJournalEntry,
    ExpenseJournalEntry,
    ExpensePaymentJournalEntry,
    LostGoodsJournalEntry,
    CashInCreate,
    CashOutCreate,
    CashBookReportRequest,
    CashBookReport,
    CashBookEntry,
    ExpenseReportRequest,
    ExpenseReport,
    ExpenseReportItem,
    ProfitLossReportRequest,
    ProfitLossReport,
    ProfitLossReportItem,
    CashReportRequest,
    CashReport,
    CashReportEntry,
    ReceivablePayableReportRequest,
    ReceivablePayableReport,
    ReceivablePayableItem,
    ProductSalesReportRequest,
    ProductSalesReport,
    ProductSalesReportItem,
    ServiceSalesReportRequest,
    ServiceSalesReport,
    ServiceSalesReportItem,
    MechanicSalesReportRequest,
    MechanicSalesReport,
    MechanicSalesReportItem,
    MechanicProductSalesItem,
    MechanicServiceSalesItem,
    DailyReportRequest,
    DailyReport,
    WorkOrderSummary,
    WorkOrderSummaryItem
)
from collections import defaultdict

def to_dict(obj):
    result = {}
    for c in obj.__table__.columns:
        value = getattr(obj, c.name)
        # Konversi UUID ke string
        if isinstance(value, uuid.UUID):
            value = str(value)
        # Konversi Decimal ke float
        elif isinstance(value, decimal.Decimal):
            value = float(value)
        # Konversi datetime/date/time ke isoformat string
        elif isinstance(value, (datetime.datetime, datetime.date, datetime.time)):
            value = value.isoformat()
        # Konversi bytes ke string (opsional, jika ada kolom bytes)
        elif isinstance(value, bytes):
            value = value.decode('utf-8')
        result[c.name] = value
    return result

# ---------- Helpers ----------
def _get_account_by_code(db: Session, code: str) -> Account:
    """
    Retrieve an active account by its code.

    Args:
        db: Database session.
        code: Account code to search for.

    Returns:
        Account: The active account object.

    Raises:
        ValueError: If the account code is not found or inactive.
    """
    acc = db.execute(select(Account).where(Account.code == code, Account.is_active == True)).scalar_one_or_none()
    if not acc:
        raise ValueError(f"Account code '{code}' not found or inactive")
    return acc


def _sum(lines: Iterable[JournalLineCreate], key: str) -> Decimal:
    """
    Sum the values of a specific attribute across journal lines.

    Args:
        lines: Iterable of JournalLineCreate objects.
        key: Attribute name to sum (e.g., 'debit' or 'credit').

    Returns:
        Decimal: The total sum.
    """
    return sum(getattr(line, key) for line in lines)


def _validate_balance(lines: List[JournalLineCreate]) -> None:
    """
    Validate that the journal lines are balanced (total debit equals total credit).

    Args:
        lines: List of JournalLineCreate objects.

    Raises:
        ValueError: If the journal is not balanced.
    """
    total_debit = _sum(lines, "debit")
    total_credit = _sum(lines, "credit")
    if total_debit != total_credit:
        raise ValueError(f"Journal not balanced: debit {total_debit} != credit {total_credit}")


def _create_entry(db: Session, payload: JournalEntryCreate, created_by: Optional[str] = "system", commit: bool = True) -> JournalEntry:
    """
    Create a new journal entry in the database.

    Args:
        db: Database session.
        payload: JournalEntryCreate object with entry details.
        created_by: User who created the entry (default: "system").

    Returns:
        JournalEntry: The created journal entry object.
    """
    # Validate balance
    _validate_balance(payload.lines)

    # Generate entry_no if not provided
    entry_no = payload.entry_no if payload.entry_no else generate_entry_no(db, payload.journal_type.value, payload.date)

    entry = JournalEntry(
        id=uuid.uuid4(),
        entry_no=entry_no,
        date=payload.date,
        memo=payload.memo,
        journal_type=JournalType(payload.journal_type.value),
        customer_id=payload.customer_id,
        supplier_id=payload.supplier_id,
        workorder_id=payload.workorder_id,
        created_by=created_by,
    )
    db.add(entry)
    db.flush()  # Ensure entry.id is available

    for line in payload.lines:
        acc = _get_account_by_code(db, line.account_code)
        jl = JournalLine(
            id=uuid.uuid4(),
            entry_id=entry.id,
            account_id=acc.id,
            description=line.description,
            debit=line.debit,
            credit=line.credit,
        )
        db.add(jl)

    db.flush()  # Ensure lines are flushed to the database
    if commit:
        db.commit()  # Commit the transaction
    return entry


def _to_entry_out(db: Session, entry: JournalEntry) -> dict:
    """
    Convert a JournalEntry object to a dictionary for JSON serialization.

    Args:
        db: Database session (for loading relationships if needed).
        entry: JournalEntry object to convert.

    Returns:
        dict: The output dictionary.
    """
    # Ensure accounts are loaded
    lines_out = []
    for ln in entry.lines:
        lines_out.append({
            "account_code": ln.account.code,
            "account_name": ln.account.name,
            "description": ln.description,
            "debit": float(ln.debit),
            "credit": float(ln.credit),
        })
    return {
        "id": str(entry.id),
        "entry_no": entry.entry_no,
        "date": entry.date.isoformat() if entry.date else None,
        "memo": entry.memo,
        "journal_type": entry.journal_type.value,
        "lines": lines_out
    }


# ---------- API Tipe Jurnal Siap Pakai ----------

def record_purchase(
    db: Session,
    *,
    purchase_data: PurchaseRecordCreate
) -> dict:
    """
    Jurnal pembelian (perpetual):
    Dr Persediaan (atau Beban Pembelian)      xxx
    Dr PPN Masukan                             yyy (opsional)
       Cr Hutang Usaha / Kas/Bank             zzz

    Jika kas_bank_code diisi -> pembayaran tunai/bank (Cr ke kas/bank),
    kalau None -> Cr ke Hutang Usaha.
    """
    lines: List[JournalLineCreate] = []

    # Persediaan = total_bruto - potongan (sebelum pajak, sesuaikan kebutuhanmu)
    persediaan = purchase_data.total_bruto - purchase_data.potongan
    if persediaan > 0:
        lines.append(JournalLineCreate(
            account_code=purchase_data.persediaan_code,
            description="Pembelian",
            debit=persediaan,
            credit=Decimal("0.00")
        ))

    if purchase_data.ppn and purchase_data.ppn > 0:
        lines.append(JournalLineCreate(
            account_code=purchase_data.ppn_masukan_code,
            description="PPN Masukan",
            debit=purchase_data.ppn,
            credit=Decimal("0.00")
        ))

    total_credit = persediaan + purchase_data.ppn
    if purchase_data.kas_bank_code:
        lines.append(JournalLineCreate(
            account_code=purchase_data.kas_bank_code,
            description="Pembayaran Pembelian",
            debit=Decimal("0.00"),
            credit=total_credit
        ))
    else:
        lines.append(JournalLineCreate(
            account_code=purchase_data.hutang_code,
            description="Hutang Usaha atas Pembelian",
            debit=Decimal("0.00"),
            credit=total_credit
        ))

    payload = JournalEntryCreate(
        entry_no=purchase_data.entry_no,
        date=purchase_data.tanggal,
        memo=purchase_data.memo,
        journal_type=JT.PURCHASE,
        supplier_id=purchase_data.supplier_id,
        customer_id=None,
        workorder_id=None,
        lines=lines
    )
    entry = _create_entry(db, payload, created_by=purchase_data.created_by)
    return _to_entry_out(db, entry)


def record_sale(
    db: Session,
    *,
    sale_data: SaleRecordCreate
) -> dict:
    """
    Jurnal penjualan (perpetual):
    Dr Piutang/Kas-Bank                         total_bersih + PPN
       Cr Penjualan                             total_bersih
       Cr PPN Keluaran                          PPN
    + (opsional HPP):
    Dr HPP                                      hpp
       Cr Persediaan                            hpp
    """
    lines: List[JournalLineCreate] = []
    total_bersih = sale_data.total_penjualan - sale_data.potongan
    debit_receipt = total_bersih + (sale_data.ppn or Decimal("0.00"))

    if sale_data.kas_bank_code:
        lines.append(JournalLineCreate(
            account_code=sale_data.kas_bank_code,
            description="Penerimaan Penjualan",
            debit=debit_receipt,
            credit=Decimal("0.00")
        ))
    else:
        lines.append(JournalLineCreate(
            account_code=sale_data.piutang_code,
            description="Piutang Penjualan",
            debit=debit_receipt,
            credit=Decimal("0.00")
        ))

    if total_bersih > 0:
        lines.append(JournalLineCreate(
            account_code=sale_data.penjualan_code,
            description="Penjualan",
            debit=Decimal("0.00"),
            credit=total_bersih
        ))
    if sale_data.ppn and sale_data.ppn > 0:
        lines.append(JournalLineCreate(
            account_code=sale_data.ppn_keluaran_code,
            description="PPN Keluaran",
            debit=Decimal("0.00"),
            credit=sale_data.ppn
        ))

    # HPP opsional
    if sale_data.hpp and sale_data.hpp > 0 and sale_data.hpp_code and sale_data.persediaan_code:
        lines.append(JournalLineCreate(
            account_code=sale_data.hpp_code,
            description="HPP Penjualan",
            debit=sale_data.hpp,
            credit=Decimal("0.00")
        ))
        lines.append(JournalLineCreate(
            account_code=sale_data.persediaan_code,
            description="Pengurangan Persediaan",
            debit=Decimal("0.00"),
            credit=sale_data.hpp
        ))

    # Group consignment payables per supplier (if any) and create separate payable entries
    consign_by_supplier = defaultdict(Decimal)
    if sale_data.workorder_id:
        workorder = db.query(Workorder).filter(Workorder.id == sale_data.workorder_id).first()
        if workorder:
            for po in workorder.product_ordered:
                product = po.product
                # For consignment products, calculate payable based on product cost (HPP)
                if product and getattr(product, "is_consignment", False):
                    supplier_id = getattr(product, "supplier_id", None)
                    # Use product.cost (HPP) when available; if not present, skip or treat as zero
                    product_cost = getattr(product, "cost", None) or Decimal("0.00")
                    cost_amount = po.quantity * product_cost
                    if supplier_id and cost_amount and cost_amount > 0:
                        consign_by_supplier[supplier_id] += cost_amount

    # create sale entry and consignment payable entries in one transaction
    with db.begin():
        sale_payload = JournalEntryCreate(
            entry_no=sale_data.entry_no,
            date=sale_data.tanggal,
            memo=sale_data.memo,
            journal_type=JT.SALE,
            supplier_id=None,
            customer_id=sale_data.customer_id,
            workorder_id=sale_data.workorder_id,
            lines=lines
        )
        sale_entry = _create_entry(db, sale_payload, created_by=sale_data.created_by, commit=False)
        # For each consignor, create a separate JournalEntry for the payable
        cons_entries = []
        for supplier_id, amount in consign_by_supplier.items():
            if amount and amount > 0:
                acc_hpp = db.execute(select(Account).where(Account.code == "5001")).scalar_one_or_none()
                acc_payable = db.execute(select(Account).where(Account.code == "3002")).scalar_one_or_none()
                if not acc_hpp or not acc_payable:
                    raise ValueError("Akun untuk HPP atau hutang konsinyasi (5001/3002) belum tersedia")

                cons_entry = JournalEntry(
                    id=uuid.uuid4(),
                    entry_no=f"CONS-{uuid.uuid4().hex[:8]}",
                    date=sale_data.tanggal,
                    memo=f"Hutang konsinyasi untuk supplier {supplier_id} - WO {sale_data.workorder_id}",
                    journal_type=JournalType.CONSIGNMENT,
                    supplier_id=supplier_id,
                    customer_id=None,
                    workorder_id=sale_data.workorder_id,
                    created_by=sale_data.created_by,
                )
                db.add(cons_entry)
                db.flush()

                jl1 = JournalLine(
                    id=uuid.uuid4(),
                    entry_id=cons_entry.id,
                    account_id=acc_hpp.id,
                    description="HPP Konsinyasi (berdasarkan cost produk)",
                    debit=amount,
                    credit=Decimal("0.00")
                )
                jl2 = JournalLine(
                    id=uuid.uuid4(),
                    entry_id=cons_entry.id,
                    account_id=acc_payable.id,
                    description="Hutang Konsinyasi (berdasarkan cost produk)",
                    debit=Decimal("0.00"),
                    credit=amount
                )
                db.add_all([jl1, jl2])
                cons_entries.append(cons_entry)

    # convert sale and consignment entries to output schema
    sale_out = _to_entry_out(db, sale_entry)
    consign_outs = [_to_entry_out(db, ce) for ce in (cons_entries if 'cons_entries' in locals() else [])]

    return {
        "sale": sale_out,
        "consignments": consign_outs
    }


def receive_payment_ar(
    db: Session,
    *,
    payment_ar_data: PaymentARCreate
) -> dict:
    """
    Pembayaran piutang (pelunasan AR):
    Dr Kas/Bank                        amount - discount
    Dr Potongan Penjualan (opsional)   discount
       Cr Piutang Usaha                amount
    """
    cash_in = payment_ar_data.amount - (payment_ar_data.discount or Decimal("0.00"))
    lines: List[JournalLineCreate] = [
        JournalLineCreate(
            account_code=payment_ar_data.kas_bank_code,
            description="Terima Pelunasan Piutang",
            debit=cash_in,
            credit=Decimal("0.00")
        ),
        JournalLineCreate(
            account_code=payment_ar_data.piutang_code,
            description="Pelunasan Piutang",
            debit=Decimal("0.00"),
            credit=payment_ar_data.amount
        ),
    ]
    if payment_ar_data.discount and payment_ar_data.discount > 0:
        if not payment_ar_data.potongan_penjualan_code:
            raise ValueError("potongan_penjualan_code wajib diisi bila discount > 0")
        lines.append(JournalLineCreate(
            account_code=payment_ar_data.potongan_penjualan_code,
            description="Diskon Pelunasan Piutang",
            debit=payment_ar_data.discount,
            credit=Decimal("0.00")
        ))

    payload = JournalEntryCreate(
        entry_no=payment_ar_data.entry_no,
        date=payment_ar_data.tanggal,
        memo=payment_ar_data.memo,
        journal_type=JT.AR_RECEIPT,
        supplier_id=None,
        customer_id=payment_ar_data.customer_id,
        workorder_id=None,
        lines=lines
    )
    entry = _create_entry(db, payload, created_by=payment_ar_data.created_by)
    return _to_entry_out(db, entry)


def pay_ap(
    db: Session,
    *,
    payment_ap_data: PaymentAPCreate
) -> dict:
    """
    Pembayaran hutang (pelunasan AP):
    Dr Hutang Usaha                    amount
       Cr Kas/Bank                     amount - discount
       Cr Potongan Pembelian           discount (opsional)
    """
    cash_out = payment_ap_data.amount - (payment_ap_data.discount or Decimal("0.00"))
    lines: List[JournalLineCreate] = [
        JournalLineCreate(
            account_code=payment_ap_data.hutang_code,
            description="Pelunasan Hutang",
            debit=payment_ap_data.amount,
            credit=Decimal("0.00")
        ),
        JournalLineCreate(
            account_code=payment_ap_data.kas_bank_code,
            description="Pembayaran Hutang",
            debit=Decimal("0.00"),
            credit=cash_out
        ),
    ]
    if payment_ap_data.discount and payment_ap_data.discount > 0:
        if not payment_ap_data.potongan_pembelian_code:
            raise ValueError("potongan_pembelian_code wajib diisi bila discount > 0")
        lines.append(JournalLineCreate(
            account_code=payment_ap_data.potongan_pembelian_code,
            description="Diskon Pembayaran Hutang",
            debit=Decimal("0.00"),
            credit=payment_ap_data.discount
        ))

    payload = JournalEntryCreate(
        entry_no=payment_ap_data.entry_no,
        date=payment_ap_data.tanggal,
        memo=payment_ap_data.memo,
        journal_type=JT.AP_PAYMENT,
        supplier_id=payment_ap_data.supplier_id,
        customer_id=None,
        workorder_id=None,
        lines=lines
    )
    entry = _create_entry(db, payload, created_by=payment_ap_data.created_by)
    return _to_entry_out(db, entry)


def record_expense(
    db: Session,
    *,
    expense_data: ExpenseRecordCreate
) -> dict:
    """
    Pengeluaran biaya (tanpa hutang):
    Dr Beban XXX             amount (excl PPN)
    Dr PPN Masukan (ops)     ppn
       Cr Kas/Bank           amount + ppn
    """
    lines: List[JournalLineCreate] = [
        JournalLineCreate(
            account_code=expense_data.expense_code,
            description="Pengeluaran Biaya",
            debit=expense_data.amount,
            credit=Decimal("0.00")
        ),
    ]
    total_credit = expense_data.amount
    if expense_data.ppn and expense_data.ppn > 0:
        if not expense_data.ppn_masukan_code:
            raise ValueError("ppn_masukan_code wajib jika ppn > 0")
        lines.append(JournalLineCreate(
            account_code=expense_data.ppn_masukan_code,
            description="PPN Masukan",
            debit=expense_data.ppn,
            credit=Decimal("0.00")
        ))
        total_credit += expense_data.ppn

    lines.append(JournalLineCreate(
        account_code=expense_data.kas_bank_code,
        description="Pembayaran Biaya",
        debit=Decimal("0.00"),
        credit=total_credit
    ))

    payload = JournalEntryCreate(
        entry_no=expense_data.entry_no,
        date=expense_data.tanggal,
        memo=expense_data.memo,
        journal_type=JT.EXPENSE,
        supplier_id=None,
        customer_id=None,
        workorder_id=None,
        lines=lines
    )
    entry = _create_entry(db, payload, created_by=expense_data.created_by)
    return _to_entry_out(db, entry)

def create_account(db: Session, account_data: CreateAccount):
    # Create a new account
    new_account = Account(
        id=uuid.uuid4(),
        code=account_data.code,
        name=account_data.name,
        normal_balance=account_data.normal_balance,
        account_type=account_data.account_type,
        is_active=account_data.is_active
    )
    db.add(new_account)
    db.commit()
    db.refresh(new_account)

    return to_dict(new_account)

def edit_account(db: Session, account_id: str, account_data: CreateAccount):
    # Edit an existing account
    account = db.query(Account).filter(Account.id == account_id).first()
    if not account:
        raise ValueError(f"Account with id '{account_id}' not found")

    account.code = account_data.code
    account.name = account_data.name
    account.normal_balance = account_data.normal_balance
    account.account_type = account_data.account_type
    account.is_active = account_data.is_active

    db.commit()
    db.refresh(account)

    return to_dict(account)

def get_account(db: Session, account_id: str):
    account = db.query(Account).filter(Account.id == account_id).first()
    if not account:
        raise ValueError(f"Account with id '{account_id}' not found")
    return to_dict(account)

def get_all_accounts(db: Session):
    results = db.query(Account).all()
    return [to_dict(result) for result in results] if isinstance(results, Iterable) else []

def generate_entry_no(db: Session, journal_type: str, date: date) -> str:
    """
    Generate a unique entry_no that is not affected by deletions.
    Format: {journal_type_prefix}-{YYYYMMDD}-{sequential_number}

    Args:
        db: Database session.
        journal_type: Type of journal (e.g., 'purchase', 'sale').
        date: Date of the entry.

    Returns:
        str: Generated entry_no.
    """
    # Define prefixes for journal types
    prefixes = {
        'purchase': 'PUR',
        'sale': 'SAL',
        'ar_receipt': 'ARR',
        'ap_payment': 'APP',
        'expense': 'EXP',
        'general': 'GEN'
    }
    prefix = prefixes.get(journal_type, 'GEN')

    # Format date as YYYYMMDD
    date_str = date.strftime('%Y%m%d')

    # Find the next sequential number for this prefix and date
    max_entry_no = db.query(func.max(JournalEntry.entry_no)).filter(
        JournalEntry.entry_no.like(f'{prefix}-{date_str}-%')
    ).scalar()

    if max_entry_no:
        # Extract the sequential number and increment
        parts = max_entry_no.split('-')
        if len(parts) == 3:
            seq_num = int(parts[2]) + 1
        else:
            seq_num = 1
    else:
        seq_num = 1

    # Generate the new entry_no
    entry_no = f'{prefix}-{date_str}-{seq_num:03d}'  # Pad with zeros to 3 digits
    return entry_no


def create_sales_journal_entry(db: Session, data_entry: SalesJournalEntry) -> dict:
    """
    Create a sales journal entry for product and service sales (perpetual inventory).
    Assumes piutang (receivable) for sales, with HPP for costs.
    Also handles consignment commission for consignment products.
    """
    # Check if sale journal already exists for this workorder
    existing_sale = db.query(JournalEntry).filter(
        JournalEntry.journal_type == JT.SALE,
        JournalEntry.workorder_id == data_entry.workorder_id
    ).first()
    if existing_sale:
        raise ValueError(f"Sale journal already exists for workorder {data_entry.workorder_id}")

    lines: List[JournalLineCreate] = []

    # Calculate totals
    total_product = data_entry.harga_product
    total_service = data_entry.harga_service
    total_sales = total_product + total_service
    total_tax = data_entry.pajak or Decimal("0.00")
    total_debit = total_sales + total_tax

    # Debit Piutang (receivable) for total sales + tax
    lines.append(JournalLineCreate(
        account_code="2001",  # Piutang Usaha
        description="Piutang Penjualan",
        debit=total_debit,
        credit=Decimal("0.00")
    ))

    # Credit Penjualan Product (if any)
    if total_product > 0:
        lines.append(JournalLineCreate(
            account_code="4001",  # Penjualan
            description="Penjualan Produk",
            debit=Decimal("0.00"),
            credit=total_product
        ))

    # Credit Penjualan Service (if any)
    if total_service > 0:
        lines.append(JournalLineCreate(
            account_code="4002",  # Assume separate for service, or adjust
            description="Penjualan Jasa",
            debit=Decimal("0.00"),
            credit=total_service
        ))

    # Credit PPN Keluaran (tax)
    if total_tax > 0:
        lines.append(JournalLineCreate(
            account_code="2410",  # PPN Keluaran
            description="PPN Keluaran",
            debit=Decimal("0.00"),
            credit=total_tax
        ))

    # HPP for Product (if provided)
    if data_entry.hpp_product and data_entry.hpp_product > 0:
        lines.append(JournalLineCreate(
            account_code="5001",  # HPP
            description="HPP Produk",
            debit=data_entry.hpp_product,
            credit=Decimal("0.00")
        ))
        lines.append(JournalLineCreate(
            account_code="2002",  # Persediaan
            description="Pengurangan Persediaan Produk",
            debit=Decimal("0.00"),
            credit=data_entry.hpp_product
        ))

    # HPP for Service (if provided, assuming service cost)
    if data_entry.hpp_service and data_entry.hpp_service > 0:
        lines.append(JournalLineCreate(
            account_code="5002",  # Assume separate HPP for service
            description="HPP Jasa",
            debit=data_entry.hpp_service,
            credit=Decimal("0.00")
        ))
        lines.append(JournalLineCreate(
            account_code="6002",  # Assume expense for service cost
            description="Biaya Jasa",
            debit=Decimal("0.00"),
            credit=data_entry.hpp_service
        ))

    # Calculate and record consignment commission if workorder has consignment products
    # Group consignment commissions per supplier (if any)
    consign_by_supplier = defaultdict(Decimal)
    if data_entry.workorder_id:
        workorder = db.query(Workorder).filter(Workorder.id == data_entry.workorder_id).first()
        if workorder:
            for po in workorder.product_ordered:
                product = po.product
                # For consignment products, use product cost (HPP) as the payable base
                if product and getattr(product, "is_consignment", False):
                    supplier_id = getattr(product, "supplier_id", None)
                    product_cost = getattr(product, "cost", None) or Decimal("0.00")
                    cost_amount = po.quantity * product_cost
                    if supplier_id and cost_amount and cost_amount > 0:
                        consign_by_supplier[supplier_id] += cost_amount

    # Create sale entry and consignment payable entries
    sale_payload = JournalEntryCreate(
        entry_no=None,  # Auto-generate
        date=data_entry.date,
        memo=data_entry.memo,
        journal_type=JT.SALE,
        supplier_id=None,
        customer_id=data_entry.customer_id,
        workorder_id=data_entry.workorder_id,
        lines=lines
    )
    sale_entry = _create_entry(db, sale_payload, created_by="system", commit=False)

    cons_entries = []
    for supplier_id, amount in consign_by_supplier.items():
        if amount and amount > 0:
            # Use HPP (5001) as the debit account for consignment payable clearing
            acc_hpp = db.execute(select(Account).where(Account.code == "5001")).scalar_one_or_none()
            acc_payable = db.execute(select(Account).where(Account.code == "3002")).scalar_one_or_none()
            if not acc_hpp or not acc_payable:
                raise ValueError("Akun untuk HPP atau hutang konsinyasi (5001/3002) belum tersedia")

            cons_entry = JournalEntry(
                id=uuid.uuid4(),
                entry_no=f"CONS-{uuid.uuid4().hex[:8]}",
                date=data_entry.date,
                memo=f"Hutang konsinyasi untuk supplier {supplier_id} - WO {data_entry.workorder_id}",
                journal_type=JournalType.consignment,
                supplier_id=supplier_id,
                customer_id=None,
                workorder_id=data_entry.workorder_id,
                created_by="system",
            )
            db.add(cons_entry)
            db.flush()

            jl1 = JournalLine(
                id=uuid.uuid4(),
                entry_id=cons_entry.id,
                account_id=acc_hpp.id,
                description="HPP/Pembayaran Konsinyasi (berdasarkan cost produk)",
                debit=amount,
                credit=Decimal("0.00")
            )
            jl2 = JournalLine(
                id=uuid.uuid4(),
                entry_id=cons_entry.id,
                account_id=acc_payable.id,
                description="Hutang Konsinyasi (berdasarkan cost produk)",
                debit=Decimal("0.00"),
                credit=amount
            )
            db.add_all([jl1, jl2])
            cons_entries.append(cons_entry)

    db.commit()

    sale_out = _to_entry_out(db, sale_entry)
    consign_outs = [_to_entry_out(db, ce) for ce in cons_entries]
    return {"sale": sale_out, "consignments": consign_outs}


def cash_in(
    db: Session,
    *,
    cash_in_data: CashInCreate
) -> dict:
    """
    General cash-in transaction:
    Dr Kas/Bank                        amount
       Cr Specified Account             amount
    """
    lines: List[JournalLineCreate] = [
        JournalLineCreate(
            account_code=cash_in_data.kas_bank_code,
            description="Cash In",
            debit=cash_in_data.amount,
            credit=Decimal("0.00")
        ),
        JournalLineCreate(
            account_code=cash_in_data.credit_account_code,
            description="Cash In",
            debit=Decimal("0.00"),
            credit=cash_in_data.amount
        ),
    ]

    payload = JournalEntryCreate(
        entry_no=cash_in_data.entry_no,
        date=cash_in_data.tanggal,
        memo=cash_in_data.memo,
        journal_type=JT.GENERAL,
        supplier_id=None,
        customer_id=None,
        workorder_id=None,
        lines=lines
    )
    entry = _create_entry(db, payload, created_by=cash_in_data.created_by)
    return _to_entry_out(db, entry)


def cash_out(
    db: Session,
    *,
    cash_out_data: CashOutCreate
) -> dict:
    """
    General cash-out transaction:
    Dr Specified Account               amount
       Cr Kas/Bank                      amount
    """
    lines: List[JournalLineCreate] = [
        JournalLineCreate(
            account_code=cash_out_data.debit_account_code,
            description="Cash Out",
            debit=cash_out_data.amount,
            credit=Decimal("0.00")
        ),
        JournalLineCreate(
            account_code=cash_out_data.kas_bank_code,
            description="Cash Out",
            debit=Decimal("0.00"),
            credit=cash_out_data.amount
        ),
    ]

    payload = JournalEntryCreate(
        entry_no=cash_out_data.entry_no,
        date=cash_out_data.tanggal,
        memo=cash_out_data.memo,
        journal_type=JT.GENERAL,
        supplier_id=None,
        customer_id=None,
        workorder_id=None,
        lines=lines
    )
    entry = _create_entry(db, payload, created_by=cash_out_data.created_by)
    return _to_entry_out(db, entry)


def create_sales_payment_journal_entry(db: Session, data_entry: SalesPaymentJournalEntry) -> dict:
    """
    Create a sales payment journal entry (AR receipt).
    Dr Kas/Bank                        amount - discount
    Dr Potongan Penjualan (optional)   discount
       Cr Piutang Usaha                amount
    """
    # Check if payment journal already exists for this payment_no to prevent double payment
    existing_payment = db.query(JournalEntry).filter(
        JournalEntry.entry_no == data_entry.payment_no
    ).first()
    if existing_payment:
        raise ValueError(f"Payment journal already exists for payment_no {data_entry.payment_no}")

    cash_in = data_entry.amount
    lines: List[JournalLineCreate] = [
        JournalLineCreate(
            account_code=data_entry.kas_bank_code,
            description="Terima Pelunasan Piutang Penjualan",
            debit=cash_in,
            credit=Decimal("0.00")
        ),
        JournalLineCreate(
            account_code=data_entry.piutang_code,
            description="Pelunasan Piutang Penjualan",
            debit=Decimal("0.00"),
            credit=data_entry.amount
        ),
    ]

    payload = JournalEntryCreate(
        entry_no=data_entry.payment_no,  # Use payment_no as entry_no
        date=data_entry.date,
        memo=data_entry.memo,
        journal_type=JT.AR_RECEIPT,
        supplier_id=None,
        customer_id=data_entry.customer_id,
        workorder_id=data_entry.workorder_id,
        lines=lines
    )
    entry = _create_entry(db, payload, created_by="system")
    return _to_entry_out(db, entry)

def create_purchase_journal_entry(db: Session, data_entry: PurchaseJournalEntry) -> dict:
    """
    Create a purchase journal entry for product and service purchases (perpetual inventory).
    Assumes hutang (payable) for purchases, with HPP for costs.
    """
    lines: List[JournalLineCreate] = []

    # Calculate totals
    total_product = data_entry.harga_product
    total_service = data_entry.harga_service
    total_purchases = total_product + total_service
    total_tax = data_entry.pajak or Decimal("0.00")
    total_credit = total_purchases + total_tax

    # Debit Persediaan (inventory) for total purchases + tax
    lines.append(JournalLineCreate(
        account_code="2002",  # Persediaan
        description="Pembelian Persediaan",
        debit=total_credit,
        credit=Decimal("0.00")
    ))

    # Credit Hutang Usaha (payable) for total purchases + tax
    lines.append(JournalLineCreate(
        account_code="3001",  # Hutang Usaha
        description="Hutang Pembelian",
        debit=Decimal("0.00"),
        credit=total_credit
    ))

    # HPP for Product (if provided, but for purchase, it's the cost)
    # For purchase, HPP is not debited here; it's when sold.
    # But if we want to record cost, perhaps debit expense or something, but typically for perpetual, inventory is debited.

    # For service purchases, if it's a cost, debit expense
    if data_entry.hpp_service and data_entry.hpp_service > 0:
        lines.append(JournalLineCreate(
            account_code="6002",  # Assume expense for service cost
            description="Biaya Jasa Pembelian",
            debit=data_entry.hpp_service,
            credit=Decimal("0.00")
        ))
        lines.append(JournalLineCreate(
            account_code="3001",  # Hutang Usaha
            description="Hutang Biaya Jasa",
            debit=Decimal("0.00"),
            credit=data_entry.hpp_service
        ))

    payload = JournalEntryCreate(
        entry_no=None,  # Auto-generate
        date=data_entry.date,
        memo=data_entry.memo,
        journal_type=JT.PURCHASE,
        supplier_id=data_entry.supplier_id,
        customer_id=None,
        purchase_id=data_entry.purchase_id,
        lines=lines
    )
    entry = _create_entry(db, payload, created_by="system")
    return _to_entry_out(db, entry)


def create_purchase_payment_journal_entry(db: Session, data_entry: PurchasePaymentJournalEntry) -> dict:
    """
    Create a purchase payment journal entry (AP payment).
    Dr Hutang Usaha                    amount
    Cr Kas/Bank                     amount - discount
    Cr Potongan Pembelian           discount (optional)
    """
    # Check if payment journal already exists for this payment_no to prevent double payment
    existing_payment = db.query(JournalEntry).filter(
        JournalEntry.entry_no == data_entry.payment_no
    ).first()
    if existing_payment:
        raise ValueError(f"Payment journal already exists for payment_no {data_entry.payment_no}")

    cash_out = data_entry.amount
    lines: List[JournalLineCreate] = [
        JournalLineCreate(
            account_code=data_entry.hutang_code,
            description="Pelunasan Hutang Pembelian",
            debit=data_entry.amount,
            credit=Decimal("0.00")
        ),
        JournalLineCreate(
            account_code=data_entry.kas_bank_code,
            description="Pembayaran Hutang Pembelian",
            debit=Decimal("0.00"),
            credit=cash_out
        ),
    ]


    payload = JournalEntryCreate(
        entry_no=data_entry.payment_no,  # Use payment_no as entry_no
        date=data_entry.date,
        memo=data_entry.memo,
        journal_type=JT.AP_PAYMENT,
        supplier_id=data_entry.supplier_id,
        customer_id=None,
        purchase_id=data_entry.purchase_id,
        lines=lines
    )
    entry = _create_entry(db, payload, created_by="system")
    return _to_entry_out(db, entry)


def create_expense_journal_entry(db: Session, data_entry: ExpenseJournalEntry) -> dict:
    """
    Create an expense journal entry when an expense is paid.
    Dr Expense Account             amount (excl PPN)
    Dr PPN Masukan (optional)      pajak
       Cr Kas/Bank                 amount + pajak
    """
    lines: List[JournalLineCreate] = [
        JournalLineCreate(
            account_code=data_entry.expense_code,
            description="Pengeluaran Biaya",
            debit=data_entry.amount,
            credit=Decimal("0.00")
        ),
    ]
    total_credit = data_entry.amount
    if data_entry.pajak and data_entry.pajak > 0:
        if not data_entry.ppn_masukan_code:
            raise ValueError("ppn_masukan_code wajib jika pajak > 0")
        lines.append(JournalLineCreate(
            account_code=data_entry.ppn_masukan_code,
            description="PPN Masukan",
            debit=data_entry.pajak,
            credit=Decimal("0.00")
        ))
        total_credit += data_entry.pajak

    lines.append(JournalLineCreate(
        account_code=data_entry.kas_bank_code,
        description="Pembayaran Biaya",
        debit=Decimal("0.00"),
        credit=total_credit
    ))

    payload = JournalEntryCreate(
        entry_no=None,  # Auto-generate
        date=data_entry.date,
        memo=data_entry.memo,
        journal_type=JT.EXPENSE,
        supplier_id=None,
        customer_id=None,
        workorder_id=None,
        lines=lines
    )
    entry = _create_entry(db, payload, created_by="system")
    return _to_entry_out(db, entry)


def create_expense_payment_journal_entry(db: Session, data_entry: ExpensePaymentJournalEntry) -> dict:
    """
    Create an expense payment journal entry.
    Dr Expense Account             amount
       Cr Kas/Bank                 amount
    """
    # Check if payment journal already exists for this payment_no to prevent double payment
    existing_payment = db.query(JournalEntry).filter(
        JournalEntry.entry_no == data_entry.payment_no
    ).first()
    if existing_payment:
        raise ValueError(f"Payment journal already exists for payment_no {data_entry.payment_no}")

    lines: List[JournalLineCreate] = [
        JournalLineCreate(
            account_code=data_entry.expense_code,
            description="Pelunasan Biaya",
            debit=data_entry.amount,
            credit=Decimal("0.00")
        ),
        JournalLineCreate(
            account_code=data_entry.kas_bank_code,
            description="Pembayaran Biaya",
            debit=Decimal("0.00"),
            credit=data_entry.amount
        ),
    ]

    payload = JournalEntryCreate(
        entry_no=data_entry.payment_no,  # Use payment_no as entry_no
        date=data_entry.date,
        memo=data_entry.memo,
        journal_type=JT.EXPENSE,
        supplier_id=None,
        customer_id=None,
        workorder_id=None,
        lines=lines
    )
    entry = _create_entry(db, payload, created_by="system")
    from services.services_expenses import edit_expense_status
    edit_expense_status(db, data_entry.expense_id)
    return _to_entry_out(db, entry)


def create_lost_goods_journal_entry(db: Session, data_entry: LostGoodsJournalEntry) -> dict:
    """
    Create a lost goods journal entry.
    Dr Loss Account (Kerugian Barang)    amount
       Cr Inventory Account (Persediaan Barang)    amount
    """
    if data_entry.quantity <= 0:
        raise ValueError("Quantity must be positive for lost goods entry")

    # Get product cost from database
    from models.workorder import Product
    product = db.query(Product).filter(Product.id == data_entry.product_id).first()
    if not product:
        raise ValueError(f"Product with id '{data_entry.product_id}' not found")
    if not product.cost:
        raise ValueError(f"Product '{product.name}' does not have a cost defined")

    amount = product.cost * data_entry.quantity

    lines: List[JournalLineCreate] = [
        JournalLineCreate(
            account_code=data_entry.loss_account_code,
            description="Kerugian Barang",
            debit=amount,
            credit=Decimal("0.00")
        ),
        JournalLineCreate(
            account_code=data_entry.inventory_account_code,
            description="Pengurangan Persediaan Barang",
            debit=Decimal("0.00"),
            credit=amount
        ),
    ]

    payload = JournalEntryCreate(
        entry_no=None,  # Auto-generate
        date=data_entry.date,
        memo=data_entry.memo,
        journal_type=JT.EXPENSE,  # Or JT.GENERAL, depending on classification
        supplier_id=None,
        customer_id=None,
        workorder_id=None,
        lines=lines
    )
    entry = _create_entry(db, payload, created_by="system")
    return _to_entry_out(db, entry)


def generate_cash_book_report(db: Session, request: CashBookReportRequest) -> CashBookReport:
    """
    Generate a cash book report for a specific account within a date range.
    Includes opening balance, all transactions (cash-in and cash-out), and running balance.
    """
    # Get the account
    account = db.query(Account).filter(Account.id == request.account_id).first()
    if not account:
        raise ValueError(f"Account with id '{request.account_id}' not found")

    # Calculate opening balance (sum of all transactions before start_date)
    # Adjust based on normal_balance
    if account.normal_balance == "debit":
        net_change_expr = (JournalLine.debit - JournalLine.credit).label('net_change')
    else:
        net_change_expr = (JournalLine.credit - JournalLine.debit).label('net_change')

    opening_balance_query = db.query(net_change_expr).join(JournalEntry).filter(
        JournalLine.account_id == request.account_id,
        JournalEntry.date < request.start_date
    )
    opening_balance_result = db.execute(opening_balance_query).all()
    opening_balance = sum(row.net_change for row in opening_balance_result)

    # Get all journal lines for the account within the date range, ordered by date
    lines_query = db.query(JournalLine, JournalEntry).join(JournalEntry).filter(
        JournalLine.account_id == request.account_id,
        JournalEntry.date >= request.start_date,
        JournalEntry.date <= request.end_date
    ).order_by(JournalEntry.date, JournalEntry.created_at)

    entries = []
    running_balance = opening_balance

    for line, entry in lines_query:
        # Determine debit and credit based on normal balance
        if account.normal_balance == "debit":
            debit = line.debit
            credit = line.credit
        else:
            # For credit normal accounts, reverse the signs for cash book
            debit = line.credit
            credit = line.debit

        # Update running balance
        running_balance += debit - credit

        entries.append(CashBookEntry(
            date=entry.date,
            memo=entry.memo,
            debit=debit,
            credit=credit,
            balance=running_balance
        ))

    return CashBookReport(
        opening_balance=opening_balance,
        entries=entries
    )


def generate_expense_report(db: Session, request: ExpenseReportRequest) -> ExpenseReport:
    """
    Generate an expense report within a date range, optionally filtered by expense_type and status.
    Summarizes total expenses and counts by expense type.
    """
    

    # Build query
    query = db.query(Expenses).filter(
        Expenses.date >= request.start_date,
        Expenses.date <= request.end_date
    )

    if request.expense_type:
        query = query.filter(Expenses.expense_type == request.expense_type)

    if request.status:
        query = query.filter(Expenses.status == request.status)

    expenses = query.all()

    # Aggregate by expense_type
    from collections import defaultdict
    summary = defaultdict(lambda: {"total_amount": Decimal("0.00"), "count": 0})

    total_expenses = Decimal("0.00")
    total_count = 0

    for exp in expenses:
        exp_type = exp.expense_type.value
        summary[exp_type]["total_amount"] += exp.amount
        summary[exp_type]["count"] += 1
        total_expenses += exp.amount
        total_count += 1

    # Convert to list of ExpenseReportItem
    items = [
        ExpenseReportItem(
            expense_type=exp_type,
            total_amount=data["total_amount"],
            count=data["count"]
        )
        for exp_type, data in summary.items()
    ]

    return ExpenseReport(
        total_expenses=total_expenses,
        total_count=total_count,
        items=items
    )

def getBankCodes(db: Session):
    banks = db.query(Account).filter(Account.code.like("10%")).all()
    result = []
    for banku in banks:
        b_dict = to_dict(banku)
        result.append(b_dict)
    return result

def getEquityCodes(db: Session):
    banks = db.query(Account).filter(Account.code.like("90%")).all()
    result = []
    for banku in banks:
        b_dict = to_dict(banku)
        result.append(b_dict)
    return result

def getTarikCodes(db: Session):
    banks = db.query(Account).filter(Account.code.like("22%")).all()
    result = []
    for banku in banks:
        b_dict = to_dict(banku)
        result.append(b_dict)
    return result


def generate_profit_loss_report(db: Session, request: ProfitLossReportRequest) -> ProfitLossReport:
    """
    Generate a profit and loss report within a date range.
    Summarizes total revenue and total expenses, calculates net profit.
    """
    # Get all revenue accounts (account_type == 'revenue')
    revenue_accounts = db.query(Account).filter(Account.account_type == 'revenue', Account.is_active == True).all()
    revenue_account_ids = [acc.id for acc in revenue_accounts]

    # Get all expense accounts (account_type == 'expense')
    expense_accounts = db.query(Account).filter(Account.account_type == 'expense', Account.is_active == True).all()
    expense_account_ids = [acc.id for acc in expense_accounts]

    # Calculate total revenue: sum of credits for revenue accounts (since revenue is credited)
    revenue_query = db.query(
        (JournalLine.credit - JournalLine.debit).label('net_revenue')
    ).join(JournalEntry).filter(
        JournalLine.account_id.in_(revenue_account_ids),
        JournalEntry.date >= request.start_date,
        JournalEntry.date <= request.end_date
    )
    revenue_result = db.execute(revenue_query).all()
    total_revenue = sum(row.net_revenue for row in revenue_result)

    # Calculate total expenses: sum of debits for expense accounts (since expenses are debited)
    expense_query = db.query(
        (JournalLine.debit - JournalLine.credit).label('net_expense')
    ).join(JournalEntry).filter(
        JournalLine.account_id.in_(expense_account_ids),
        JournalEntry.date >= request.start_date,
        JournalEntry.date <= request.end_date
    )
    expense_result = db.execute(expense_query).all()
    total_expenses = sum(row.net_expense for row in expense_result)

    # Calculate net profit
    net_profit = total_revenue - total_expenses

    # Build revenue items
    revenues = []
    for acc in revenue_accounts:
        rev_query = db.query(
            (JournalLine.credit - JournalLine.debit).label('amount')
        ).join(JournalEntry).filter(
            JournalLine.account_id == acc.id,
            JournalEntry.date >= request.start_date,
            JournalEntry.date <= request.end_date
        )
        rev_amount = sum(row.amount for row in db.execute(rev_query).all())
        if rev_amount != 0:
            revenues.append(ProfitLossReportItem(
                account_code=acc.code,
                account_name=acc.name,
                amount=rev_amount
            ))

    # Build expense items
    expenses = []
    for acc in expense_accounts:
        exp_query = db.query(
            (JournalLine.debit - JournalLine.credit).label('amount')
        ).join(JournalEntry).filter(
            JournalLine.account_id == acc.id,
            JournalEntry.date >= request.start_date,
            JournalEntry.date <= request.end_date
        )
        exp_amount = sum(row.amount for row in db.execute(exp_query).all())
        if exp_amount != 0:
            expenses.append(ProfitLossReportItem(
                account_code=acc.code,
                account_name=acc.name,
                amount=exp_amount
            ))

    return ProfitLossReport(
        total_revenue=total_revenue,
        total_expenses=total_expenses,
        net_profit=net_profit,
        revenues=revenues,
        expenses=expenses
    )


def generate_cash_report(db: Session, request: CashReportRequest) -> CashReport:
    """
    Generate a cash report within a date range, optionally filtered by account_ids and transaction_type.
    Summarizes cash-in and cash-out transactions.
    """
    # Get cash/bank accounts (assuming account_type == 'asset' and code starts with '1' for cash/bank)
    cash_accounts_query = db.query(Account).filter(Account.account_type == 'asset', Account.code.like('1%'), Account.is_active == True)
    if request.account_ids:
        cash_accounts_query = cash_accounts_query.filter(Account.id.in_(request.account_ids))
    cash_accounts = cash_accounts_query.all()
    cash_account_ids = [acc.id for acc in cash_accounts]

    # Query journal lines for cash accounts within date range
    lines_query = db.query(JournalLine, JournalEntry, Account).join(JournalEntry).join(Account).filter(
        JournalLine.account_id.in_(cash_account_ids),
        JournalEntry.date >= request.start_date,
        JournalEntry.date <= request.end_date
    ).order_by(JournalEntry.date)

    entries = []
    total_cash_in = Decimal("0.00")
    total_cash_out = Decimal("0.00")

    for line, entry, account in lines_query:
        # Determine transaction type based on normal balance
        if account.normal_balance == "debit":
            # Debit increases cash (cash_in), credit decreases cash (cash_out)
            if line.debit > 0:
                transaction_type = "cash_in"
                amount = line.debit
                total_cash_in += amount
            elif line.credit > 0:
                transaction_type = "cash_out"
                amount = line.credit
                total_cash_out += amount
            else:
                continue  # Skip zero amounts
        else:
            # For credit normal accounts, reverse
            if line.credit > 0:
                transaction_type = "cash_in"
                amount = line.credit
                total_cash_in += amount
            elif line.debit > 0:
                transaction_type = "cash_out"
                amount = line.debit
                total_cash_out += amount
            else:
                continue

        # Filter by transaction_type if specified
        if request.transaction_type and transaction_type != request.transaction_type:
            continue

        entries.append(CashReportEntry(
            date=entry.date,
            memo=entry.memo,
            account_code=account.code,
            account_name=account.name,
            amount=amount,
            transaction_type=transaction_type
        ))

    net_cash_flow = total_cash_in - total_cash_out

    return CashReport(
        total_cash_in=total_cash_in,
        total_cash_out=total_cash_out,
        net_cash_flow=net_cash_flow,
        entries=entries
    )

def generate_receivable_payable_report(db: Session, request: ReceivablePayableReportRequest):

    # Get all customers with receivable balances
    customer_receivables = db.query(
        Customer.id.label('entity_id'),
        Customer.nama.label('entity_name'),
        func.sum(
            func.coalesce(
                select(func.sum(JournalLine.debit - JournalLine.credit))
                .join(JournalEntry, JournalLine.entry_id == JournalEntry.id)
                .where(JournalLine.account_id == select(Account.id).where(Account.code == '2001'))
                .where(JournalEntry.customer_id == Customer.id)
                .where(JournalEntry.date >= request.start_date)
                .where(JournalEntry.date <= request.end_date)
                .scalar_subquery(), 0
            )
        ).label('total_receivable')
    ).group_by(Customer.id, Customer.nama).all()

    # Get all suppliers with payable balances
    supplier_payables = db.query(
        Supplier.id.label('entity_id'),
        Supplier.nama.label('entity_name'),
        func.sum(
            func.coalesce(
                select(func.sum(JournalLine.credit - JournalLine.debit))
                .join(JournalEntry, JournalLine.entry_id == JournalEntry.id)
                .where(JournalLine.account_id == select(Account.id).where(Account.code == '3001'))
                .where(JournalEntry.supplier_id == Supplier.id)
                .where(JournalEntry.date >= request.start_date)
                .where(JournalEntry.date <= request.end_date)
                .scalar_subquery(), 0
            )
        ).label('total_payable')
    ).group_by(Supplier.id, Supplier.nama).all()

    items = []
    total_receivable = Decimal("0.00")
    total_payable = Decimal("0.00")

    # Process customers (receivables)
    for cust in customer_receivables:
        if cust.total_receivable > 0:
            item = ReceivablePayableItem(
                entity_id=str(cust.entity_id),
                entity_name=cust.entity_name,
                entity_type="customer",
                customer_id=str(cust.entity_id),
                supplier_id=None,
                total_receivable=cust.total_receivable,
                total_payable=Decimal("0.00"),
                balance=cust.total_receivable
            )
            items.append(item)
            total_receivable += cust.total_receivable

    # Process suppliers (payables)
    for supp in supplier_payables:
        if supp.total_payable > 0:
            item = ReceivablePayableItem(
                entity_id=str(supp.entity_id),
                entity_name=supp.entity_name,
                entity_type="supplier",
                customer_id=None,
                supplier_id=str(supp.entity_id),
                total_receivable=Decimal("0.00"),
                total_payable=supp.total_payable,
                balance=-supp.total_payable
            )
            items.append(item)
            total_payable += supp.total_payable

    net_balance = total_receivable - total_payable

    return ReceivablePayableReport(
        total_receivable=total_receivable,
        total_payable=total_payable,
        net_balance=net_balance,
        items=items
    )


def generate_consignment_payable_report(db: Session, request: ReceivablePayableReportRequest) -> dict:
    """
    Generate a report of consignment payables per supplier within a date range.
    Sums JournalLine (credit - debit) for the consignment payable account (code '3002').
    """
    # find consignment payable account id
    cons_acc = db.query(Account).filter(Account.code == '3002').first()
    if not cons_acc:
        # nothing to report if account doesn't exist
        return {"total_payable": Decimal("0.00"), "items": []}

    # aggregate by supplier
    rows = db.query(
        Supplier.id.label('supplier_id'),
        Supplier.nama.label('supplier_name'),
        func.sum((JournalLine.credit - JournalLine.debit)).label('total_payable')
    ).join(JournalEntry, JournalLine.entry_id == JournalEntry.id)
    rows = rows.join(Supplier, JournalEntry.supplier_id == Supplier.id)
    rows = rows.filter(
        JournalLine.account_id == cons_acc.id,
        JournalEntry.date >= request.start_date,
        JournalEntry.date <= request.end_date
    ).group_by(Supplier.id, Supplier.nama).all()

    items = []
    total = Decimal("0.00")
    for r in rows:
        tp = r.total_payable or Decimal("0.00")
        if tp != 0:
            items.append({
                "supplier_id": str(r.supplier_id),
                "supplier_name": r.supplier_name,
                "total_payable": tp
            })
            total += tp

    return {"total_payable": total, "items": items}


def generate_product_sales_report(db: Session, request: ProductSalesReportRequest) -> ProductSalesReport:
    """
    Generate a product sales report within a date range.
    Lists each product line sold in workorders, with totals for quantity and sales.
    Optionally filters by product_id and customer_id.
    """


    # Query product_ordered joined with workorder, product, customer
    query = db.query(
        Workorder.no_wo,
        Workorder.tanggal_masuk,
        Customer.nama.label('customer_name'),
        Product.name.label('product_name'),
        ProductOrdered.quantity,
        ProductOrdered.price,
        ProductOrdered.subtotal,
        ProductOrdered.discount
    ).join(ProductOrdered, Workorder.id == ProductOrdered.workorder_id)\
     .join(Product, ProductOrdered.product_id == Product.id)\
     .join(Customer, Workorder.customer_id == Customer.id)\
     .filter(Workorder.tanggal_masuk >= request.start_date)\
     .filter(Workorder.tanggal_masuk < request.end_date + datetime.timedelta(days=1))

    if request.product_id:
        query = query.filter(ProductOrdered.product_id == request.product_id)

    if request.customer_id:
        query = query.filter(Workorder.customer_id == request.customer_id)

    query = query.order_by(Workorder.tanggal_masuk, Workorder.no_wo)

    results = query.all()

    items = []
    total_quantity = Decimal("0.00")
    total_sales = Decimal("0.00")

    for row in results:
        item = ProductSalesReportItem(
            workorder_no=row.no_wo,
            workorder_date=row.tanggal_masuk.date() if isinstance(row.tanggal_masuk, datetime.datetime) else row.tanggal_masuk,
            customer_name=row.customer_name,
            product_name=row.product_name,
            quantity=row.quantity,
            price=row.price,
            subtotal=row.subtotal,
            discount=row.discount
        )
        items.append(item)
        total_quantity += row.quantity
        total_sales += row.subtotal

    return ProductSalesReport(
        total_quantity=total_quantity,
        total_sales=total_sales,
        items=items
    )


def generate_service_sales_report(db: Session, request: ServiceSalesReportRequest) -> ServiceSalesReport:
    """
    Generate a service sales report within a date range.
    Lists each service line sold in workorders, with totals for quantity and sales.
    Optionally filters by service_id and customer_id.
    """
    from models.workorder import Workorder, ServiceOrdered, Service
    from models.customer import Customer
    from sqlalchemy import func

    # Query service_ordered joined with workorder, service, customer
    query = db.query(
        Workorder.no_wo,
        Workorder.tanggal_masuk,
        Customer.nama.label('customer_name'),
        Service.name.label('service_name'),
        ServiceOrdered.quantity,
        ServiceOrdered.price,
        ServiceOrdered.subtotal,
        ServiceOrdered.discount
    ).join(ServiceOrdered, Workorder.id == ServiceOrdered.workorder_id)\
     .join(Service, ServiceOrdered.service_id == Service.id)\
     .join(Customer, Workorder.customer_id == Customer.id)\
     .filter(func.date(Workorder.tanggal_masuk) >= request.start_date)\
     .filter(func.date(Workorder.tanggal_masuk) <= request.end_date)

    if request.service_id:
        query = query.filter(ServiceOrdered.service_id == request.service_id)

    if request.customer_id:
        query = query.filter(Workorder.customer_id == request.customer_id)

    query = query.order_by(Workorder.tanggal_masuk, Workorder.no_wo)

    results = query.all()

    items = []
    total_quantity = Decimal("0.00")
    total_sales = Decimal("0.00")

    for row in results:
        # Calculate subtotal as quantity * price - discount
        calculated_subtotal = row.quantity * row.price - row.discount
        item = ServiceSalesReportItem(
            workorder_no=row.no_wo,
            workorder_date=row.tanggal_masuk.date() if isinstance(row.tanggal_masuk, datetime.datetime) else row.tanggal_masuk,
            customer_name=row.customer_name,
            service_name=row.service_name,
            quantity=row.quantity,
            price=row.price,
            subtotal=calculated_subtotal,
            discount=row.discount
        )
        items.append(item)
        total_quantity += row.quantity
        total_sales += calculated_subtotal

    return ServiceSalesReport(
        total_quantity=total_quantity,
        total_sales=total_sales,
        items=items
    )


def consignment_payment(
    db: Session,
    *,
    payment_data: ConsignmentPaymentCreate
) -> dict:
    """
    Pembayaran hutang konsinyasi (consignment payable):
    Dr Hutang Konsinyasi                    amount
       Cr Kas/Bank                         amount - discount
       Cr Potongan Konsinyasi              discount (opsional)
    """
    discount = payment_data.discount or Decimal("0.00")
    cash_out = payment_data.amount - discount
    lines: List[JournalLineCreate] = [
        JournalLineCreate(
            account_code=payment_data.hutang_konsinyasi_code,
            description="Pelunasan Hutang Konsinyasi",
            debit=payment_data.amount,
            credit=Decimal("0.00")
        ),
        JournalLineCreate(
            account_code=payment_data.kas_bank_code,
            description="Pembayaran Hutang Konsinyasi",
            debit=Decimal("0.00"),
            credit=cash_out
        ),
    ]
    if discount > 0:
        if not payment_data.potongan_konsinyasi_code:
            raise ValueError("potongan_konsinyasi_code wajib diisi bila discount > 0")
        lines.append(JournalLineCreate(
            account_code=payment_data.potongan_konsinyasi_code,
            description="Diskon Pembayaran Hutang Konsinyasi",
            debit=Decimal("0.00"),
            credit=discount
        ))

    payload = JournalEntryCreate(
        entry_no=payment_data.entry_no,
        date=payment_data.tanggal,
        memo=payment_data.memo,
        journal_type=JT.CONSIGNMENT,
        supplier_id=payment_data.supplier_id,
        customer_id=None,
        workorder_id=None,
        lines=lines
    )
    entry = _create_entry(db, payload, created_by=payment_data.created_by)
    return _to_entry_out(db, entry)


def generate_daily_report(db: Session, request: DailyReportRequest) -> DailyReport:
    """
    Generate a comprehensive daily report combining multiple reports for a specific date.
    Includes cash book for all cash/bank accounts combined, product sales, service sales, profit/loss, and work order summary.
    """
    # Use the date as both start and end for single day
    start_date = request.date
    end_date = request.date

    # Generate cash book reports for each account 1001-1004
    # Get the accounts 1001 to 1004
    cash_accounts = db.query(Account).filter(
        Account.code.in_(['1001', '1002', '1003', '1004']),
        Account.is_active == True
    ).all()

    cash_books = []
    for account in cash_accounts:
        # Calculate opening balance for this account
        if account.normal_balance == "debit":
            net_change_expr = (JournalLine.debit - JournalLine.credit).label('net_change')
        else:
            net_change_expr = (JournalLine.credit - JournalLine.debit).label('net_change')

        opening_balance_query = db.query(net_change_expr).join(JournalEntry).filter(
            JournalLine.account_id == account.id,
            JournalEntry.date < start_date
        )
        opening_balance = sum(row.net_change for row in db.execute(opening_balance_query).all())

        # Get entries for this account within the date range
        lines_query = db.query(JournalLine, JournalEntry).join(JournalEntry).filter(
            JournalLine.account_id == account.id,
            JournalEntry.date >= start_date,
            JournalEntry.date <= end_date
        ).order_by(JournalEntry.date, JournalEntry.created_at)

        entries = []
        running_balance = opening_balance

        for line, entry in lines_query:
            # Determine debit and credit based on normal balance
            if account.normal_balance == "debit":
                debit = line.debit
                credit = line.credit
            else:
                # For credit normal accounts, reverse the signs for cash book
                debit = line.credit
                credit = line.debit

            # Update running balance
            running_balance += debit - credit

            entries.append(CashBookEntry(
                date=entry.date,
                memo=entry.memo,
                debit=debit,
                credit=credit,
                balance=running_balance
            ))

        cash_book = CashBookReport(
            account_code=account.code,
            account_name=account.name,
            opening_balance=opening_balance,
            entries=entries
        )
        cash_books.append(cash_book)

    product_sales_request = ProductSalesReportRequest(
        start_date=start_date,
        end_date=end_date
    )
    product_sales = generate_product_sales_report(db, product_sales_request)

    service_sales_request = ServiceSalesReportRequest(
        start_date=start_date,
        end_date=end_date
    )
    service_sales = generate_service_sales_report(db, service_sales_request)

    profit_loss_request = ProfitLossReportRequest(
        start_date=start_date,
        end_date=end_date
    )
    profit_loss = generate_profit_loss_report(db, profit_loss_request)

    # Generate work order summary
    work_orders = generate_work_order_summary(db, start_date, end_date)

    return DailyReport(
        date=request.date,
        cash_books=cash_books,
        product_sales=product_sales,
        service_sales=service_sales,
        profit_loss=profit_loss,
        work_orders=work_orders
    )


def generate_work_order_summary(db: Session, start_date: date, end_date: date) -> WorkOrderSummary:
    """
    Generate a summary of work orders within a date range.
    """
    # Query workorders with customer info
    query = db.query(
        Workorder.no_wo,
        Customer.nama.label('customer_name'),
        Workorder.total_biaya,
        Workorder.status
    ).join(Customer, Workorder.customer_id == Customer.id)\
     .filter(func.date(Workorder.tanggal_masuk) >= start_date)\
     .filter(func.date(Workorder.tanggal_masuk) <= end_date)\
     .order_by(Workorder.tanggal_masuk, Workorder.no_wo)

    results = query.all()

    items = []
    total_workorders = 0
    total_revenue = Decimal("0.00")

    for row in results:
        item = WorkOrderSummaryItem(
            workorder_no=row.no_wo,
            customer_name=row.customer_name,
            total_biaya=row.total_biaya,
            status=row.status
        )
        items.append(item)
        total_workorders += 1
        total_revenue += row.total_biaya

    return WorkOrderSummary(
        total_workorders=total_workorders,
        total_revenue=total_revenue,
        items=items
    )


def generate_mechanic_sales_report(db: Session, request: MechanicSalesReportRequest) -> MechanicSalesReport:
    """
    Generate a sales report grouped by mechanic (karyawan) and date.
    Includes product and service sales for each mechanic per day with detailed breakdowns.
    """
    from models.karyawan import Karyawan

    # Query detailed product sales by mechanic and date
    product_detail_query = db.query(
        Karyawan.id.label('mechanic_id'),
        Karyawan.nama.label('mechanic_name'),
        func.date(Workorder.tanggal_masuk).label('date'),
        Workorder.no_wo,
        Workorder.tanggal_masuk,
        Customer.nama.label('customer_name'),
        Product.name.label('product_name'),
        ProductOrdered.quantity,
        ProductOrdered.price,
        ProductOrdered.subtotal,
        ProductOrdered.discount
    ).join(Workorder, Karyawan.id == Workorder.karyawan_id)\
     .join(ProductOrdered, Workorder.id == ProductOrdered.workorder_id)\
     .join(Product, ProductOrdered.product_id == Product.id)\
     .join(Customer, Workorder.customer_id == Customer.id)\
     .filter(func.date(Workorder.tanggal_masuk) >= request.start_date)\
     .filter(func.date(Workorder.tanggal_masuk) <= request.end_date)\
     .order_by(Karyawan.nama, func.date(Workorder.tanggal_masuk), Workorder.no_wo)

    product_details = product_detail_query.all()

    # Query detailed service sales by mechanic and date
    service_detail_query = db.query(
        Karyawan.id.label('mechanic_id'),
        Karyawan.nama.label('mechanic_name'),
        func.date(Workorder.tanggal_masuk).label('date'),
        Workorder.no_wo,
        Workorder.tanggal_masuk,
        Customer.nama.label('customer_name'),
        Service.name.label('service_name'),
        ServiceOrdered.quantity,
        ServiceOrdered.price,
        ServiceOrdered.subtotal,
        ServiceOrdered.discount
    ).join(Workorder, Karyawan.id == Workorder.karyawan_id)\
     .join(ServiceOrdered, Workorder.id == ServiceOrdered.workorder_id)\
     .join(Service, ServiceOrdered.service_id == Service.id)\
     .join(Customer, Workorder.customer_id == Customer.id)\
     .filter(func.date(Workorder.tanggal_masuk) >= request.start_date)\
     .filter(func.date(Workorder.tanggal_masuk) <= request.end_date)\
     .order_by(Karyawan.nama, func.date(Workorder.tanggal_masuk), Workorder.no_wo)

    service_details = service_detail_query.all()

    # Group by mechanic and date
    mechanic_data = {}

    # Process product details
    for row in product_details:
        key = (row.mechanic_id, row.date)
        if key not in mechanic_data:
            mechanic_data[key] = {
                'mechanic_name': row.mechanic_name,
                'product_sales': Decimal("0.00"),
                'service_sales': Decimal("0.00"),
                'product_details': [],
                'service_details': []
            }
        mechanic_data[key]['product_sales'] += row.subtotal
        mechanic_data[key]['product_details'].append(MechanicProductSalesItem(
            workorder_no=row.no_wo,
            workorder_date=row.tanggal_masuk.date() if isinstance(row.tanggal_masuk, datetime.datetime) else row.tanggal_masuk,
            customer_name=row.customer_name,
            product_name=row.product_name,
            quantity=row.quantity,
            price=row.price,
            subtotal=row.subtotal,
            discount=row.discount
        ))

    # Process service details
    for row in service_details:
        key = (row.mechanic_id, row.date)
        if key not in mechanic_data:
            mechanic_data[key] = {
                'mechanic_name': row.mechanic_name,
                'product_sales': Decimal("0.00"),
                'service_sales': Decimal("0.00"),
                'product_details': [],
                'service_details': []
            }
        mechanic_data[key]['service_sales'] += row.subtotal
        mechanic_data[key]['service_details'].append(MechanicServiceSalesItem(
            workorder_no=row.no_wo,
            workorder_date=row.tanggal_masuk.date() if isinstance(row.tanggal_masuk, datetime.datetime) else row.tanggal_masuk,
            customer_name=row.customer_name,
            service_name=row.service_name,
            quantity=row.quantity,
            price=row.price,
            subtotal=row.subtotal,
            discount=row.discount
        ))

    items = []
    total_product_sales = Decimal("0.00")
    total_service_sales = Decimal("0.00")

    for (mechanic_id, date_key), data in mechanic_data.items():
        product_sales = data['product_sales']
        service_sales = data['service_sales']
        total_sales = product_sales + service_sales

        # Get mechanic name
        mechanic_name = data['mechanic_name']

        item = MechanicSalesReportItem(
            mechanic_id=str(mechanic_id),
            mechanic_name=mechanic_name,
            date=date_key,
            total_product_sales=product_sales,
            total_service_sales=service_sales,
            total_sales=total_sales,
            product_details=data['product_details'],
            service_details=data['service_details']
        )
        items.append(item)
        total_product_sales += product_sales
        total_service_sales += service_sales

    total_sales = total_product_sales + total_service_sales

    return MechanicSalesReport(
        total_product_sales=total_product_sales,
        total_service_sales=total_service_sales,
        total_sales=total_sales,
        items=items
    )
