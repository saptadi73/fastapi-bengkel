from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from models.database import SessionLocal
from services.services_supplier import create_supplier, update_supplier, delete_supplier, get_supplier, get_all_suppliers
from supports.utils_json_response import success_response, error_response
from middleware.jwt_required import jwt_required
from schemas.service_supplier import CreateSupplier, UpdateSupplier

router = APIRouter(prefix="/suppliers", tags=["Supplier"])

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("/create", dependencies=[Depends(jwt_required)])
def create_supplier_router(
    supplier_data: CreateSupplier,
    db: Session = Depends(get_db)
):
    try:
        result = create_supplier(db, supplier_data)
        return success_response(data=result)
    except Exception as e:
        return error_response(message=str(e))

@router.post("/{supplier_id}", dependencies=[Depends(jwt_required)])
def update_supplier_router(
    supplier_id: str,
    supplier_data: UpdateSupplier,
    db: Session = Depends(get_db)
):
    try:
        result = update_supplier(db, supplier_id, supplier_data)
        return success_response(data=result)
    except Exception as e:
        return error_response(message=str(e))

@router.delete("/{supplier_id}", dependencies=[Depends(jwt_required)])
def delete_supplier_router(
    supplier_id: str,
    db: Session = Depends(get_db)
):
    try:
        result = delete_supplier(db, supplier_id)
        return success_response(data=result)
    except Exception as e:
        return error_response(message=str(e))

@router.get("/all")
def get_all_suppliers_router(
    db: Session = Depends(get_db)
):
    try:
        result = get_all_suppliers(db)
        return success_response(data=result)
    except Exception as e:
        return error_response(message=str(e))

@router.get("/{supplier_id}")
def get_supplier_router(
    supplier_id: str,
    db: Session = Depends(get_db)
):
    try:
        result = get_supplier(db, supplier_id)
        return success_response(data=result)
    except Exception as e:
        return error_response(message=str(e))
