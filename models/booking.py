from sqlalchemy import Column, String, ForeignKey,Numeric,Date,Time, text
from sqlalchemy.orm import relationship
import uuid
from sqlalchemy.dialects.postgresql import UUID
from .database import Base
from .workorder import Brand

class Booking(Base):
    __tablename__ = 'booking'
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, unique=True, index=True)
    nama = Column(String, nullable=False)
    hp = Column(String, nullable=False)
    model= Column(String, nullable=True)
    type= Column(String, nullable=True)
    no_pol= Column(String, nullable=True)
    warna= Column(String, nullable=True)
    tanggal_booking= Column(Date, nullable=True)
    vehicle_id = Column(UUID(as_uuid=True), nullable=True)
    customer_id = Column(UUID(as_uuid=True), nullable=True)
    jam_booking= Column(Time, nullable=True)
    created_at = Column(Date, nullable=False, server_default=text('now()'))
    updated_at = Column(Date, nullable=False, server_default=text('now()'))