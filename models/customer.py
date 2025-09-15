from sqlalchemy import Column, String, ForeignKey,Numeric
from sqlalchemy.orm import relationship
import uuid
from sqlalchemy.dialects.postgresql import UUID
from .database import Base
from .workorder import Brand


class Customer(Base):
    __tablename__ = 'customer'
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, unique=True, index=True)
    nama = Column(String, nullable=False)
    hp = Column(String, nullable=False)
    alamat = Column(String, nullable=False)
    email = Column(String, nullable=False, unique=True)
    vehicles = relationship('Vehicle', back_populates='customer')
    workorders = relationship('Workorder', back_populates='customer')
    

class Vehicle(Base):
    __tablename__ = 'vehicle'
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, unique=True, index=True)
    merk = Column(String, nullable=False)
    model = Column(String, nullable=False)

    brand_id = Column(UUID(as_uuid=True), ForeignKey('brand.id'))
    brand = relationship('Brand', back_populates='vehicles')
    
    type = Column(String, nullable=False)
    kapasitas = Column(String, nullable=False)
    no_pol = Column(String, nullable=False)
    tahun = Column(Numeric, nullable=False)
    warna = Column(String, nullable=False)
    customer_id = Column(UUID(as_uuid=True), ForeignKey('customer.id'))
    customer = relationship('Customer', back_populates='vehicles')
    workorders = relationship('Workorder', back_populates='vehicle')
