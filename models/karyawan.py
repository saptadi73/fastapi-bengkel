from sqlalchemy import Column, String, ForeignKey,Numeric,Date
from sqlalchemy.orm import relationship
import uuid
from sqlalchemy.dialects.postgresql import UUID
from .database import Base
from sqlalchemy import text

class Karyawan(Base):
    __tablename__ = 'karyawan'
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, unique=True, index=True)
    nama = Column(String, nullable=False)
    hp = Column(String, nullable=False)
    alamat = Column(String, nullable=True)
    email = Column(String, nullable=False, unique=True)
    tanggal_lahir = Column(Date, nullable=True)
    
    created_at = Column(Date, nullable=False, server_default=text('now()'))
    updated_at = Column(Date, nullable=False, server_default=text('now()'))
    
    workorders = relationship('Workorder', back_populates='karyawan')
    attendances = relationship('Attendance', back_populates='karyawan')
