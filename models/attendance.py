from sqlalchemy import Column, String, ForeignKey, DateTime, Date, Time, Boolean
from sqlalchemy.orm import relationship
import uuid
from sqlalchemy.dialects.postgresql import UUID
from .database import Base
from sqlalchemy import text

class Attendance(Base):
    __tablename__ = 'attendance'
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, unique=True, index=True)
    karyawan_id = Column(UUID(as_uuid=True), ForeignKey('karyawan.id'), nullable=False)
    date = Column(Date, nullable=False)
    check_in_time = Column(Time, nullable=True)
    check_out_time = Column(Time, nullable=True)
    status = Column(String, nullable=False, default='absent')  # present, absent, late, early_leave
    notes = Column(String, nullable=True)

    created_at = Column(DateTime, nullable=False, server_default=text('now()'))
    updated_at = Column(DateTime, nullable=False, server_default=text('now()'))

    karyawan = relationship('Karyawan', back_populates='attendances')
