from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from services.user_service import get_user_by_id, get_all_users
from schemas.service_user import UserResponse
from models.database import SessionLocal
from supports.utils_json_response import success_response, error_response

router = APIRouter(prefix="/users", tags=["User Management"])

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.get("/")
def get_all_users_list(db: Session = Depends(get_db)):
    """Get all users for frontend dropdown/selection"""
    users = get_all_users(db)
    users_data = [{
        "id": user.id,
        "username": user.username,
        "email": user.email,
        "is_active": user.is_active
    } for user in users]
    return success_response(data=users_data, message="All users retrieved successfully")

@router.get("/{user_id}")
def get_user(user_id: str, db: Session = Depends(get_db)):
    user = get_user_by_id(db, user_id)
    if not user:
        return error_response(message="User not found", status_code=404)
    user_dict = {
        "id": user.id,
        "username": user.username,
        "email": user.email,
        "is_active": user.is_active
    }
    return success_response(data=user_dict, message="User retrieved successfully")
