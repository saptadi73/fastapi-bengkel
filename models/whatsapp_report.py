from sqlalchemy import Column, String, ForeignKey, Integer, DateTime, Date
from sqlalchemy.orm import relationship
import uuid
from sqlalchemy.dialects.postgresql import UUID
from .database import Base
from datetime import datetime
from sqlalchemy import text


class WhatsappReport(Base):
    __tablename__ = 'whatsapp_report'
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, unique=True, index=True)
    id_customer = Column(UUID(as_uuid=True), ForeignKey('customer.id'), nullable=False, index=True)
    id_vehicle = Column(UUID(as_uuid=True), ForeignKey('vehicle.id'), nullable=False, index=True)
    last_message_date = Column(DateTime, nullable=True)
    frequency = Column(Integer, default=0)  # Berapa kali pesan terkirim
    
    created_at = Column(DateTime, nullable=False, server_default=text('now()'))
    updated_at = Column(DateTime, nullable=False, server_default=text('now()'))
    
    # Relationships
    customer = relationship('Customer', backref='whatsapp_reports')
    vehicle = relationship('Vehicle', backref='whatsapp_reports')
