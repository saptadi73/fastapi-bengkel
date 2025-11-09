from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from services.services_role_user import (
    assign_role_to_user,
    remove_role_from_user,
    get_user_with_roles,
    get_roles_for_user,
    get_users_for_role
)
from schemas.service_role_user import AssignRoleToUser, UserWithRolesResponse
from schemas.service_role import RoleResponse
from schemas.service_user import UserResponse
from models.database import SessionLocal
from supports.utils_json_response import success_response, error_response

router = APIRouter(prefix="/role-user", tags=["Role-User Management"])

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("/assign")
def assign_role(assign_data: AssignRoleToUser, user_id: str, db: Session = Depends(get_db)):
    role_user = assign_role_to_user(db, user_id, str(assign_data.role_id))
    if not role_user:
        return error_response(message="Failed to assign role or role already assigned", status_code=400)
    return success_response(message="Role assigned successfully")

@router.delete("/remove")
def remove_role(assign_data: AssignRoleToUser, user_id: str, db: Session = Depends(get_db)):
    role_user = remove_role_from_user(db, user_id, str(assign_data.role_id))
    if not role_user:
        return error_response(message="Role not assigned to user", status_code=404)
    return success_response(message="Role removed successfully")

@router.get("/user/{user_id}/roles", response_model=UserWithRolesResponse)
def get_user_roles(user_id: str, db: Session = Depends(get_db)):
    user_data = get_user_with_roles(db, user_id)
    if not user_data:
        return error_response(message="User not found", status_code=404)
    return success_response(data=user_data, message="User roles retrieved successfully")

@router.get("/role/{role_id}/users")
def get_role_users(role_id: str, db: Session = Depends(get_db)):
    users = get_users_for_role(db, role_id)
    users_data = [{"id": str(user.id), "username": user.username, "email": user.email} for user in users]
    return success_response(data=users_data, message="Role users retrieved successfully")
