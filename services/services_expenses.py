from sqlalchemy.exc import IntegrityError
from datetime import datetime
from sqlalchemy.orm import Session
from models.expenses import Expenses
from schemas.service_expenses import CreateExpenses, UpdateExpenses
from models.expenses import ExpenseStatus
from supports.utils_json_response import to_dict


def create_expenses(db: Session, data: CreateExpenses):
    expenses = Expenses(
        name=data.name,
        description=data.description,
        expense_type=data.expense_type,
        status=data.status,
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
        if data.name:
            exp.name = data.name
        if data.description:
            exp.description = data.description
        if data.expense_type:
            exp.expense_type = data.expense_type
        if data.status:
            exp.status = data.status
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
