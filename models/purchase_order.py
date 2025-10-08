from sqlalchemy import Column, String, ForeignKey, Numeric, DateTime, Date, Enum
from sqlalchemy.orm import relationship
import uuid
from sqlalchemy.dialects.postgresql import UUID
from .database import Base
from sqlalchemy import text
from enum import Enum as PyEnum

class PurchaseOrderStatus(PyEnum):
    draft = "draft"
    dijalankan = "dijalankan"
    diterima = "diterima"
    dibayarkan = "dibayarkan"

class PurchaseOrder(Base):
    __tablename__ = 'purchase_order'
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, unique=True, index=True)
    po_no = Column(String, nullable=False, unique=True)
    supplier_id = Column(UUID(as_uuid=True), ForeignKey('supplier.id'))
    supplier = relationship('Supplier', back_populates='purchase_orders')
    date = Column(Date, nullable=False)
    total = Column(Numeric(10,2), nullable=False)
    status = Column(Enum(PurchaseOrderStatus), nullable=False, default=PurchaseOrderStatus.draft)
    bukti_transfer = Column(String, nullable=True)
    created_at = Column(DateTime, nullable=False, server_default=text('now()'))
    updated_at = Column(DateTime, nullable=False, server_default=text('now()'))

    lines = relationship('PurchaseOrderLine', back_populates='purchase_order')

class PurchaseOrderLine(Base):
    __tablename__ = 'purchase_order_line'
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, unique=True, index=True)
    purchase_order_id = Column(UUID(as_uuid=True), ForeignKey('purchase_order.id'))
    purchase_order = relationship('PurchaseOrder', back_populates='lines')

    product_id = Column(UUID(as_uuid=True), ForeignKey('product.id'))
    product = relationship('Product', back_populates='purchase_order_lines')

    quantity = Column(Numeric(10,2), nullable=False)
    price = Column(Numeric(10,2), nullable=False)
    discount = Column(Numeric(10,2), nullable=True, default=0)
    subtotal = Column(Numeric(10,2), nullable=False)
