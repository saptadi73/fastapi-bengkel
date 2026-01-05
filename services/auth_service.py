from models.user import User
from models.auth import Auth
from sqlalchemy.orm import Session, joinedload
from passlib.context import CryptContext
from middleware.jwt import create_access_token
import hashlib

# Use Argon2 instead of bcrypt - no 72 byte limitation
pwd_context = CryptContext(
    schemes=["argon2"],
    deprecated="auto"
)

def _truncate_password(password: str) -> str:
    """
    No need to truncate with Argon2 - it handles any length.
    But keep it for compatibility.
    """
    return password

def verify_password(plain_password, hashed_password):
    # Truncate/hash plain password to ensure it's <= 72 bytes
    plain_password = _truncate_password(plain_password)
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password):
    # Truncate/hash password to ensure it's <= 72 bytes
    password = _truncate_password(password)
    return pwd_context.hash(password)

def authenticate_user(db: Session, username: str, password: str):
    # Eager load roles relationship
    user = db.query(User).options(joinedload(User.roles)).filter(User.username == username).first()
    if not user or not verify_password(password, user.hashed_password):
        return None
    return user

def create_user(db: Session, username: str, email: str, password: str):
    hashed_password = get_password_hash(password)
    user = User(username=username, email=email, hashed_password=hashed_password)
    db.add(user)
    db.commit()
    db.refresh(user)
    return user

def create_auth_token(user: User):
    token_data = {"user_id": str(user.id), "username": user.username}
    return create_access_token(token_data)
