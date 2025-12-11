from sqlalchemy.exc import IntegrityError
from datetime import datetime
from sqlalchemy.orm import Session
from models.expenses import Expenses
from schemas.service_expenses import CreateExpenses, UpdateExpenses
from models.expenses import ExpenseStatus
from supports.utils_json_response import to_dict
from decimal import Decimal
from services.services_accounting import create_expense_journal_entry
from schemas.service_accounting import ExpenseJournalEntry



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
    # Return expenses ordered by date descending (newest first)
    expenses = db.query(Expenses).order_by(Expenses.date.desc()).all()
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
        if data.name is not None:
            exp.name = data.name  # type: ignore
        if data.description is not None:
            exp.description = data.description  # type: ignore
        if data.expense_type is not None:
            exp.expense_type = data.expense_type  # type: ignore
        if data.status is not None:
            exp.status = data.status  # type: ignore
        if data.amount is not None:
            exp.amount = data.amount  # type: ignore
        if data.date is not None:
            exp.date = data.date  # type: ignore
        if data.bukti_transfer is not None:
            exp.bukti_transfer = data.bukti_transfer  # type: ignore
        exp.updated_at = datetime.now()  # type: ignore

        db.commit()
        db.refresh(exp)

        # If status changed to 'dibayarkan', create journal entry
        if status_changed_to_paid:  # type: ignore
            # Import here to avoid circular import
            from services.services_accounting import create_expense_journal_entry

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
                date=exp.date,  # type: ignore
                memo=f"Pembayaran biaya {exp.name}",
                expense_id=exp.id,  # type: ignore
                amount=exp.amount,  # type: ignore
                kas_bank_code="1100",  # Assume kas
                expense_code=expense_code,
                pajak=Decimal("0.00")  # No tax for now
            )
            create_expense_journal_entry(db, journal_data)

        return to_dict(exp)
    except IntegrityError:
        db.rollback()
        return {"message": "Error updating Expenses"}

def edit_expense_status(db: Session, expense_id: str):
    expenseku = db.query(Expenses).filter(Expenses.id == expense_id).first()
    expenseku.status = 'dibayarkan'  # type: ignore
    db.commit()
    return to_dict(expenseku)

def get_expense_status(db: Session, expense_id: str):
    exp = db.query(Expenses).filter(Expenses.id == expense_id).first()
    if not exp:
        return None
    return {"status": exp.status}

