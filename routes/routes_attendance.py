from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from models.database import SessionLocal
from schemas.service_attendance import CreateAttendance, UpdateAttendance
from services.services_attendance import (
    create_attendance, get_attendance_by_id, get_all_attendances,
    get_attendances_by_karyawan, get_attendances_by_date_range,
    update_attendance, delete_attendance, check_in, check_out
)
from supports.utils_json_response import success_response, error_response
from middleware.jwt_required import jwt_required

router = APIRouter(prefix="/attendances", tags=["Attendance"])

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("/create", dependencies=[Depends(jwt_required)])
def create_attendance_router(
    attendance_data: CreateAttendance,
    db: Session = Depends(get_db)
):
    try:
        result = create_attendance(db, attendance_data)
        if "message" in result and "Error" in result["message"]:
            return error_response(message=result["message"])
        return success_response(data=result)
    except Exception as e:
        return error_response(message=str(e))

@router.get("/")
def get_all_attendances_router(
    db: Session = Depends(get_db)
):
    try:
        result = get_all_attendances(db)
        return success_response(data=result)
    except Exception as e:
        return error_response(message=str(e))

@router.get("/{attendance_id}")
def get_attendance_by_id_router(
    attendance_id: str,
    db: Session = Depends(get_db)
):
    try:
        result = get_attendance_by_id(db, attendance_id)
        if not result:
            raise HTTPException(status_code=404, detail="Attendance not found")
        return success_response(data=result)
    except Exception as e:
        return error_response(message=str(e))

@router.get("/karyawan/{karyawan_id}")
def get_attendances_by_karyawan_router(
    karyawan_id: str,
    db: Session = Depends(get_db)
):
    try:
        result = get_attendances_by_karyawan(db, karyawan_id)
        return success_response(data=result)
    except Exception as e:
        return error_response(message=str(e))

@router.get("/date-range/")
def get_attendances_by_date_range_router(
    start_date: str = Query(..., description="Start date in ISO format (YYYY-MM-DD)"),
    end_date: str = Query(..., description="End date in ISO format (YYYY-MM-DD)"),
    db: Session = Depends(get_db)
):
    try:
        result = get_attendances_by_date_range(db, start_date, end_date)
        return success_response(data=result)
    except Exception as e:
        return error_response(message=str(e))

@router.put("/{attendance_id}", dependencies=[Depends(jwt_required)])
def update_attendance_router(
    attendance_id: str,
    attendance_data: UpdateAttendance,
    db: Session = Depends(get_db)
):
    try:
        result = update_attendance(db, attendance_id, attendance_data)
        if "message" in result and "not found" in result["message"]:
            raise HTTPException(status_code=404, detail=result["message"])
        if "message" in result and "Error" in result["message"]:
            return error_response(message=result["message"])
        return success_response(data=result)
    except Exception as e:
        return error_response(message=str(e))

@router.delete("/{attendance_id}", dependencies=[Depends(jwt_required)])
def delete_attendance_router(
    attendance_id: str,
    db: Session = Depends(get_db)
):
    try:
        result = delete_attendance(db, attendance_id)
        if "message" in result and "not found" in result["message"]:
            raise HTTPException(status_code=404, detail=result["message"])
        return success_response(data=result)
    except Exception as e:
        return error_response(message=str(e))

@router.post("/check-in/{karyawan_id}", dependencies=[Depends(jwt_required)])
def check_in_router(
    karyawan_id: str,
    date: str = None,
    db: Session = Depends(get_db)
):
    try:
        result = check_in(db, karyawan_id, date)
        if "message" in result and ("Already checked in" in result["message"] or "Error" in result["message"]):
            return error_response(message=result["message"])
        return success_response(data=result)
    except Exception as e:
        return error_response(message=str(e))

@router.post("/check-out/{karyawan_id}", dependencies=[Depends(jwt_required)])
def check_out_router(
    karyawan_id: str,
    date: str = None,
    db: Session = Depends(get_db)
):
    try:
        result = check_out(db, karyawan_id, date)
        if "message" in result and ("Already checked out" in result["message"] or "No attendance record" in result["message"] or "Error" in result["message"]):
            return error_response(message=result["message"])
        return success_response(data=result)
    except Exception as e:
        return error_response(message=str(e))
