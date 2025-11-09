from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from models.database import get_db
from schemas.service_accounting import (
    JournalEntryCreate, JournalEntryOut,
    PurchaseRecordCreate, SaleRecordCreate,
    SalesWithConsignments,
    PaymentARCreate, PaymentAPCreate, ExpenseRecordCreate, ConsignmentPaymentCreate, SalesJournalEntry, SalesPaymentJournalEntry,PurchaseJournalEntry,PurchasePaymentJournalEntry,ExpenseJournalEntry, ExpensePaymentJournalEntry,
    CashInCreate, CashOutCreate,
    CashBookReportRequest, CashBookReport,
    ExpenseReportRequest, ExpenseReport,
    ProfitLossReportRequest, ProfitLossReport,
    CashReportRequest, CashReport,
    ReceivablePayableReportRequest, ReceivablePayableReport, ConsignmentPayableReport,
    ProductSalesReportRequest, ProductSalesReport,
    ServiceSalesReportRequest, ServiceSalesReport,
    DailyReportRequest, DailyReport,
)
from services.services_accounting import (
    record_purchase, record_sale, receive_payment_ar,
    pay_ap, record_expense, consignment_payment, create_account, edit_account, get_account, get_all_accounts,
    create_sales_journal_entry, create_sales_payment_journal_entry, create_purchase_journal_entry,
    create_purchase_payment_journal_entry, create_expense_journal_entry, create_expense_payment_journal_entry,
    cash_in, cash_out,
    generate_cash_book_report, generate_expense_report, getBankCodes, generate_profit_loss_report, generate_cash_report, getEquityCodes, getTarikCodes, generate_receivable_payable_report, generate_product_sales_report, generate_service_sales_report, generate_daily_report
)
from services.services_accounting import generate_consignment_payable_report

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

@router.post("/sale", response_model=SalesWithConsignments, dependencies=[Depends(jwt_required)])
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

@router.post("/consignment-payment", response_model=JournalEntryOut, dependencies=[Depends(jwt_required)])
def create_consignment_payment(data: ConsignmentPaymentCreate, db: Session = Depends(get_db)):
    try:
        result = consignment_payment(db, payment_data=data)
        return success_response(data=result, message="Jurnal pembayaran hutang konsinyasi berhasil dibuat")
    except Exception as e:
        return error_response(message=f"Gagal membuat jurnal pembayaran hutang konsinyasi: {str(e)}")

@router.post("/sales-journal", response_model=SalesWithConsignments, dependencies=[Depends(jwt_required)])
def create_sales_journal(data: SalesJournalEntry, db: Session = Depends(get_db)):
    try:
        result = create_sales_journal_entry(db, data_entry=data)
        return success_response(data=result, message="Jurnal penjualan berhasil dibuat")
    except Exception as e:
        return error_response(message=f"Gagal membuat jurnal penjualan: {str(e)}")

@router.post("/sales-payment-journal", response_model=JournalEntryOut, dependencies=[Depends(jwt_required)])
def create_sales_payment_journal(data: SalesPaymentJournalEntry, db: Session = Depends(get_db)):
    try:
        result = create_sales_payment_journal_entry(db, data_entry=data)
        return success_response(data=result, message="Jurnal pembayaran penjualan berhasil dibuat")
    except Exception as e:
        return error_response(message=f"Gagal membuat jurnal pembayaran penjualan: {str(e)}")

@router.post("/purchase-journal", response_model=JournalEntryOut, dependencies=[Depends(jwt_required)])
def create_purchase_journal(data: PurchaseJournalEntry, db: Session = Depends(get_db)):
    try:
        result = create_purchase_journal_entry(db, data_entry=data)
        return success_response(data=result, message="Jurnal pembelian berhasil dibuat")
    except Exception as e:
        return error_response(message=f"Gagal membuat jurnal pembelian: {str(e)}")

@router.post("/purchase-payment-journal", response_model=JournalEntryOut, dependencies=[Depends(jwt_required)])
def create_purchase_payment_journal(data: PurchasePaymentJournalEntry, db: Session = Depends(get_db)):
    try:
        result = create_purchase_payment_journal_entry(db, data_entry=data)
        return success_response(data=result, message="Jurnal pembayaran pembelian berhasil dibuat")
    except Exception as e:
        return error_response(message=f"Gagal membuat jurnal pembayaran pembelian: {str(e)}")

@router.post("/expense-journal", response_model=JournalEntryOut, dependencies=[Depends(jwt_required)])
def create_expense_journal(data: ExpenseJournalEntry, db: Session = Depends(get_db)):
    try:
        result = create_expense_journal_entry(db, data_entry=data)
        return success_response(data=result, message="Jurnal pengeluaran biaya berhasil dibuat")
    except Exception as e:
        return error_response(message=f"Gagal membuat jurnal pengeluaran biaya: {str(e)}")

@router.post("/expense-payment-journal", response_model=JournalEntryOut, dependencies=[Depends(jwt_required)])
def create_expense_payment_journal(data: ExpensePaymentJournalEntry, db: Session = Depends(get_db)):
    try:
        result = create_expense_payment_journal_entry(db, data_entry=data)
        return success_response(data=result, message="Jurnal pembayaran biaya berhasil dibuat")
    except Exception as e:
        return error_response(message=f"Gagal membuat jurnal pembayaran biaya: {str(e)}")

@router.post("/cash-in", response_model=JournalEntryOut, dependencies=[Depends(jwt_required)])
def create_cash_in(data: CashInCreate, db: Session = Depends(get_db)):
    try:
        result = cash_in(db, cash_in_data=data)
        return success_response(data=result, message="Jurnal cash in berhasil dibuat")
    except Exception as e:
        return error_response(message=f"Gagal membuat jurnal cash in: {str(e)}")

@router.post("/cash-out", response_model=JournalEntryOut, dependencies=[Depends(jwt_required)])
def create_cash_out(data: CashOutCreate, db: Session = Depends(get_db)):
    try:
        result = cash_out(db, cash_out_data=data)
        return success_response(data=result, message="Jurnal cash out berhasil dibuat")
    except Exception as e:
        return error_response(message=f"Gagal membuat jurnal cash out: {str(e)}")


# GET list journal entries
@router.get("/journals", response_model=List[JournalEntryOut])
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

@router.post("/cash-book-report", response_model=CashBookReport, dependencies=[Depends(jwt_required)])
def generate_cash_book_report_route(request: CashBookReportRequest, db: Session = Depends(get_db)):
    try:
        result = generate_cash_book_report(db, request)
        data = result.model_dump()
        return success_response(data=data, message="Laporan buku kas berhasil dihasilkan")
    except Exception as e:
        return error_response(message=f"Gagal menghasilkan laporan buku kas: {str(e)}")

@router.post("/expense-report", response_model=ExpenseReport, dependencies=[Depends(jwt_required)])
def generate_expense_report_route(request: ExpenseReportRequest, db: Session = Depends(get_db)):
    try:
        result = generate_expense_report(db, request)
        data = result.model_dump()
        return success_response(data=data, message="Laporan biaya berhasil dihasilkan")
    except Exception as e:
        return error_response(message=f"Gagal menghasilkan laporan biaya: {str(e)}")
    
@router.get("/bankcodes")
def getAllBankCodes(db: Session = Depends(get_db)):
    try:
        result = getBankCodes(db)
        return success_response(data=result, message="Daftar Bank Codes telah berhasil didapatkan")
    except Exception as e:
        return error_response(message=f"Gagal dapatkan data Bank Codes karena {str(e)}")

@router.get("/equitycodes")
def getAllEquityCodes(db: Session = Depends(get_db)):
    try:
        result = getEquityCodes(db)
        return success_response(data=result, message="Daftar Equity Codes telah berhasil didapatkan")
    except Exception as e:
        return error_response(message=f"Gagal dapatkan data Equity Codes karena {str(e)}")

@router.get("/tarikcodes")
def getAllTarikCodes(db: Session = Depends(get_db)):
    try:
        result = getTarikCodes(db)
        return success_response(data=result, message="Daftar Equity Codes telah berhasil didapatkan")
    except Exception as e:
        return error_response(message=f"Gagal dapatkan data Equity Codes karena {str(e)}")

@router.post("/profit-loss-report", response_model=ProfitLossReport, dependencies=[Depends(jwt_required)])
def generate_profit_loss_report_route(request: ProfitLossReportRequest, db: Session = Depends(get_db)):
    try:
        result = generate_profit_loss_report(db, request)
        data = result.model_dump()
        return success_response(data=data, message="Laporan laba rugi berhasil dihasilkan")
    except Exception as e:
        return error_response(message=f"Gagal menghasilkan laporan laba rugi: {str(e)}")

@router.post("/cash-report", response_model=CashReport, dependencies=[Depends(jwt_required)])
def generate_cash_report_route(request: CashReportRequest, db: Session = Depends(get_db)):
    try:
        result = generate_cash_report(db, request)
        data = result.model_dump()
        return success_response(data=data, message="Laporan kas berhasil dihasilkan")
    except Exception as e:
        return error_response(message=f"Gagal menghasilkan laporan kas: {str(e)}")

@router.post("/receivable-payable-report", response_model=ReceivablePayableReport)
def generate_receivable_payable_report_route(request: ReceivablePayableReportRequest, db: Session = Depends(get_db)):
    try:
        result = generate_receivable_payable_report(db, request)
        data = result.model_dump()
        return success_response(data=data, message="Laporan piutang hutang berhasil dihasilkan")
    except Exception as e:
        return error_response(message=f"Gagal menghasilkan laporan piutang hutang: {str(e)}")


@router.post("/consignment-payable-report", response_model=ConsignmentPayableReport, dependencies=[Depends(jwt_required)])
def generate_consignment_payable_report_route(request: ReceivablePayableReportRequest, db: Session = Depends(get_db)):
    try:
        result = generate_consignment_payable_report(db, request)
        # result is dict-like; if you prefer Pydantic conversion, do it here
        return success_response(data=result, message="Laporan hutang konsinyasi berhasil dihasilkan")
    except Exception as e:
        return error_response(message=f"Gagal menghasilkan laporan hutang konsinyasi: {str(e)}")

@router.post("/product-sales-report", response_model=ProductSalesReport, dependencies=[Depends(jwt_required)])
def generate_product_sales_report_route(request: ProductSalesReportRequest, db: Session = Depends(get_db)):
    try:
        result = generate_product_sales_report(db, request)
        data = result.model_dump()
        return success_response(data=data, message="Laporan penjualan produk berhasil dihasilkan")
    except Exception as e:
        return error_response(message=f"Gagal menghasilkan laporan penjualan produk: {str(e)}")

@router.post("/service-sales-report", response_model=ServiceSalesReport, dependencies=[Depends(jwt_required)])
def generate_service_sales_report_route(request: ServiceSalesReportRequest, db: Session = Depends(get_db)):
    try:
        result = generate_service_sales_report(db, request)
        data = result.model_dump()
        return success_response(data=data, message="Laporan penjualan jasa berhasil dihasilkan")
    except Exception as e:
        return error_response(message=f"Gagal menghasilkan laporan penjualan jasa: {str(e)}")

@router.post("/daily-report", response_model=DailyReport, dependencies=[Depends(jwt_required)])
def generate_daily_report_route(request: DailyReportRequest, db: Session = Depends(get_db)):
    try:
        result = generate_daily_report(db, request)
        data = result.model_dump()
        return success_response(data=data, message="Laporan harian berhasil dihasilkan")
    except Exception as e:
        return error_response(message=f"Gagal menghasilkan laporan harian: {str(e)}")

