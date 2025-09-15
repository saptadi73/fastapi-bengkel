from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from services.auth_service import authenticate_user, create_user, create_auth_token
from models.database import SessionLocal
from supports.utils_json_response import success_response, error_response

router = APIRouter(prefix="/auth")

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("/login")
def login(payload: dict, db: Session = Depends(get_db)):
    username = payload.get("username")
    password = payload.get("password")
    user = authenticate_user(db, username, password)
    if not user:
        return error_response(message="Invalid username or password", status_code=401)
    token = create_auth_token(user)
    return success_response(data={"access_token": token, "token_type": "bearer"}, message="Login successful")

@router.post("/register")
def register(payload: dict, db: Session = Depends(get_db)):
    username = payload.get("username")
    email = payload.get("email")
    password = payload.get("password")
    if not username or not email or not password:
        return error_response(message="Missing username, email, or password", status_code=400)
    user = create_user(db, username, email, password)
    return success_response(data={"id": str(user.id), "username": user.username, "email": user.email}, message="User registered successfully")
