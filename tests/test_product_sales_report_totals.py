from datetime import date, datetime
from decimal import Decimal
from types import SimpleNamespace

from schemas.service_accounting import ProductSalesReportRequest
from services.services_accounting import generate_product_sales_report


class FluentQuery:
    def __init__(self, rows):
        self.rows = rows

    def join(self, *args):
        return self

    def outerjoin(self, *args):
        return self

    def filter(self, *args):
        return self

    def order_by(self, *args):
        return self

    def all(self):
        return self.rows


def _row(*, number, quantity, price, hpp, subtotal, discount):
    return SimpleNamespace(
        no_wo=number,
        tanggal_masuk=datetime(2026, 7, 12, 10),
        customer_name="Customer",
        product_name="Spare Part",
        no_pol="B 1234 CD",
        quantity=Decimal(quantity),
        price=Decimal(price),
        hpp=None if hpp is None else Decimal(hpp),
        subtotal=Decimal(subtotal),
        discount=Decimal(discount),
    )


def test_product_sales_totals_use_line_subtotal_and_hpp_times_quantity():
    rows = [
        # Subtotals intentionally differ from quantity * price to ensure the
        # backend uses the stored line subtotal as the sales source of truth.
        _row(number="WO-1", quantity="2", price="100", hpp="10", subtotal="175", discount="25"),
        _row(number="WO-2", quantity="3", price="50", hpp="15", subtotal="75", discount="75"),
        _row(number="WO-3", quantity="1", price="20", hpp=None, subtotal="20", discount="0"),
    ]
    db = SimpleNamespace(query=lambda *args: FluentQuery(rows))

    report = generate_product_sales_report(
        db,
        ProductSalesReportRequest(start_date=date(2026, 7, 12), end_date=date(2026, 7, 12)),
    )

    assert report.total_sales == Decimal("270")
    assert report.total_hpp == Decimal("65")
    assert report.total_margin == Decimal("205")
    assert report.total_sales == sum(item.subtotal for item in report.items)
    assert report.total_hpp == sum(
        (item.hpp or Decimal("0")) * item.quantity for item in report.items
    )
