from sqlalchemy.orm import Session
from models.customer import Customer, Vehicle
import uuid
from models.booking import Booking
from schemas.service_booking import CreateBooking
from schemas.service_customer import CreateCustomerWithVehicles
from models.database import get_db
from schemas.service_customer import CustomerWithVehicleResponse, CreateCustomer, CreateVehicle
from schemas.service_vehicle import VehicleResponse, CreateVehicle
import decimal
import datetime
from dateutil.relativedelta import relativedelta

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

def createBookingnya(db: Session, booking_data: CreateBooking):
    # Create a new booking
    new_booking = Booking(
        id=str(uuid.uuid4()),
        nama=booking_data.nama,
        hp=booking_data.hp,
        model=booking_data.model,
        type=booking_data.type,
        no_pol=booking_data.no_pol,
        warna=booking_data.warna,
        tanggal_booking=booking_data.tanggal_booking,
        jam_booking=booking_data.jam_booking,
        customer_id=booking_data.customer_id,
        vehicle_id=booking_data.vehicle_id
    )
    db.add(new_booking)
    db.commit()
    db.refresh(new_booking)

    return to_dict(new_booking)

def get_all_bookings(db: Session):
    bookings = db.query(Booking).all()
    result = []
    for booking in bookings:
        b_dict = to_dict(booking)
        result.append(b_dict)
    return result

def get_booking_by_id(db: Session, booking_id: str):
    booking = db.query(Booking).filter(Booking.id == booking_id).first()
    if booking:
        return to_dict(booking)
    return None