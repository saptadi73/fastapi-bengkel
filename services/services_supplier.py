from sqlalchemy.orm import Session
from models.supplier import Supplier
import uuid
from schemas.service_supplier import CreateSupplier, UpdateSupplier, SupplierResponse
import decimal
import datetime

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

def create_supplier(db: Session, supplier_data: CreateSupplier):
    new_supplier = Supplier(
        nama=supplier_data.nama,
        hp=supplier_data.hp,
        alamat=supplier_data.alamat,
        email=supplier_data.email,
        npwp=supplier_data.npwp,
        perusahaan=supplier_data.perusahaan,
        toko=supplier_data.toko
    )
    db.add(new_supplier)
    db.commit()
    db.refresh(new_supplier)
    return to_dict(new_supplier)

def update_supplier(db: Session, supplier_id: str, supplier_data: UpdateSupplier):
    supplier = db.query(Supplier).filter(Supplier.id == supplier_id).first()
    if not supplier:
        raise ValueError(f"Supplier with id '{supplier_id}' not found")

    for field, value in supplier_data.model_dump(exclude_unset=True).items():
        setattr(supplier, field, value)

    supplier.updated_at = datetime.datetime.now()
    db.commit()
    db.refresh(supplier)
    return to_dict(supplier)

def delete_supplier(db: Session, supplier_id: str):
    supplier = db.query(Supplier).filter(Supplier.id == supplier_id).first()
    if not supplier:
        raise ValueError(f"Supplier with id '{supplier_id}' not found")

    db.delete(supplier)
    db.commit()
    return {"message": "Supplier deleted successfully"}

def get_supplier(db: Session, supplier_id: str):
    supplier = db.query(Supplier).filter(Supplier.id == supplier_id).first()
    if not supplier:
        raise ValueError(f"Supplier with id '{supplier_id}' not found")
    return to_dict(supplier)

def get_all_suppliers(db: Session):
    suppliers = db.query(Supplier).all()
    return [to_dict(supplier) for supplier in suppliers]
