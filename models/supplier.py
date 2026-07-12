from sqlalchemy import Column, String, Date
from sqlalchemy.orm import relationship
import uuid
from sqlalchemy.dialects.postgresql import UUID
from .database import Base
from sqlalchemy import text


class Supplier(Base):
    __tablename__ = 'supplier'
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, unique=True, index=True)
    nama = Column(String, nullable=False)
    supplier_code = Column(String(50), nullable=True, unique=True, index=True)
    hp = Column(String, nullable=False)
    alamat = Column(String, nullable=False)
    email = Column(String, nullable=True, unique=True)
    npwp = Column(String, nullable=True)
    perusahaan = Column(String, nullable=True)
    toko = Column(String, nullable=True)
    created_at = Column(Date, nullable=False, server_default=text('now()'))
    updated_at = Column(Date, nullable=False, server_default=text('now()'))
    products = relationship('Product', back_populates='supplier')
    consignment_receipts = relationship('ConsignmentReceipt', back_populates='supplier')
    purchase_orders = relationship('PurchaseOrder', back_populates='supplier')
    journal_entries = relationship('JournalEntry', back_populates='supplier')
