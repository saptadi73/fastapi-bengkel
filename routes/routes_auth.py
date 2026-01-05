from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from services.auth_service import authenticate_user, create_user, create_auth_token
from schemas.service_user import UserRegister, UserLogin, UserResponse, TokenResponse
from models.database import SessionLocal
from supports.utils_json_response import success_response, error_response

router = APIRouter(prefix="/auth", tags=["Authentication"])

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.post("/login")
def login(payload: UserLogin, db: Session = Depends(get_db)):
    user = authenticate_user(db, payload.username, payload.password)
    if not user:
        return error_response(message="Invalid username or password", status_code=401)
    token = create_auth_token(user)
    # Get user roles
    roles = [{"id": str(role.id), "name": role.name} for role in user.roles]
    user_data = {
        "id": str(user.id),
        "username": user.username,
        "email": user.email,
        "is_active": user.is_active,
        "roles": roles
    }
    return success_response(data={"access_token": token, "token_type": "bearer", "user": user_data}, message="Login successful")


@router.post("/register")
def register(payload: UserRegister, db: Session = Depends(get_db)):
    user = create_user(db, payload.username, payload.email, payload.password)
    user_response = UserResponse.model_validate(user)
    return success_response(data=user_response.model_dump(), message="User registered successfully")
