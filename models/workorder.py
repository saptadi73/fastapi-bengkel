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
    product_line_packet_order = relationship('ProductLinePacketOrder', back_populates='satuan')
    product_ordereds = relationship('ProductOrdered', back_populates='satuan')

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
    price = Column(Numeric(10,2), nullable=True)
    cost = Column(Numeric(10,2), nullable=True)

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
    product_line_packet_order = relationship('ProductLinePacketOrder', back_populates='product')
    purchase_order_lines = relationship('PurchaseOrderLine', back_populates='product')

class Service(Base):
    __tablename__ = 'service'
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, unique=True, index=True)
    name = Column(String, nullable=False)
    description = Column(String, nullable=True)
    price = Column(String, nullable=True)
    cost = Column(Numeric(10,2), nullable=True)
    service_ordereds = relationship('ServiceOrdered', back_populates='service')
    service_line_packet_order = relationship('ServiceLinePacketOrder', back_populates='service')

class ProductOrdered(Base):
    __tablename__ = 'product_ordered'
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, unique=True, index=True)
    quantity = Column(Numeric(10,2), nullable=False)
    subtotal = Column(Numeric(10,2), nullable=False)
    price = Column(Numeric(10,2), nullable=False)
    discount = Column(Numeric(10,2), nullable=True, default=0)

    satuan_id = Column(UUID(as_uuid=True), ForeignKey('satuan.id'))
    satuan = relationship('Satuan', back_populates='product_ordereds')

    product_id = Column(UUID(as_uuid=True), ForeignKey('product.id'))
    product = relationship('Product', back_populates='product_ordereds')

    workorder_id = Column(UUID(as_uuid=True), ForeignKey('workorder.id'))
    workorder = relationship('Workorder', back_populates='product_ordered')

class ServiceOrdered(Base):
    __tablename__ = 'service_ordered'
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, unique=True, index=True)
    quantity = Column(Numeric(10,2), nullable=False)
    subtotal = Column(Numeric(10,2), nullable=False)
    price = Column(Numeric(10,2), nullable=False)
    discount = Column(Numeric(10,2), nullable=True, default=0)

    service_id = Column(UUID(as_uuid=True), ForeignKey('service.id'))
    service = relationship('Service', back_populates='service_ordereds')

    workorder_id = Column(UUID(as_uuid=True), ForeignKey('workorder.id'))
    workorder = relationship('Workorder', back_populates='service_ordered')

class Workorder(Base):
    __tablename__ = 'workorder'
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, unique=True, index=True)
    no_wo = Column(String, nullable=False)
    tanggal_masuk = Column(DateTime, nullable=False)
    tanggal_keluar = Column(DateTime, nullable=True)
    keluhan = Column(String, nullable=False)
    kilometer= Column(Numeric(10,2), nullable=True)
    saran = Column(String, nullable=True)
    status = Column(String, nullable=False)
    total_discount = Column(Numeric(10,2), nullable=True, default=0)
    total_biaya = Column(Numeric(10,2), nullable=False)
    pajak = Column(Numeric(10,2), nullable=True, default=0)
    keterangan=Column(String,nullable=True)
    status_pembayaran=Column(String,nullable=True, default='belum ada pembayaran')

    karyawan_id = Column(UUID(as_uuid=True), ForeignKey('karyawan.id'))
    karyawan = relationship('Karyawan', back_populates='workorders')

    customer_id = Column(UUID(as_uuid=True), ForeignKey('customer.id'))
    customer = relationship('Customer', back_populates='workorders')

    vehicle_id = Column(UUID(as_uuid=True), ForeignKey('vehicle.id'))
    vehicle = relationship('Vehicle', back_populates='workorders')
    
    product_ordered = relationship('ProductOrdered', back_populates='workorder')
    service_ordered = relationship('ServiceOrdered', back_populates='workorder')

    journal_entries = relationship('JournalEntry', back_populates='workorder')

# Agar relationship('Inventory', ...) dapat ditemukan oleh SQLAlchemy

