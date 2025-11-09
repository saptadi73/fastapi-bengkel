from models.role_user import RoleUser
from models.user import User
from models.role import Role
from sqlalchemy.orm import Session
from schemas.service_role_user import RoleUserCreate, AssignRoleToUser
from sqlalchemy.exc import IntegrityError

def get_role_user_by_id(db: Session, role_user_id: str):
    return db.query(RoleUser).filter(RoleUser.id == role_user_id).first()

def get_roles_for_user(db: Session, user_id: str):
    user = db.query(User).filter(User.id == user_id).first()
    if user:
        return user.roles
    return []

def get_users_for_role(db: Session, role_id: str):
    role = db.query(Role).filter(Role.id == role_id).first()
    if role:
        return role.users
    return []

def assign_role_to_user(db: Session, user_id: str, role_id: str):
    # Check if user and role exist
    user = db.query(User).filter(User.id == user_id).first()
    role = db.query(Role).filter(Role.id == role_id).first()
    if not user or not role:
        return None

    # Check if association already exists
    existing = db.query(RoleUser).filter(
        RoleUser.user_id == user_id,
        RoleUser.role_id == role_id
    ).first()
    if existing:
        return existing

    # Create new association
    role_user = RoleUser(user_id=user_id, role_id=role_id)
    db.add(role_user)
    try:
        db.commit()
        db.refresh(role_user)
        return role_user
    except IntegrityError:
        db.rollback()
        return None

def remove_role_from_user(db: Session, user_id: str, role_id: str):
    role_user = db.query(RoleUser).filter(
        RoleUser.user_id == user_id,
        RoleUser.role_id == role_id
    ).first()
    if role_user:
        db.delete(role_user)
        db.commit()
    return role_user

def get_user_with_roles(db: Session, user_id: str):
    user = db.query(User).filter(User.id == user_id).first()
    if user:
        roles_data = [{"id": str(role.id), "name": role.name} for role in user.roles]
        return {
            "id": user.id,
            "username": user.username,
            "email": user.email,
            "roles": roles_data
        }
    return None
