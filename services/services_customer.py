from sqlalchemy.orm import Session
from models.customer import Customer, Vehicle
import uuid
from schemas.service_customer import CreateCustomerWithVehicles
from fastapi import APIRouter, Depends
from models.database import get_db
from schemas.service_customer import CustomerWithVehicleResponse
import decimal
import datetime

router = APIRouter()

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

def create_customer_with_vehicles(db: Session, customer_data: CreateCustomerWithVehicles):
    # Create a new customer
    new_customer = Customer(
        id=str(uuid.uuid4()),
        nama=customer_data.nama,
        hp=customer_data.hp,
        alamat=customer_data.alamat,
        email=customer_data.email
    )
    db.add(new_customer)
    db.commit()
    db.refresh(new_customer)

    # Create a new vehicle associated with the customer
    new_vehicle = Vehicle(
        id=str(uuid.uuid4()),
        model=customer_data.model,
        brand_id=customer_data.brand_id,
        type=customer_data.type,
        kapasitas=customer_data.kapasitas,
        no_pol=customer_data.no_pol,
        tahun=customer_data.tahun,
        warna=customer_data.warna,
        customer_id=new_customer.id
    )
    db.add(new_vehicle)
    db.commit()
    db.refresh(new_vehicle)

    return {
        "customer": to_dict(new_customer),
        "vehicle": to_dict(new_vehicle)
    }
