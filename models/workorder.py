from sqlalchemy import Column, String, ForeignKey, Numeric, DateTime, Date
from sqlalchemy.orm import relationship
import uuid
from sqlalchemy.dialects.postgresql import UUID
from .database import Base

class Satuan(Base):
    __tablename__ = 'satuan'
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, unique=True, index=True)
    name = Column(String, nullable=False)
    description = Column(String, nullable=True)
    products = relationship('Product', back_populates='satuan')

class Category(Base):
    __tablename__ = 'category'
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, unique=True, index=True)
    name = Column(String, nullable=False)
    description = Column(String, nullable=True)
    products = relationship('Product', back_populates='category')

class Brand(Base):
    __tablename__ = 'brand'
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, unique=True, index=True)
    name = Column(String, nullable=False)
    description = Column(String, nullable=True)
    products = relationship('Product', back_populates='brand')
    vehicles = relationship('Vehicle', back_populates='brand')


class Product(Base):
    __tablename__ = 'product'
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, unique=True, index=True)
    name = Column(String, nullable=False)
    type = Column(String, nullable=False)
    description = Column(String, nullable=True)
    price = Column(Numeric(10,2), nullable=False)
    min_stock = Column(Numeric(10,2), nullable=False)
    

    brand_id = Column(UUID(as_uuid=True),ForeignKey('brand.id'))
    brand = relationship('Brand', back_populates='products')

    satuan_id = Column(UUID(as_uuid=True),ForeignKey('satuan.id'))
    satuan = relationship('Satuan', back_populates='products')

    category_id = Column(UUID(as_uuid=True), ForeignKey('category.id'))
    category = relationship('Category', back_populates='products')

    product_ordereds = relationship('ProductOrdered', back_populates='product')
    inventory = relationship('Inventory', back_populates='product')
    product_moved_history = relationship('ProductMovedHistory', back_populates='product')

class Service(Base):
    __tablename__ = 'service'
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, unique=True, index=True)
    name = Column(String, nullable=False)
    description = Column(String, nullable=True)
    price = Column(String, nullable=False)
    cost = Column(Numeric(10,2), nullable=False)
    service_ordereds = relationship('ServiceOrdered', back_populates='service')

class ProductOrdered(Base):
    __tablename__ = 'product_ordered'
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, unique=True, index=True)
    quantity = Column(Numeric(10,2), nullable=False)
    subtotal = Column(Numeric(10,2), nullable=False)

    product_id = Column(UUID(as_uuid=True), ForeignKey('product.id'))
    product = relationship('Product', back_populates='product_ordereds')

    workorder_id = Column(UUID(as_uuid=True), ForeignKey('workorder.id'))
    workorder = relationship('Workorder', back_populates='product_ordered')

class ServiceOrdered(Base):
    __tablename__ = 'service_ordered'
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, unique=True, index=True)
    quantity = Column(Numeric(10,2), nullable=False)
    subtotal = Column(Numeric(10,2), nullable=False)

    service_id = Column(UUID(as_uuid=True), ForeignKey('service.id'))
    service = relationship('Service', back_populates='service_ordereds')

    workorder_id = Column(UUID(as_uuid=True), ForeignKey('workorder.id'))
    workorder = relationship('Workorder', back_populates='service_ordered')

class Workorder(Base):
    __tablename__ = 'workorder'
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, unique=True, index=True)
    no_wo = Column(String, nullable=False)
    tanggal_masuk = Column(Date, nullable=False)
    tanggal_keluar = Column(Date, nullable=True)
    keluhan = Column(String, nullable=False)
    status = Column(String, nullable=False)
    total_biaya = Column(Numeric(10,2), nullable=False)

    customer_id = Column(UUID(as_uuid=True), ForeignKey('customer.id'))
    customer = relationship('Customer', back_populates='workorders')

    vehicle_id = Column(UUID(as_uuid=True), ForeignKey('vehicle.id'))
    vehicle = relationship('Vehicle', back_populates='workorders')
    
    product_ordered = relationship('ProductOrdered', back_populates='workorder')
    service_ordered = relationship('ServiceOrdered', back_populates='workorder')

class WorkOrderActivityLog(Base):
    __tablename__ = 'workorder_activity_log'
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, unique=True, index=True)
    workorder_id = Column(UUID(as_uuid=True), ForeignKey('workorder.id'))
    action = Column(String, nullable=False)
    timestamp = Column(DateTime, nullable=False)
    performed_by = Column(String, nullable=False)

# Agar relationship('Inventory', ...) dapat ditemukan oleh SQLAlchemy
from models.inventory import Inventory
