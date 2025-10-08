from sqlalchemy import Column, String, DateTime, Date, Numeric
import uuid
from sqlalchemy.dialects.postgresql import UUID
from .database import Base
from sqlalchemy import text


class Expenses(Base):
    __tablename__ = 'expenses'
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, unique=True, index=True)
    description = Column(String, nullable=False)
    amount = Column(Numeric(10,2), nullable=False)
    date = Column(Date, nullable=False)
    bukti_transfer = Column(String, nullable=True)
    created_at = Column(DateTime, nullable=False, server_default=text('now()'))
    updated_at = Column(DateTime, nullable=False, server_default=text('now()'))
