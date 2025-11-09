from sqlalchemy import Column, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from .database import Base

class RoleUser(Base):
    __tablename__ = 'role_user'
    id = Column(UUID(as_uuid=True), primary_key=True, server_default="gen_random_uuid()", unique=True, index=True)
    user_id = Column(UUID(as_uuid=True), ForeignKey('users.id'), nullable=False)
    role_id = Column(UUID(as_uuid=True), ForeignKey('roles.id'), nullable=False)
