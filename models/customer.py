from sqlalchemy import Column, String, ForeignKey,Numeric,Date
from sqlalchemy.orm import relationship
import uuid
from sqlalchemy.dialects.postgresql import UUID
from .database import Base
from .workorder import Brand
from sqlalchemy import text


class Customer(Base):
    __tablename__ = 'customer'
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, unique=True, index=True)
    nama = Column(String, nullable=False)
    hp = Column(String, nullable=False)
    alamat = Column(String, nullable=True)
    email = Column(String, nullable=True, unique=True)
    tanggal_lahir = Column(Date, nullable=True)
    
    created_at = Column(Date, nullable=False, server_default=text('now()'))
    updated_at = Column(Date, nullable=False, server_default=text('now()'))
    vehicles = relationship('Vehicle', back_populates='customer')
    workorders = relationship('Workorder', back_populates='customer')
    journal_entries = relationship('JournalEntry', back_populates='customer')
    

class Vehicle(Base):
    __tablename__ = 'vehicle'
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, unique=True, index=True)
    model = Column(String, nullable=False)

    brand_id = Column(UUID(as_uuid=True), ForeignKey('brand.id'))
    brand = relationship('Brand', back_populates='vehicles')
    
    type = Column(String, nullable=False)
    kapasitas = Column(String, nullable=False)
    no_pol = Column(String, nullable=False)
    tahun = Column(Numeric, nullable=False)
    warna = Column(String, nullable=False)
    no_mesin = Column(String, nullable=True)
    no_rangka = Column(String, nullable=True)
    customer_id = Column(UUID(as_uuid=True), ForeignKey('customer.id'))
    customer = relationship('Customer', back_populates='vehicles')
    workorders = relationship('Workorder', back_populates='vehicle')
