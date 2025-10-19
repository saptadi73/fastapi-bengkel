from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from sqlalchemy.orm import Session
import shutil
import os
import json
from typing import Optional
from models.database import SessionLocal
from schemas.service_purchase_order import CreatePurchaseOrder, UpdatePurchaseOrder, UpdatePurchaseOrderLineSingle, CreatePurchaseOrderLineSingle
from services.services_purchase_order import create_purchase_order, get_all_purchase_orders, get_purchase_order_by_id, update_purchase_order, delete_purchase_order, update_purchase_order_status, edit_purchase_order, update_purchase_order_line, add_purchase_order_line, delete_purchase_order_line, update_only_status_purchase_order
from supports.utils_json_response import success_response, error_response
from middleware.jwt_required import jwt_required
from models.purchase_order import PurchaseOrder
from supports.utils_json_response import to_dict

router = APIRouter(prefix="/purchase-orders", tags=["Purchase Order"])

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("/create", dependencies=[Depends(jwt_required)])
def create_purchase_order_router(
    data: str = Form(...),
    bukti_transfer: Optional[UploadFile] = File(None),
    db: Session = Depends(get_db)
):
    try:
        data_dict = json.loads(data)
        create_data = CreatePurchaseOrder(**data_dict)

        if bukti_transfer:
            # Validate file type
            allowed_types = ["image/png", "image/jpeg", "image/jpg", "image/gif", "image/webp", "application/pdf"]
            if bukti_transfer.content_type not in allowed_types:
                raise HTTPException(status_code=400, detail="File type not allowed. Only PNG, JPG, JPEG, GIF, WEBP, and PDF are allowed.")

            # Validate file size (1 MB max)
            max_size = 1024 * 1024  # 1 MB
            bukti_transfer.file.seek(0, 2)  # Seek to end
            file_size = bukti_transfer.file.tell()
            bukti_transfer.file.seek(0)  # Seek back to start
            if file_size > max_size:
                raise HTTPException(status_code=400, detail="File size too large. Maximum size is 1 MB.")

            # Create uploads directory if not exists
            upload_dir = "uploads/bukti_transfer"
            os.makedirs(upload_dir, exist_ok=True)

            # Save file
            file_path = f"{upload_dir}/po_{create_data.supplier_id}_{bukti_transfer.filename}"
            with open(file_path, "wb") as buffer:
                shutil.copyfileobj(bukti_transfer.file, buffer)

            create_data.bukti_transfer = file_path

        result = create_purchase_order(db, create_data)
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

@router.get("/{purchase_order_identifier}")
def get_purchase_order_by_id_router(
    purchase_order_identifier: str,
    db: Session = Depends(get_db)
):
    try:
        result = get_purchase_order_by_id(db, purchase_order_identifier)
        if not result:
            raise HTTPException(status_code=404, detail="Purchase Order not found")
        return success_response(data=result)
    except Exception as e:
        return error_response(message=str(e))

@router.post("/{purchase_order_id}", dependencies=[Depends(jwt_required)])
def edit_purchase_order_router(
    purchase_order_id: str,
    data: str = Form(...),
    bukti_transfer: Optional[UploadFile] = File(None),
    db: Session = Depends(get_db)
):
    try:
        data_dict = json.loads(data)
        # Filter out null values to avoid validation errors for optional fields
        data_dict = {k: v for k, v in data_dict.items() if v is not None}
        update_data = UpdatePurchaseOrder(**data_dict)

        # Handle file upload
        if bukti_transfer:
            # Validate file type
            allowed_types = ["image/png", "image/jpeg", "image/jpg", "image/gif", "image/webp", "application/pdf"]
            if bukti_transfer.content_type not in allowed_types:
                raise HTTPException(status_code=400, detail="File type not allowed. Only PNG, JPG, JPEG, GIF, WEBP, and PDF are allowed.")

            # Validate file size (1 MB max)
            max_size = 1024 * 1024  # 1 MB
            bukti_transfer.file.seek(0, 2)  # Seek to end
            file_size = bukti_transfer.file.tell()
            bukti_transfer.file.seek(0)  # Seek back to start
            if file_size > max_size:
                raise HTTPException(status_code=400, detail="File size too large. Maximum size is 1 MB.")

            # Create uploads directory if not exists
            upload_dir = "uploads/bukti_transfer"
            os.makedirs(upload_dir, exist_ok=True)

            # Delete old file if exists
            po = get_purchase_order_by_id(db, purchase_order_id)
            if po and po.get('bukti_transfer'):
                old_file_path = po['bukti_transfer']
                if os.path.exists(old_file_path):
                    os.remove(old_file_path)

            # Save new file
            file_path = f"{upload_dir}/po_{purchase_order_id}_{bukti_transfer.filename}"
            with open(file_path, "wb") as buffer:
                shutil.copyfileobj(bukti_transfer.file, buffer)

            update_data.bukti_transfer = file_path

        result = edit_purchase_order(db, purchase_order_id, update_data)
        return success_response(data=result)
    except Exception as e:
        return error_response(message=str(e))

@router.post("/{purchase_order_id}/status", dependencies=[Depends(jwt_required)])
def update_purchase_order_status_router(
    purchase_order_id: str,
    status: str = Form(...),
    bukti_transfer: Optional[UploadFile] = File(None),
    db: Session = Depends(get_db)
):
    try:
        # Handle file upload
        bukti_path = None
        if bukti_transfer:
            # Validate file type
            allowed_types = ["image/png", "image/jpeg", "image/jpg", "image/gif", "image/webp", "application/pdf"]
            if bukti_transfer.content_type not in allowed_types:
                raise HTTPException(status_code=400, detail="File type not allowed. Only PNG, JPG, JPEG, GIF, WEBP, and PDF are allowed.")

            # Validate file size (1 MB max)
            max_size = 1024 * 1024  # 1 MB
            bukti_transfer.file.seek(0, 2)  # Seek to end
            file_size = bukti_transfer.file.tell()
            bukti_transfer.file.seek(0)  # Seek back to start
            if file_size > max_size:
                raise HTTPException(status_code=400, detail="File size too large. Maximum size is 1 MB.")

            # Create uploads directory if not exists
            upload_dir = "uploads/bukti_transfer"
            os.makedirs(upload_dir, exist_ok=True)

            # Delete old file if exists
            po = get_purchase_order_by_id(db, purchase_order_id)
            if po and po.get('bukti_transfer'):
                old_file_path = po['bukti_transfer']
                if os.path.exists(old_file_path):
                    os.remove(old_file_path)

            # Save new file
            file_path = f"{upload_dir}/po_{purchase_order_id}_{bukti_transfer.filename}"
            with open(file_path, "wb") as buffer:
                shutil.copyfileobj(bukti_transfer.file, buffer)

            bukti_path = file_path

        result = update_purchase_order_status(db, purchase_order_id, status)
        # If bukti_path, update the bukti_transfer
        if bukti_path:
            po = db.query(PurchaseOrder).filter(PurchaseOrder.id == purchase_order_id).first()
            if po:
                po.bukti_transfer = bukti_path
                db.commit()
                db.refresh(po)
                result = to_dict(po)
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

        # Validate file type
        allowed_types = ["image/png", "image/jpeg", "image/jpg", "image/gif", "image/webp", "application/pdf"]
        if file.content_type not in allowed_types:
            raise HTTPException(status_code=400, detail="File type not allowed. Only PNG, JPG, JPEG, GIF, WEBP, and PDF are allowed.")

        # Validate file size (1 MB max)
        max_size = 1024 * 1024  # 1 MB
        file.file.seek(0, 2)  # Seek to end
        file_size = file.file.tell()
        file.file.seek(0)  # Seek back to start
        if file_size > max_size:
            raise HTTPException(status_code=400, detail="File size too large. Maximum size is 1 MB.")

        # Create uploads directory if not exists
        upload_dir = "uploads/bukti_transfer"
        os.makedirs(upload_dir, exist_ok=True)

        # Delete old file if exists
        if po.get('bukti_transfer'):
            old_file_path = po['bukti_transfer']
            if os.path.exists(old_file_path):
                os.remove(old_file_path)

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

@router.put("/{purchase_order_id}/lines/{line_id}", dependencies=[Depends(jwt_required)])
def update_purchase_order_line_router(
    purchase_order_id: str,
    line_id: str,
    data: UpdatePurchaseOrderLineSingle,
    db: Session = Depends(get_db)
):
    try:
        result = update_purchase_order_line(db, line_id, data)
        return success_response(data=result)
    except Exception as e:
        return error_response(message=str(e))

@router.post("/{purchase_order_id}/lines", dependencies=[Depends(jwt_required)])
def add_purchase_order_line_router(
    purchase_order_id: str,
    data: CreatePurchaseOrderLineSingle,
    db: Session = Depends(get_db)
):
    try:
        result = add_purchase_order_line(db, purchase_order_id, data)
        return success_response(data=result)
    except Exception as e:
        return error_response(message=str(e))

@router.delete("/{purchase_order_id}/lines/{line_id}", dependencies=[Depends(jwt_required)])
def delete_purchase_order_line_router(
    purchase_order_id: str,
    line_id: str,
    db: Session = Depends(get_db)
):
    try:
        result = delete_purchase_order_line(db, line_id)
        return success_response(data=result)
    except Exception as e:
        return error_response(message=str(e))

@router.post("/pay/{purchase_id}", dependencies=[Depends(jwt_required)])
def update_only_status_purchase_order_router(
    purchase_id: str ,
    db: Session = Depends(get_db)
):
    try:
        result = update_only_status_purchase_order(db, purchase_id)
        return success_response(data=result)
    except Exception as e:
        return error_response(message=str(e))
    
    
