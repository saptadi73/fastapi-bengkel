from pydantic import BaseModel
from typing import Optional, List
from uuid import UUID

class RoleUserBase(BaseModel):
    user_id: UUID
    role_id: UUID

class RoleUserCreate(RoleUserBase):
    pass

class RoleUserResponse(RoleUserBase):
    id: UUID

    model_config = {
        "from_attributes": True
    }

class AssignRoleToUser(BaseModel):
    role_id: UUID

class UserWithRolesResponse(BaseModel):
    id: UUID
    username: str
    email: str
    roles: List[dict]  # List of role dicts with id and name

    model_config = {
        "from_attributes": True
    }

class UpdateRolesForUser(BaseModel):
    role_ids: List[UUID]
