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
    CreateAccount
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

def create_account(db: Session, account_data: CreateAccount):
    # Create a new account
    new_account = Account(
        id=uuid.uuid4(),
        code=account_data.code,
        name=account_data.name,
        normal_balance=account_data.normal_balance,
        is_active=account_data.is_active
    )
    db.add(new_account)
    db.commit()
    db.refresh(new_account)

    return to_dict(new_account)

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
    return to_dict(acc)


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

    entry = JournalEntry(
        id=uuid.uuid4(),
        entry_no=payload.entry_no,
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

    return entry


def _to_entry_out(db: Session, entry: JournalEntry) -> JournalEntryOut:
    """
    Convert a JournalEntry object to JournalEntryOut schema.

    Args:
        db: Database session (for loading relationships if needed).
        entry: JournalEntry object to convert.

    Returns:
        JournalEntryOut: The output schema object.
    """
    # Ensure accounts are loaded
    lines_out = []
    for ln in entry.lines:
        lines_out.append({
            "account_code": ln.account.code,
            "account_name": ln.account.name,
            "description": ln.description,
            "debit": ln.debit,
            "credit": ln.credit,
        })
    return JournalEntryOut(
        id=str(entry.id),
        entry_no=entry.entry_no,
        date=entry.date,
        memo=entry.memo,
        journal_type=JT(entry.journal_type.value),
        lines=lines_out
    )


# ---------- API Tipe Jurnal Siap Pakai ----------

def record_purchase(
    db: Session,
    *,
    purchase_data: PurchaseRecordCreate
) -> JournalEntryOut:
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
    with db.begin():
        entry = _create_entry(db, payload, created_by=purchase_data.created_by)
    return _to_entry_out(db, entry)


def record_sale(
    db: Session,
    *,
    sale_data: SaleRecordCreate
) -> JournalEntryOut:
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
    with db.begin():
        entry = _create_entry(db, payload, created_by=sale_data.created_by)
    return _to_entry_out(db, entry)


def receive_payment_ar(
    db: Session,
    *,
    payment_ar_data: PaymentARCreate
) -> JournalEntryOut:
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
    with db.begin():
        entry = _create_entry(db, payload, created_by=payment_ar_data.created_by)
    return _to_entry_out(db, entry)


def pay_ap(
    db: Session,
    *,
    payment_ap_data: PaymentAPCreate
) -> JournalEntryOut:
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
    with db.begin():
        entry = _create_entry(db, payload, created_by=payment_ap_data.created_by)
    return _to_entry_out(db, entry)


def record_expense(
    db: Session,
    *,
    expense_data: ExpenseRecordCreate
) -> JournalEntryOut:
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
    with db.begin():
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
