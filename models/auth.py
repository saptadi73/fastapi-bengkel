from sqlalchemy import Column, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
import uuid
from .database import Base

class Auth(Base):
    __tablename__ = 'auth'
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, unique=True, index=True)
    user_id = Column(UUID(as_uuid=True), nullable=False)
    access_token = Column(String, nullable=False)
    refresh_token = Column(String, nullable=True)
