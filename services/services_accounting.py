# services_accounting.py
import uuid
from decimal import Decimal
from typing import Iterable, List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import select
from datetime import date
import decimal
import datetime

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
    CreateAccount,
    SalesJournalEntry,
    SalesPaymentJournalEntry,
    PurchaseJournalEntry,
    PurchasePaymentJournalEntry,
    ExpenseJournalEntry,
    ExpensePaymentJournalEntry
)

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


def _create_entry(db: Session, payload: JournalEntryCreate, created_by: Optional[str] = "system") -> JournalEntry:
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

    payload = JournalEntryCreate(
        entry_no=sale_data.entry_no,
        date=sale_data.tanggal,
        memo=sale_data.memo,
        journal_type=JT.SALE,
        supplier_id=None,
        customer_id=sale_data.customer_id,
        workorder_id=None,
        lines=lines
    )
    entry = _create_entry(db, payload, created_by=sale_data.created_by)
    return _to_entry_out(db, entry)


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
    from sqlalchemy import func
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
    """
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

    payload = JournalEntryCreate(
        entry_no=None,  # Auto-generate
        date=data_entry.date,
        memo=data_entry.memo,
        journal_type=JT.SALE,
        supplier_id=None,
        customer_id=data_entry.customer_id,
        workorder_id=data_entry.workorder_id,
        lines=lines
    )
    entry = _create_entry(db, payload, created_by="system")
    return _to_entry_out(db, entry)


def create_sales_payment_journal_entry(db: Session, data_entry: SalesPaymentJournalEntry) -> dict:
    """
    Create a sales payment journal entry (AR receipt).
    Dr Kas/Bank                        amount - discount
    Dr Potongan Penjualan (optional)   discount
       Cr Piutang Usaha                amount
    """
    cash_in = data_entry.amount - (data_entry.discount or Decimal("0.00"))
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
    if data_entry.discount and data_entry.discount > 0:
        if not data_entry.potongan_penjualan_code:
            raise ValueError("potongan_penjualan_code wajib diisi bila discount > 0")
        lines.append(JournalLineCreate(
            account_code=data_entry.potongan_penjualan_code,
            description="Diskon Pelunasan Piutang Penjualan",
            debit=data_entry.discount,
            credit=Decimal("0.00")
        ))

    payload = JournalEntryCreate(
        entry_no=None,  # Auto-generate
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
        workorder_id=data_entry.workorder_id,
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
    cash_out = data_entry.amount - (data_entry.discount or Decimal("0.00"))
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
    if data_entry.discount and data_entry.discount > 0:
        if not data_entry.potongan_pembelian_code:
            raise ValueError("potongan_pembelian_code wajib diisi bila discount > 0")
        lines.append(JournalLineCreate(
            account_code=data_entry.potongan_pembelian_code,
            description="Diskon Pembayaran Hutang Pembelian",
            debit=Decimal("0.00"),
            credit=data_entry.discount
        ))

    payload = JournalEntryCreate(
        entry_no=None,  # Auto-generate
        date=data_entry.date,
        memo=data_entry.memo,
        journal_type=JT.AP_PAYMENT,
        supplier_id=data_entry.supplier_id,
        customer_id=None,
        workorder_id=data_entry.workorder_id,
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
    Create an expense payment journal entry (similar to AP payment but for expenses).
    Dr Expense Account             amount - discount
    Dr Potongan Biaya (optional)   discount
       Cr Kas/Bank                 amount
    """
    cash_out = data_entry.amount - (data_entry.discount or Decimal("0.00"))
    lines: List[JournalLineCreate] = [
        JournalLineCreate(
            account_code=data_entry.expense_code,
            description="Pelunasan Biaya",
            debit=cash_out,
            credit=Decimal("0.00")
        ),
        JournalLineCreate(
            account_code=data_entry.kas_bank_code,
            description="Pembayaran Biaya",
            debit=Decimal("0.00"),
            credit=data_entry.amount
        ),
    ]
    if data_entry.discount and data_entry.discount > 0:
        if not data_entry.potongan_biaya_code:
            raise ValueError("potongan_biaya_code wajib diisi bila discount > 0")
        lines.append(JournalLineCreate(
            account_code=data_entry.potongan_biaya_code,
            description="Diskon Pembayaran Biaya",
            debit=data_entry.discount,
            credit=Decimal("0.00")
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
