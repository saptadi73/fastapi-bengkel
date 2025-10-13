from sqlalchemy.exc import IntegrityError
from datetime import datetime
from sqlalchemy.orm import Session
from models.expenses import Expenses
from schemas.service_expenses import CreateExpenses, UpdateExpenses
from models.expenses import ExpenseStatus
from supports.utils_json_response import to_dict
from services.services_accounting import create_expense_journal_entry
from schemas.service_accounting import ExpenseJournalEntry
from decimal import Decimal


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

        # Check if status is being changed to 'dibayarkan'
        status_changed_to_paid = data.status and data.status == ExpenseStatus.dibayarkan and exp.status != ExpenseStatus.dibayarkan

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

        # If status changed to 'dibayarkan', create journal entry
        if status_changed_to_paid:
            # Map expense_type to account code (assuming some mapping, e.g., listrik -> 6001, etc.)
            expense_account_map = {
                "listrik": "6001",
                "gaji": "6002",
                "air": "6003",
                "internet": "6004",
                "transportasi": "6005",
                "komunikasi": "6006",
                "konsumsi": "6007",
                "entertaint": "6008",
                "umum": "6009",
                "lain_lain": "6010"
            }
            expense_code = expense_account_map.get(exp.expense_type.value, "6009")  # Default to umum

            journal_data = ExpenseJournalEntry(
                date=exp.date,
                memo=f"Pembayaran biaya {exp.name}",
                expense_id=exp.id,
                amount=exp.amount,
                kas_bank_code="1100",  # Assume kas
                expense_code=expense_code,
                pajak=Decimal("0.00")  # No tax for now
            )
            create_expense_journal_entry(db, journal_data)

        return to_dict(exp)
    except IntegrityError:
        db.rollback()
        return {"message": "Error updating Expenses"}
