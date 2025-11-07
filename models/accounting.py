# https://chatgpt.com/share/68e2fcb5-b030-800e-a2f6-7dc01047e10b
# models_accounting.py
import uuid
import enum
import datetime
from decimal import Decimal

from sqlalchemy import (
    Column, String, Date, DateTime, Boolean, Enum, Numeric,
    ForeignKey, CheckConstraint, Index
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship, Mapped, mapped_column

from .database import Base  # sesuaikan path Base kamu


class NormalBalance(str, enum.Enum):
    debit = "debit"
    credit = "credit"


class JournalType(str, enum.Enum):
    purchase = "purchase"                # jurnal pembelian
    sale = "sale"                        # jurnal penjualan
    ar_receipt = "ar_receipt"            # pembayaran piutang
    ap_payment = "ap_payment"            # pembayaran hutang
    consignment = "consignment"          # hutang/komisi konsinyasi (per supplier)
    expense = "expense"                  # pengeluaran biaya-biaya
    general = "general"                  # umum (fallback)


class AccountType(str, enum.Enum):
    asset = "asset"
    liability = "liability"
    equity = "equity"
    revenue = "revenue"
    expense = "expense"
    other = "other"


class Account(Base):
    __tablename__ = "accounts"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    code: Mapped[str] = mapped_column(String(32), unique=True, index=True, nullable=False)
    name: Mapped[str] = mapped_column(String(128), nullable=False)
    normal_balance: Mapped[NormalBalance] = mapped_column(Enum(NormalBalance), nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    account_type: Mapped[AccountType] = mapped_column(Enum(AccountType), nullable=False)

    # contoh: 1100 Kas, 1130 Bank, 1200 Piutang Usaha, 2100 Hutang Usaha, 5000 Beban, 4000 Penjualan, 5100 HPP, 1300 Persediaan

    def __repr__(self) -> str:
        return f"<Account {self.code} {self.name}>"


class JournalEntry(Base):
    __tablename__ = "journal_entries"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    entry_no: Mapped[str] = mapped_column(String(40), index=True, nullable=False)  # nomor bukti/entry
    date: Mapped[datetime.date] = mapped_column(Date, nullable=False)
    memo: Mapped[str] = mapped_column(String(255), nullable=True)
    journal_type: Mapped[JournalType] = mapped_column(Enum(JournalType), nullable=False, default=JournalType.general)

    customer_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), ForeignKey("customer.id"), nullable=True)
    supplier_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), ForeignKey("supplier.id"), nullable=True)
    workorder_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), ForeignKey("workorder.id"), nullable=True)
    purchase_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), ForeignKey("purchase_order.id"), nullable=True)

    customer = relationship("Customer", back_populates="journal_entries")
    supplier = relationship("Supplier", back_populates="journal_entries")
    workorder = relationship("Workorder", back_populates="journal_entries")
    purchase_order = relationship("PurchaseOrder", back_populates="journal_entries")

    created_at: Mapped[datetime.datetime] = mapped_column(DateTime, default=datetime.datetime.utcnow)
    created_by: Mapped[str | None] = mapped_column(String(64), nullable=True)

    lines: Mapped[list["JournalLine"]] = relationship(
        "JournalLine", back_populates="entry", cascade="all, delete-orphan"
    )

    __table_args__ = (
        Index("ix_journal_entries_date_type", "date", "journal_type"),
    )


class JournalLine(Base):
    __tablename__ = "journal_lines"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    entry_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("journal_entries.id", ondelete="CASCADE"), nullable=False)
    account_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("accounts.id"), nullable=False)

    description: Mapped[str | None] = mapped_column(String(255), nullable=True)
    debit: Mapped[Decimal] = mapped_column(Numeric(18, 2), default=Decimal("0.00"), nullable=False)
    credit: Mapped[Decimal] = mapped_column(Numeric(18, 2), default=Decimal("0.00"), nullable=False)

    entry: Mapped["JournalEntry"] = relationship("JournalEntry", back_populates="lines")
    account: Mapped["Account"] = relationship("Account")

    __table_args__ = (
        CheckConstraint("debit >= 0", name="chk_journal_lines_debit_nonneg"),
        CheckConstraint("credit >= 0", name="chk_journal_lines_credit_nonneg"),
        CheckConstraint("(debit = 0 AND credit > 0) OR (credit = 0 AND debit > 0)", name="chk_one_side_positive"),
    )
