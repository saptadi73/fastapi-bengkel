from models.role_user import RoleUser
from models.user import User
from models.role import Role
from sqlalchemy.orm import Session
from schemas.service_role_user import RoleUserCreate, AssignRoleToUser
from schemas.service_role import RoleResponse
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

def update_roles_for_user(db: Session, user_id: str, role_ids: list):
    # Check if user exists
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        return None

    # Get current roles
    current_role_ids = {str(role.id) for role in user.roles}

    # Roles to add
    new_role_ids = set(str(rid) for rid in role_ids) - current_role_ids

    # Roles to remove
    roles_to_remove = current_role_ids - set(str(rid) for rid in role_ids)

    # Add new roles
    for role_id in new_role_ids:
        role = db.query(Role).filter(Role.id == role_id).first()
        if role:
            role_user = RoleUser(user_id=user_id, role_id=role_id)
            db.add(role_user)

    # Remove old roles
    for role_id in roles_to_remove:
        role_user = db.query(RoleUser).filter(
            RoleUser.user_id == user_id,
            RoleUser.role_id == role_id
        ).first()
        if role_user:
            db.delete(role_user)

    try:
        db.commit()
        return get_user_with_roles(db, user_id)
    except IntegrityError:
        db.rollback()
        return None

def get_all_roles_list(db: Session):
    roles = db.query(Role).all()
    return [{"id": str(role.id), "name": role.name} for role in roles]

def get_all_users_with_roles(db: Session):
    users = db.query(User).all()
    users_data = []
    for user in users:
        roles_data = [{"id": str(role.id), "name": role.name} for role in user.roles]
        users_data.append({
            "id": str(user.id),
            "username": user.username,
            "email": user.email,
            "is_active": user.is_active,
            "roles": roles_data
        })
    return users_data
