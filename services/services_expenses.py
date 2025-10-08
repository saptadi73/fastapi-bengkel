from sqlalchemy.exc import IntegrityError
from datetime import datetime
from sqlalchemy.orm import Session
from models.expenses import Expenses
import uuid
from schemas.service_expenses import CreateExpenses, UpdateExpenses
import decimal
from decimal import Decimal


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


def create_expenses(db: Session, data: CreateExpenses):
    expenses = Expenses(
        description=data.description,
        amount=data.amount,
        date=data.date,
        bukti_transfer=data.bukti_transfer
    )
    db.add(expenses)
    db.commit()
    db.refresh(expenses)
    return to_dict(expenses)


def get_all_expenses(db: Session):
    expenses = db.query(Expenses).all()
    result = []
    for exp in expenses:
        result.append(to_dict(exp))
    return result


def get_expenses_by_id(db: Session, expenses_id: str):
    exp = db.query(Expenses).filter(Expenses.id == expenses_id).first()
    if not exp:
        return None
    return to_dict(exp)


def delete_expenses(db: Session, expenses_id: str):
    try:
        exp = db.query(Expenses).filter(Expenses.id == expenses_id).first()
        if not exp:
            return {"message": "Expenses not found"}

        db.delete(exp)
        db.commit()
        return {"message": "Expenses deleted successfully"}
    except IntegrityError:
        db.rollback()
        return {"message": "Error deleting Expenses"}


def update_expenses(db: Session, expenses_id: str, data: UpdateExpenses):
    try:
        exp = db.query(Expenses).filter(Expenses.id == expenses_id).first()
        if not exp:
            return {"message": "Expenses not found"}

        # Update fields
        if data.description:
            exp.description = data.description
        if data.amount:
            exp.amount = data.amount
        if data.date:
            exp.date = data.date
        if data.bukti_transfer:
            exp.bukti_transfer = data.bukti_transfer
        exp.updated_at = datetime.datetime.now()

        db.commit()
        db.refresh(exp)
        return to_dict(exp)
    except IntegrityError:
        db.rollback()
        return {"message": "Error updating Expenses"}
