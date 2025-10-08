from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.orm import Session
import shutil
import os
from models.database import SessionLocal
from schemas.service_purchase_order import CreatePurchaseOrder, UpdatePurchaseOrder
from services.services_purchase_order import create_purchase_order, get_all_purchase_orders, get_purchase_order_by_id, update_purchase_order, delete_purchase_order
from supports.utils_json_response import success_response, error_response
from middleware.jwt_required import jwt_required

router = APIRouter(prefix="/purchase-orders", tags=["Purchase Order"])

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("/", dependencies=[Depends(jwt_required)])
def create_purchase_order_router(
    data: CreatePurchaseOrder,
    db: Session = Depends(get_db)
):
    try:
        result = create_purchase_order(db, data)
        return success_response(data=result)
    except Exception as e:
        return error_response(message=str(e))

@router.get("/")
def get_all_purchase_orders_router(
    db: Session = Depends(get_db)
):
    try:
        result = get_all_purchase_orders(db)
        return success_response(data=result)
    except Exception as e:
        return error_response(message=str(e))

@router.get("/{purchase_order_id}")
def get_purchase_order_by_id_router(
    purchase_order_id: str,
    db: Session = Depends(get_db)
):
    try:
        result = get_purchase_order_by_id(db, purchase_order_id)
        if not result:
            raise HTTPException(status_code=404, detail="Purchase Order not found")
        return success_response(data=result)
    except Exception as e:
        return error_response(message=str(e))

@router.put("/{purchase_order_id}", dependencies=[Depends(jwt_required)])
def update_purchase_order_router(
    purchase_order_id: str,
    data: UpdatePurchaseOrder,
    db: Session = Depends(get_db)
):
    try:
        result = update_purchase_order(db, purchase_order_id, data)
        return success_response(data=result)
    except Exception as e:
        return error_response(message=str(e))

@router.delete("/{purchase_order_id}", dependencies=[Depends(jwt_required)])
def delete_purchase_order_router(
    purchase_order_id: str,
    db: Session = Depends(get_db)
):
    try:
        result = delete_purchase_order(db, purchase_order_id)
        return success_response(data=result)
    except Exception as e:
        return error_response(message=str(e))

@router.post("/{purchase_order_id}/upload-bukti", dependencies=[Depends(jwt_required)])
def upload_bukti_transfer(
    purchase_order_id: str,
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    try:
        # Check if purchase order exists
        po = get_purchase_order_by_id(db, purchase_order_id)
        if not po:
            raise HTTPException(status_code=404, detail="Purchase Order not found")

        # Create uploads directory if not exists
        upload_dir = "uploads/bukti_transfer"
        os.makedirs(upload_dir, exist_ok=True)

        # Save file
        file_path = f"{upload_dir}/{purchase_order_id}_{file.filename}"
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        # Update bukti_transfer in db
        update_data = UpdatePurchaseOrder(bukti_transfer=file_path)
        update_purchase_order(db, purchase_order_id, update_data)

        return success_response(data={"file_path": file_path})
    except Exception as e:
        return error_response(message=str(e))
