from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from services.auth_service import authenticate_user, create_user, create_auth_token
from schemas.service_user import UserRegister, UserLogin, UserResponse, TokenResponse
from models.database import SessionLocal
from supports.utils_json_response import success_response, error_response

router = APIRouter(prefix="/auth")

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.post("/login", response_model=TokenResponse)
def login(payload: UserLogin, db: Session = Depends(get_db)):
    user = authenticate_user(db, payload.username, payload.password)
    if not user:
        return error_response(message="Invalid username or password", status_code=401)
    token = create_auth_token(user)
    return success_response(data={"access_token": token, "token_type": "bearer"}, message="Login successful")


@router.post("/register", response_model=UserResponse)
def register(payload: UserRegister, db: Session = Depends(get_db)):
    user = create_user(db, payload.username, payload.email, payload.password)
    return success_response(data=UserResponse(
        id=str(user.id),
        username=user.username,
        email=user.email,
    ).dict(), message="User registered successfully")
