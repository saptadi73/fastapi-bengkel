from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from services.services_role import get_role_by_id, get_all_roles, create_role, update_role, delete_role
from schemas.service_role import RoleCreate, RoleUpdate, RoleResponse
from models.database import SessionLocal
from supports.utils_json_response import success_response, error_response

router = APIRouter(prefix="/roles", tags=["Roles"])

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.get("/", response_model=list[RoleResponse])
def read_roles(db: Session = Depends(get_db)):
    roles = get_all_roles(db)
    return success_response(data=[RoleResponse.model_validate(role) for role in roles], message="Roles retrieved successfully")

@router.get("/{role_id}", response_model=RoleResponse)
def read_role(role_id: str, db: Session = Depends(get_db)):
    role = get_role_by_id(db, role_id)
    if not role:
        return error_response(message="Role not found", status_code=404)
    return success_response(data=RoleResponse.model_validate(role), message="Role retrieved successfully")

@router.post("/", response_model=RoleResponse)
def create_new_role(role: RoleCreate, db: Session = Depends(get_db)):
    db_role = create_role(db, role)
    return success_response(data=RoleResponse.model_validate(db_role), message="Role created successfully")

@router.put("/{role_id}", response_model=RoleResponse)
def update_existing_role(role_id: str, role_update: RoleUpdate, db: Session = Depends(get_db)):
    db_role = update_role(db, role_id, role_update)
    if not db_role:
        return error_response(message="Role not found", status_code=404)
    return success_response(data=RoleResponse.model_validate(db_role), message="Role updated successfully")

@router.delete("/{role_id}")
def delete_existing_role(role_id: str, db: Session = Depends(get_db)):
    db_role = delete_role(db, role_id)
    if not db_role:
        return error_response(message="Role not found", status_code=404)
    return success_response(message="Role deleted successfully")
