from schemas.service_karyawan import CreateKaryawan
from models.karyawan import Karyawan
from sqlalchemy.exc import IntegrityError
from datetime import datetime
from sqlalchemy.orm import Session
from models.workorder import Product, Brand, Satuan, Category, Service, Workorder, ProductOrdered, ServiceOrdered, WorkOrderActivityLog
import uuid
from models.database import get_db
import decimal
import datetime
from collections.abc import Iterable

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

def create_karyawan(db: Session, karyawan: CreateKaryawan):
    db_karyawan = Karyawan(
        nama=karyawan.nama,
        hp=karyawan.hp,
        alamat=karyawan.alamat,
        email=karyawan.email,
        tanggal_lahir=karyawan.tanggal_lahir,
        created_at=datetime.date.today(),
        updated_at=datetime.date.today()
    )
    db.add(db_karyawan)
    try:
        db.commit()
        db.refresh(db_karyawan)
        return to_dict(db_karyawan)
    except IntegrityError as e:
        db.rollback()
        return {"error": True, "message": str(e)}
    
def get_karyawan(db: Session, karyawan_id: str):
    result = db.query(Karyawan).filter(Karyawan.id == karyawan_id).first()
    return to_dict(result)

def get_all_karyawans(db: Session):
    results = db.query(Karyawan).all()
    return [to_dict(result) for result in results] if isinstance(results, Iterable) else []
