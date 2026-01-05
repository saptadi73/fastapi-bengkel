from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List, Dict, Any
from uuid import UUID

class UserRegister(BaseModel):
    username: str
    email: EmailStr
    password: str

class UserLogin(BaseModel):
    username: str
    password: str

class UserResponse(BaseModel):
    id: UUID
    username: str
    email: EmailStr
    is_active: Optional[bool] = None

    model_config = {
        "from_attributes": True
    }

class UserWithRolesResponse(BaseModel):
    id: UUID
    username: str
    email: str
    is_active: Optional[bool] = None
    roles: List[Dict[str, Any]] = []

    model_config = {
        "from_attributes": True
    }

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: Optional[Dict[str, Any]] = None
