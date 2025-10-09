from sqlalchemy import Column, String, DateTime, Date, Numeric, Enum
import uuid
from sqlalchemy.dialects.postgresql import UUID
from .database import Base
from sqlalchemy import text
from enum import Enum as PyEnum

class ExpenseType(PyEnum):
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

class ExpenseStatus(PyEnum):
    open = "open"
    dibayarkan = "dibayarkan"

class Expenses(Base):
    __tablename__ = 'expenses'
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, unique=True, index=True)
    name = Column(String, nullable=False)
    description = Column(String, nullable=False)
    expense_type = Column(Enum(ExpenseType), nullable=False)
    status = Column(Enum(ExpenseStatus), nullable=False, default=ExpenseStatus.open)
    amount = Column(Numeric(10,2), nullable=False)
    date = Column(Date, nullable=False)
    bukti_transfer = Column(String, nullable=True)
    created_at = Column(DateTime, nullable=False, server_default=text('now()'))
    updated_at = Column(DateTime, nullable=False, server_default=text('now()'))
