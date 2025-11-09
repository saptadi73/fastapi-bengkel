from sqlalchemy import Column, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from .database import Base

class Role(Base):
    __tablename__ = 'roles'
    id = Column(UUID(as_uuid=True), primary_key=True, server_default="gen_random_uuid()", unique=True, index=True)
    name = Column(String, unique=True, nullable=False, index=True)

    # Many-to-many relationship with users
    users = relationship("User", secondary="role_user", back_populates="roles")
