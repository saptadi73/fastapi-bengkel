from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials
from sqlalchemy.orm import Session, joinedload

from models.database import get_db
from models.user import User
from middleware.jwt import decode_access_token
from middleware.jwt_required import bearer_scheme


def admin_required(
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme),
    db: Session = Depends(get_db),
):
    """Require a valid token belonging to a user with the ``admin`` role."""
    payload = decode_access_token(credentials.credentials)
    if not payload:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid or expired token")

    user_id = payload.get("user_id")
    user = (
        db.query(User)
        .options(joinedload(User.roles))
        .filter(User.id == user_id)
        .first()
        if user_id
        else None
    )
    if not user or not any((role.name or "").strip().lower() == "admin" for role in user.roles):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Admin access required")

    return payload
