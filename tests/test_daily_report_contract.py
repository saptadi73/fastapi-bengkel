from datetime import date
from decimal import Decimal

from schemas.service_accounting import CashBookEntry, CashBookReport, DailyReport
from services.services_accounting import (
    _build_payment_channels,
    _normalize_payment_status,
    _normalize_workorder_status,
)


def test_payment_channel_and_cashier_account_code_are_reconciled():
    cash_book = CashBookReport(
        account_code="1001",
        account_name="Kas Kasir",
        opening_balance=Decimal("1000"),
        entries=[
            CashBookEntry(
                date=date(2026, 7, 12),
                memo="Penjualan",
                debit=Decimal("500"),
                credit=Decimal("100"),
                balance=Decimal("1400"),
            )
        ],
    )

    channels, cashier = _build_payment_channels([cash_book])

    assert channels[0]["code"] == "CASHIER_CASH"
    assert channels[0]["account_code"] == "1001"
    assert channels[0]["closing_balance"] == Decimal("1400")
    assert cashier["code"] == "CASHIER_CASH"
    assert cashier["account_code"] == channels[0]["account_code"]


def test_daily_report_empty_state_has_required_new_structures():
    fields = DailyReport.model_fields

    assert {"outflows", "payment_channels", "cashier_cash"} <= fields.keys()
    assert {"total_hpp", "gross_profit", "operating_expenses"} <= (
        fields["profit_loss"].annotation.model_fields.keys()
    )
    assert fields["cashier_cash"].annotation().account_code == "1001"


def test_workorder_statuses_are_normalized_to_stable_codes():
    assert _normalize_workorder_status("selesai") == "completed"
    assert _normalize_workorder_status("dibatalkan") == "cancelled"
    assert _normalize_payment_status("dibayarkan") == "paid"
    assert _normalize_payment_status("belum ada pembayaran") == "unpaid"
