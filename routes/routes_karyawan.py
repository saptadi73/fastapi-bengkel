from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from models.database import SessionLocal
from services.services_karyawan import create_karyawan,get_karyawan, get_all_karyawans
from supports.utils_json_response import success_response, error_response
from middleware.jwt_required import jwt_required
from schemas.service_karyawan import CreateKaryawan

router = APIRouter(prefix="/karyawans")

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("/create", dependencies=[Depends(jwt_required)])
def create_karyawan_router(
    karyawan_data: CreateKaryawan,
    db: Session = Depends(get_db)
):
    try:
        result = create_karyawan(db, karyawan_data)
        if "error" in result:
            return error_response(message=result["message"])
        return success_response(data=result)
    except Exception as e:
        return error_response(message=str(e))

@router.get("/all")
def list_all_karyawans(
    db: Session = Depends(get_db)
):
    try:
        result = get_all_karyawans(db)
        return success_response(data=result)
    except Exception as e:
        return error_response(message=str(e))

@router.get("/{karyawan_id}")
def get_karyawan_router(
    karyawan_id: str,
    db: Session = Depends(get_db)
):
    try:
        if karyawan_id == "all":
            return error_response(message="Use /karyawans/all to get all karyawans")
        result = get_karyawan(db, karyawan_id)
        if not result:
            raise HTTPException(status_code=404, detail="Karyawan not found")
        return success_response(data=result)
    except Exception as e:
        return error_response(message=str(e))
