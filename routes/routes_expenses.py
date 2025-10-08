from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.orm import Session
import shutil
import os
from models.database import SessionLocal
from schemas.service_expenses import CreateExpenses, UpdateExpenses
from services.services_expenses import create_expenses, get_all_expenses, get_expenses_by_id, update_expenses, delete_expenses
from supports.utils_json_response import success_response, error_response
from middleware.jwt_required import jwt_required

router = APIRouter(prefix="/expenses", tags=["Expenses"])

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("/", dependencies=[Depends(jwt_required)])
def create_expenses_router(
    data: CreateExpenses,
    db: Session = Depends(get_db)
):
    try:
        result = create_expenses(db, data)
        return success_response(data=result)
    except Exception as e:
        return error_response(message=str(e))

@router.get("/")
def get_all_expenses_router(
    db: Session = Depends(get_db)
):
    try:
        result = get_all_expenses(db)
        return success_response(data=result)
    except Exception as e:
        return error_response(message=str(e))

@router.get("/{expenses_id}")
def get_expenses_by_id_router(
    expenses_id: str,
    db: Session = Depends(get_db)
):
    try:
        result = get_expenses_by_id(db, expenses_id)
        if not result:
            raise HTTPException(status_code=404, detail="Expenses not found")
        return success_response(data=result)
    except Exception as e:
        return error_response(message=str(e))

@router.put("/{expenses_id}", dependencies=[Depends(jwt_required)])
def update_expenses_router(
    expenses_id: str,
    data: UpdateExpenses,
    db: Session = Depends(get_db)
):
    try:
        result = update_expenses(db, expenses_id, data)
        return success_response(data=result)
    except Exception as e:
        return error_response(message=str(e))

@router.delete("/{expenses_id}", dependencies=[Depends(jwt_required)])
def delete_expenses_router(
    expenses_id: str,
    db: Session = Depends(get_db)
):
    try:
        result = delete_expenses(db, expenses_id)
        return success_response(data=result)
    except Exception as e:
        return error_response(message=str(e))

@router.post("/{expenses_id}/upload-bukti", dependencies=[Depends(jwt_required)])
def upload_bukti_transfer(
    expenses_id: str,
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    try:
        # Check if expenses exists
        exp = get_expenses_by_id(db, expenses_id)
        if not exp:
            raise HTTPException(status_code=404, detail="Expenses not found")

        # Create uploads directory if not exists
        upload_dir = "uploads/bukti_transfer"
        os.makedirs(upload_dir, exist_ok=True)

        # Save file
        file_path = f"{upload_dir}/{expenses_id}_{file.filename}"
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        # Update bukti_transfer in db
        update_data = UpdateExpenses(bukti_transfer=file_path)
        update_expenses(db, expenses_id, update_data)

        return success_response(data={"file_path": file_path})
    except Exception as e:
        return error_response(message=str(e))
