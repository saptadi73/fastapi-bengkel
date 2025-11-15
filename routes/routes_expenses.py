from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from sqlalchemy.orm import Session
import shutil
import os
from models.database import SessionLocal
from schemas.service_expenses import CreateExpenses, UpdateExpenses, ExpenseStatus, ExpenseType
from services.services_expenses import create_expenses, get_all_expenses, get_expenses_by_id, update_expenses, delete_expenses, get_expense_status
from supports.utils_json_response import success_response, error_response
from middleware.jwt_required import jwt_required
from datetime import datetime
from decimal import Decimal

router = APIRouter(prefix="/expenses", tags=["Expenses"])

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("/create", dependencies=[Depends(jwt_required)])
def create_expenses_router(
    name: str = Form(...),
    description: str = Form(...),
    expense_type: str = Form(...),
    status: str = Form('open'),
    amount: float = Form(...),
    date: str = Form(...),
    bukti_transfer: UploadFile = File(None),
    db: Session = Depends(get_db)
):
    print("Start create expenses")
    try:
        bukti_transfer_path = None
        if bukti_transfer:
            print("Processing file")
            # Limit file size max 1MB and only allow image and pdf
            allowed_types = ["image/jpeg", "image/png", "image/gif", "application/pdf"]
            if bukti_transfer.content_type not in allowed_types:
                return error_response(message="File type not allowed. Only images and PDFs are accepted.")
            bukti_transfer.file.seek(0, 2)  # Seek to end of file
            size = bukti_transfer.file.tell()
            bukti_transfer.file.seek(0)  # Reset to start
            if size > 1 * 1024 * 1024:
                return error_response(message="File size exceeds 1MB limit.")
            upload_dir = "uploads/bukti_transfer"
            os.makedirs(upload_dir, exist_ok=True)
            file_path = f"{upload_dir}/{bukti_transfer.filename}"
            with open(file_path, "wb") as buffer:
                shutil.copyfileobj(bukti_transfer.file, buffer)
            bukti_transfer_path = file_path
            print("File processed")

        print("Creating data")
        create_data = CreateExpenses(
            name=name,
            description=description,
            expense_type=ExpenseType(expense_type),
            status=ExpenseStatus(status),
            amount=Decimal(amount),
            date=datetime.fromisoformat(date).date(),
            bukti_transfer=bukti_transfer_path
        )
        print("Calling create_expenses")
        result = create_expenses(db, create_data)
        print("Returning response")
        return success_response(data=result)
    except Exception as e:
        print(f"Error: {e}")
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
    name: str = Form(...),
    description: str = Form(...),
    expense_type: str = Form(...),
    status: str = Form('open'),
    amount: float = Form(...),
    date: str = Form(...),
    bukti_transfer: UploadFile = File(None),
    db: Session = Depends(get_db)
):
    try:
        existing_expense = get_expenses_by_id(db, expenses_id)
        if not existing_expense:
            return error_response(message="Expenses not found")

        bukti_transfer_path = existing_expense.get('bukti_transfer')

        if bukti_transfer:
            # Limit file size max 1MB and only allow image and pdf
            allowed_types = ["image/jpeg", "image/png", "image/gif", "application/pdf"]
            if bukti_transfer.content_type not in allowed_types:
                return error_response(message="File type not allowed. Only images and PDFs are accepted.")
            bukti_transfer.file.seek(0, 2)  # Seek to end of file
            size = bukti_transfer.file.tell()
            bukti_transfer.file.seek(0)  # Reset to start
            if size > 1 * 1024 * 1024:
                return error_response(message="File size exceeds 1MB limit.")
            upload_dir = "uploads/bukti_transfer"
            os.makedirs(upload_dir, exist_ok=True)
            if bukti_transfer_path and os.path.exists(bukti_transfer_path):
                os.remove(bukti_transfer_path)
            file_path = f"{upload_dir}/{bukti_transfer.filename}"
            with open(file_path, "wb") as buffer:
                shutil.copyfileobj(bukti_transfer.file, buffer)
            bukti_transfer_path = file_path

        update_data = UpdateExpenses(
            name=name,
            description=description,
            expense_type=ExpenseType(expense_type),
            status=ExpenseStatus(status),
            amount=Decimal(amount),
            date=datetime.fromisoformat(date).date(),
            bukti_transfer=bukti_transfer_path
        )
        result = update_expenses(db, expenses_id, update_data)
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
        exp = get_expenses_by_id(db, expenses_id)
        if not exp:
            raise HTTPException(status_code=404, detail="Expenses not found")

        upload_dir = "uploads/bukti_transfer"
        os.makedirs(upload_dir, exist_ok=True)

        file_path = f"{upload_dir}/{expenses_id}_{file.filename}"
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        update_data = UpdateExpenses(bukti_transfer=file_path)
        update_expenses(db, expenses_id, update_data)

        return success_response(data={"file_path": file_path})
    except Exception as e:
        return error_response(message=str(e))

@router.get("/{expenses_id}/status")
def get_expense_status_router(
    expenses_id: str,
    db: Session = Depends(get_db)
):
    try:
        result = get_expense_status(db, expenses_id)
        if not result:
            raise HTTPException(status_code=404, detail="Expenses not found")
        return success_response(data=result)
    except Exception as e:
        return error_response(message=str(e))
