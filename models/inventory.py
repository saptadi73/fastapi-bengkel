from sqlalchemy import Column, String, ForeignKey, Numeric, DateTime, Date
from sqlalchemy.orm import relationship
import uuid
from sqlalchemy.dialects.postgresql import UUID
from .database import Base

class Inventory(Base):
    __tablename__ = 'inventory'
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, unique=True, index=True)

    product_id = Column(UUID(as_uuid=True), ForeignKey('product.id'))
    product = relationship('Product', back_populates='inventory')

    quantity = Column(Numeric(10,2), nullable=False)

    created_at = Column(DateTime, nullable=False)
    updated_at = Column(DateTime, nullable=True)

class ProductMovedHistory(Base):
    __tablename__ = 'product_moved_history'
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, unique=True, index=True)
    product_id = Column(UUID(as_uuid=True), ForeignKey('product.id'))
    product = relationship('Product', back_populates='product_moved_history')

    type = Column(String, nullable=False)  # e.g., 'added', 'removed', 'updated'
    quantity = Column(Numeric(10,2), nullable=False)
    timestamp = Column(DateTime, nullable=False)
    performed_by = Column(String, nullable=False)  # User who performed the action
    notes = Column(String, nullable=True)