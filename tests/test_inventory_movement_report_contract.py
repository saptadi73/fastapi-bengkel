from datetime import date, datetime
from decimal import Decimal

import pytest
from pydantic import ValidationError

from schemas.service_inventory import (
    ProductMoveHistoryPagination,
    ProductMoveHistoryReport,
    ProductMoveHistoryReportItem,
    ProductMoveHistoryReportRequest,
    ProductMoveHistorySummary,
)


def test_report_request_validates_range_enums_and_pagination():
    with pytest.raises(ValidationError):
        ProductMoveHistoryReportRequest(start_date=date(2026, 7, 2), end_date=date(2026, 7, 1))
    with pytest.raises(ValidationError):
        ProductMoveHistoryReportRequest(start_date=date(2026, 7, 1), end_date=date(2026, 7, 2), limit=101)
    with pytest.raises(ValidationError):
        ProductMoveHistoryReportRequest(start_date=date(2026, 7, 1), end_date=date(2026, 7, 2), sort_order='random')


def test_stock_card_contract_preserves_structured_references_and_balances():
    item = ProductMoveHistoryReportItem(
        movement_id='move-id', product_id='product-id', product_name='Oli',
        type='income', quantity=Decimal('10'), quantity_in=Decimal('10'),
        quantity_out=Decimal('0'), balance_before=Decimal('5'), balance_after=Decimal('15'),
        purchase_price=Decimal('100000'), price=Decimal('100000'), hpp=Decimal('100000'),
        reference_type='purchase_order', reference_id='po-id', reference_no='PO-001',
        purchase_order_id='po-id', purchase_order_no='PO-001', supplier_id='supplier-id',
        vendor_code='VND-001', vendor_name='Vendor', timestamp=datetime(2026, 7, 1, 10),
        performed_by='admin', notes='received',
    )
    report = ProductMoveHistoryReport(
        summary=ProductMoveHistorySummary(
            opening_balance=Decimal('5'), total_in=Decimal('10'), total_out=Decimal('4'),
            total_adjustment=Decimal('0'), closing_balance=Decimal('11'),
        ),
        total_entries=1, items=[item],
        pagination=ProductMoveHistoryPagination(
            page=1, limit=25, total=1, total_pages=1,
            has_previous=False, has_next=False,
        ),
    )

    assert report.items[0].purchase_order_no == report.items[0].reference_no
    assert report.items[0].balance_after == Decimal('15')
    assert report.summary.closing_balance == (
        report.summary.opening_balance + report.summary.total_in - report.summary.total_out
    )
