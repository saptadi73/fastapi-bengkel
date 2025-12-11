from models.role import Role
from sqlalchemy.orm import Session
from schemas.service_role import RoleCreate, RoleUpdate

def get_role_by_id(db: Session, role_id: str):
    return db.query(Role).filter(Role.id == role_id).first()

def get_role_by_name(db: Session, name: str):
    return db.query(Role).filter(Role.name == name).first()

def get_all_roles(db: Session):
    return db.query(Role).all()

def create_role(db: Session, role: RoleCreate):
    db_role = Role(name=role.name)
    db.add(db_role)
    db.commit()
    db.refresh(db_role)
    return db_role

def update_role(db: Session, role_id: str, role_update: RoleUpdate):
    db_role = db.query(Role).filter(Role.id == role_id).first()
    if db_role:
        db_role.name = role_update.name # type: ignore
        db.commit()
        db.refresh(db_role)
    return db_role

def delete_role(db: Session, role_id: str):
    db_role = db.query(Role).filter(Role.id == role_id).first()
    if db_role:
        db.delete(db_role)
        db.commit()
    return db_role
