"""
Consignment Receipt Model
Tracks when consignment products are received from suppliers
"""

from sqlalchemy import Column, String, ForeignKey, Numeric, DateTime, Date, Boolean
from sqlalchemy.orm import relationship
import uuid
from sqlalchemy.dialects.postgresql import UUID
from models.database import Base

class ConsignmentReceipt(Base):
    __tablename__ = 'consignment_receipt'
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, unique=True, index=True)
    
    # Foreign keys
    product_id = Column(UUID(as_uuid=True), ForeignKey('product.id'), nullable=False)
    supplier_id = Column(UUID(as_uuid=True), ForeignKey('supplier.id'), nullable=False)
    
    # Receipt details
    receipt_number = Column(String, nullable=False, unique=True)  # e.g., CR-2025-001
    receipt_date = Column(Date, nullable=False)
    quantity_received = Column(Numeric(12,2), nullable=False)
    
    # Unit pricing at time of receipt
    unit_price = Column(Numeric(12,2), nullable=True)
    total_value = Column(Numeric(14,2), nullable=True)
    
    # Status tracking
    notes = Column(String, nullable=True)
    received_by = Column(String, nullable=False)  # User who received
    
    # Timestamps
    created_at = Column(DateTime, nullable=False)
    updated_at = Column(DateTime, nullable=True)
    
    # Relationships
    product = relationship('Product', back_populates='consignment_receipts')
    supplier = relationship('Supplier', back_populates='consignment_receipts')
    
    def __repr__(self):
        return f"<ConsignmentReceipt(id={self.id}, receipt_number={self.receipt_number})>"
