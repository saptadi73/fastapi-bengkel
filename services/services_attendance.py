from sqlalchemy.exc import IntegrityError
import datetime
from sqlalchemy.orm import Session
from models.attendance import Attendance
from schemas.service_attendance import CreateAttendance, UpdateAttendance
import uuid
import decimal
import logging

logger = logging.getLogger(__name__)

def to_dict(obj):
    result = {}
    for c in obj.__table__.columns:
        value = getattr(obj, c.name)
        # Konversi UUID ke string
        if isinstance(value, uuid.UUID):
            value = str(value)
        # Konversi Decimal ke float
        elif isinstance(value, decimal.Decimal):
            value = float(value)
        # Konversi datetime/date/time ke isoformat string
        elif isinstance(value, (datetime.datetime, datetime.date, datetime.time)):
            value = value.isoformat()
        # Konversi bytes ke string (opsional, jika ada kolom bytes)
        elif isinstance(value, bytes):
            value = value.decode('utf-8')
        result[c.name] = value
    return result

def create_attendance(db: Session, data: CreateAttendance):
    try:
        attendance = Attendance(
            karyawan_id=data.karyawan_id,
            date=data.date,
            check_in_time=data.check_in_time,
            check_out_time=data.check_out_time,
            status=data.status,
            notes=data.notes
        )
        db.add(attendance)
        db.commit()
        db.refresh(attendance)
        return to_dict(attendance)
    except IntegrityError as e:
        db.rollback()
        logger.error(f"IntegrityError in create_attendance: {str(e)}")
        return {"message": f"IntegrityError: {str(e)}"}
    except Exception as e:
        db.rollback()
        logger.error(f"Unexpected error in create_attendance: {str(e)}")
        return {"message": f"Unexpected error: {str(e)}"}

def get_attendance_by_id(db: Session, attendance_id: str):
    attendance = db.query(Attendance).filter(Attendance.id == attendance_id).first()
    if not attendance:
        return None
    attendance_dict = to_dict(attendance)
    attendance_dict['karyawan_name'] = attendance.karyawan.nama if attendance.karyawan else None
    return attendance_dict

def get_all_attendances(db: Session):
    attendances = db.query(Attendance).all()
    result = []
    for attendance in attendances:
        attendance_dict = to_dict(attendance)
        attendance_dict['karyawan_name'] = attendance.karyawan.nama if attendance.karyawan else None
        result.append(attendance_dict)
    return result

def get_attendances_by_karyawan(db: Session, karyawan_id: str):
    attendances = db.query(Attendance).filter(Attendance.karyawan_id == karyawan_id).all()
    result = []
    for attendance in attendances:
        attendance_dict = to_dict(attendance)
        attendance_dict['karyawan_name'] = attendance.karyawan.nama if attendance.karyawan else None
        result.append(attendance_dict)
    return result

def get_attendances_by_date_range(db: Session, start_date: str, end_date: str):
    start = datetime.datetime.fromisoformat(start_date).date()
    end = datetime.datetime.fromisoformat(end_date).date()
    attendances = db.query(Attendance).filter(Attendance.date.between(start, end)).all()
    result = []
    for attendance in attendances:
        attendance_dict = to_dict(attendance)
        attendance_dict['karyawan_name'] = attendance.karyawan.nama if attendance.karyawan else None
        result.append(attendance_dict)
    return result

def update_attendance(db: Session, attendance_id: str, data: UpdateAttendance):
    try:
        attendance = db.query(Attendance).filter(Attendance.id == attendance_id).first()
        if not attendance:
            return {"message": "Attendance not found"}

        if data.check_in_time is not None:
            attendance.check_in_time = data.check_in_time
        if data.check_out_time is not None:
            attendance.check_out_time = data.check_out_time
        if data.status is not None:
            attendance.status = data.status
        if data.notes is not None:
            attendance.notes = data.notes

        attendance.updated_at = datetime.datetime.now()

        db.commit()
        db.refresh(attendance)
        return to_dict(attendance)
    except IntegrityError as e:
        db.rollback()
        logger.error(f"IntegrityError in update_attendance: {str(e)}")
        return {"message": f"IntegrityError: {str(e)}"}
    except Exception as e:
        db.rollback()
        logger.error(f"Unexpected error in update_attendance: {str(e)}")
        return {"message": f"Unexpected error: {str(e)}"}

def delete_attendance(db: Session, attendance_id: str):
    try:
        attendance = db.query(Attendance).filter(Attendance.id == attendance_id).first()
        if not attendance:
            return {"message": "Attendance not found"}

        db.delete(attendance)
        db.commit()
        return {"message": "Attendance deleted successfully"}
    except IntegrityError as e:
        db.rollback()
        logger.error(f"IntegrityError in delete_attendance: {str(e)}")
        return {"message": f"IntegrityError: {str(e)}"}
    except Exception as e:
        db.rollback()
        logger.error(f"Unexpected error in delete_attendance: {str(e)}")
        return {"message": f"Unexpected error: {str(e)}"}

def check_in(db: Session, karyawan_id: str, date: str = None):
    try:
        if date is None:
            date = datetime.date.today()
        else:
            date = datetime.datetime.fromisoformat(date).date()

        # Check if attendance already exists for today
        existing = db.query(Attendance).filter(
            Attendance.karyawan_id == karyawan_id,
            Attendance.date == date
        ).first()

        if existing:
            if existing.check_in_time:
                return {"message": "Already checked in today"}
            # Update check_in_time
            existing.check_in_time = datetime.datetime.now().time()
            existing.status = 'present'
            existing.updated_at = datetime.datetime.now()
            db.commit()
            db.refresh(existing)
            return to_dict(existing)
        else:
            # Create new attendance record
            attendance = Attendance(
                karyawan_id=karyawan_id,
                date=date,
                check_in_time=datetime.datetime.now().time(),
                status='present'
            )
            db.add(attendance)
            db.commit()
            db.refresh(attendance)
            return to_dict(attendance)
    except IntegrityError as e:
        db.rollback()
        logger.error(f"IntegrityError in check_in: {str(e)}")
        return {"message": f"IntegrityError: {str(e)}"}
    except Exception as e:
        db.rollback()
        logger.error(f"Unexpected error in check_in: {str(e)}")
        return {"message": f"Unexpected error: {str(e)}"}

def check_out(db: Session, karyawan_id: str, date: str = None):
    try:
        if date is None:
            date = datetime.date.today()
        else:
            date = datetime.datetime.fromisoformat(date).date()

        attendance = db.query(Attendance).filter(
            Attendance.karyawan_id == karyawan_id,
            Attendance.date == date
        ).first()

        if not attendance:
            return {"message": "No attendance record found for today"}

        if attendance.check_out_time:
            return {"message": "Already checked out today"}

        attendance.check_out_time = datetime.datetime.now().time()
        attendance.updated_at = datetime.datetime.now()

        db.commit()
        db.refresh(attendance)
        return to_dict(attendance)
    except IntegrityError as e:
        db.rollback()
        logger.error(f"IntegrityError in check_out: {str(e)}")
        return {"message": f"IntegrityError: {str(e)}"}
    except Exception as e:
        db.rollback()
        logger.error(f"Unexpected error in check_out: {str(e)}")
        return {"message": f"Unexpected error: {str(e)}"}
