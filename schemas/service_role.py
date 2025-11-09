from pydantic import BaseModel
from typing import Optional
from uuid import UUID

class RoleBase(BaseModel):
    name: str

class RoleCreate(RoleBase):
    pass

class RoleUpdate(RoleBase):
    pass

class RoleResponse(RoleBase):
    id: UUID

    model_config = {
        "from_attributes": True
    }
