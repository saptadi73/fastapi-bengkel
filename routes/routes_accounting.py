from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from models.database import get_db
from schemas.service_accounting import (
    JournalEntryCreate, JournalEntryOut,
    PurchaseRecordCreate, SaleRecordCreate,
    PaymentARCreate, PaymentAPCreate, ExpenseRecordCreate
)
from services.services_accounting import (
    record_purchase, record_sale, receive_payment_ar,
    pay_ap, record_expense, create_account, edit_account, get_account, get_all_accounts
)

from models.accounting import JournalEntry
from schemas.service_accounting import JournalEntryOut, CreateAccount
from sqlalchemy import select
from supports.utils_json_response import success_response, error_response
from middleware.jwt_required import jwt_required

router = APIRouter(prefix="/accounting", tags=["Accounting"])

@router.post("/purchase", response_model=JournalEntryOut, dependencies=[Depends(jwt_required)])
def create_purchase(data: PurchaseRecordCreate, db: Session = Depends(get_db)):
    try:
        result = record_purchase(db, purchase_data=data)
        return success_response(data=result, message="Jurnal pembelian berhasil dibuat")
    except Exception as e:
        return error_response(message=f"Gagal membuat jurnal pembelian: {str(e)}")

@router.post("/sale", response_model=JournalEntryOut, dependencies=[Depends(jwt_required)])
def create_sale(data: SaleRecordCreate, db: Session = Depends(get_db)):
    try:
        result = record_sale(db, sale_data=data)
        return success_response(data=result, message="Jurnal penjualan berhasil dibuat")
    except Exception as e:
        return error_response(message=f"Gagal membuat jurnal penjualan: {str(e)}")

@router.post("/payment-ar", response_model=JournalEntryOut,dependencies=[Depends(jwt_required)])
def create_payment_ar(data: PaymentARCreate, db: Session = Depends(get_db)):
    try:
        result = receive_payment_ar(db, payment_ar_data=data)
        return success_response(data=result, message="Jurnal pembayaran piutang berhasil dibuat")
    except Exception as e:
        return error_response(message=f"Gagal membuat jurnal pembayaran piutang: {str(e)}")

@router.post("/payment-ap", response_model=JournalEntryOut, dependencies=[Depends(jwt_required)])
def create_payment_ap(data: PaymentAPCreate, db: Session = Depends(get_db)):
    try:
        result = pay_ap(db, payment_ap_data=data)
        return success_response(data=result, message="Jurnal pembayaran hutang berhasil dibuat")
    except Exception as e:
        return error_response(message=f"Gagal membuat jurnal pembayaran hutang: {str(e)}")

@router.post("/expense", response_model=JournalEntryOut, dependencies=[Depends(jwt_required)])
def create_expense(data: ExpenseRecordCreate, db: Session = Depends(get_db)):
    try:
        result = record_expense(db, expense_data=data)
        return success_response(data=result, message="Jurnal pengeluaran biaya berhasil dibuat")
    except Exception as e:
        return error_response(message=f"Gagal membuat jurnal pengeluaran biaya: {str(e)}")


# GET list journal entries
@router.get("/journals", response_model=list[JournalEntryOut])
def get_journal_list(db: Session = Depends(get_db), ):
    try:
        # Query all journal entries, order by date desc
        entries = db.execute(select(JournalEntry).order_by(JournalEntry.date.desc())).scalars().all()
        # Convert to JournalEntryOut
        from services.services_accounting import _to_entry_out
        result = [_to_entry_out(db, entry) for entry in entries]
        return success_response(data=result, message="List jurnal berhasil diambil")
    except Exception as e:
        return error_response(message=f"Gagal mengambil list jurnal: {str(e)}")

@router.post("/account/create", dependencies=[Depends(jwt_required)])
def create_account_route(account_data: CreateAccount, db: Session = Depends(get_db)):
    try:
        result = create_account(db, account_data=account_data)
        if not result:
            return error_response(message="Gagal membuat akun")
        return success_response(data=result, message="Akun berhasil dibuat")
    except Exception as e:
        return error_response(message=f"Gagal membuat akun: {str(e)}")
    
@router.post("/account/edit/{account_id}", dependencies=[Depends(jwt_required)])
def edit_account_route(account_id: str, account_data: CreateAccount, db: Session = Depends(get_db)):
    try:
        existing_account = get_account(db, account_id)
        if not existing_account:
            return error_response(message="Akun tidak ditemukan", status_code=404)
        result = edit_account(db, account_id=account_id, account_data=account_data)
        if not result:
            return error_response(message="Gagal mengedit akun")
        return success_response(data=result, message="Akun berhasil diedit")
    except Exception as e:
        return error_response(message=f"Gagal mengedit akun: {str(e)}")
    
@router.get("/account/all")
def get_all_accounts_route(db: Session = Depends(get_db)):
    try:
        result = get_all_accounts(db)
        return success_response(data=result, message="List akun berhasil diambil")
    except Exception as e:
        return error_response(message=f"Gagal mengambil list akun: {str(e)}")