from sqlalchemy import Column, String, ForeignKey, Numeric, DateTime, Date
from sqlalchemy.orm import relationship
import uuid
from sqlalchemy.dialects.postgresql import UUID
from .database import Base

class PacketOrder(Base):
    __tablename__ = 'packet_order'
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, unique=True, index=True)
    name = Column(String, nullable=False)

    product_line_packet_order=relationship('ProductLinePacketOrder', back_populates='packet_order')
    service_line_packet_order = relationship('ServiceLinePacketOrder', back_populates='packet_order')

class ProductLinePacketOrder(Base):
    __tablename__ = 'product_line_packet_order'
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, unique=True, index=True)

    packet_order_id = Column(UUID(as_uuid=True), ForeignKey('packet_order.id'))
    packet_order = relationship('PacketOrder', back_populates='product_line_packet_order')

    quantity = Column(Numeric(10,2), nullable=True)
    price = Column(Numeric(10,2), nullable=True)
    discount = Column(Numeric(10,2), nullable=True)
    subtotal = Column(Numeric(10,2), nullable=True)

    satuan_id = Column(UUID(as_uuid=True), ForeignKey('satuan.id'))
    satuan = relationship('Satuan', back_populates='product_line_packet_order')

    product_id = Column(UUID(as_uuid=True), ForeignKey('product.id'))
    product = relationship('Product', back_populates='product_line_packet_order')

class ServiceLinePacketOrder(Base):
    __tablename__ = 'service_line_packet_order'
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, unique=True, index=True)

    packet_order_id = Column(UUID(as_uuid=True), ForeignKey('packet_order.id'))
    packet_order = relationship('PacketOrder', back_populates='service_line_packet_order')

    quantity = Column(Numeric(10,2), nullable=True)
    price = Column(Numeric(10,2), nullable=True)
    discount = Column(Numeric(10,2), nullable=True)
    subtotal = Column(Numeric(10,2), nullable=True)

    service_id = Column(UUID(as_uuid=True), ForeignKey('service.id'))
    service = relationship('Service', back_populates='service_line_packet_order')
