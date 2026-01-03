"""
Model untuk Manual WhatsApp - untuk customer yang belum terintegrasi dengan sistem customer utama
Menyimpan data customer yang dimasukkan secara manual untuk pengiriman WhatsApp reminder
"""
from sqlalchemy import Column, String, DateTime, Integer, Date
from models.database import Base
import uuid
from datetime import datetime


class ManualWhatsApp(Base):
    __tablename__ = "manual_whatsapp"
    
    # Primary Key
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    
    # Customer Information
    customer_name = Column(String(255), nullable=False, index=True)
    nopol = Column(String(20), nullable=False, unique=True, index=True)
    no_hp = Column(String(20), nullable=False, index=True)
    
    # Service Dates
    last_service = Column(Date, nullable=True)
    next_service = Column(Date, nullable=True, index=True)
    
    # Status & Tracking
    is_active = Column(Integer, default=1, nullable=False)  # 1=active, 0=inactive
    reminder_sent_count = Column(Integer, default=0, nullable=False)  # Track berapa kali reminder sudah dikirim
    last_reminder_sent = Column(DateTime, nullable=True)  # Last time reminder was sent
    
    # Metadata
    notes = Column(String(500), nullable=True)  # Catatan tambahan
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    def __repr__(self):
        return f"<ManualWhatsApp(id={self.id}, customer_name={self.customer_name}, nopol={self.nopol})>"
