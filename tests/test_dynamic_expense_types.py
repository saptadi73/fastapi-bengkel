from datetime import date, datetime
from decimal import Decimal

from sqlalchemy import create_engine, event
from sqlalchemy.orm import Session

from models.expenses import Expenses, ExpenseStatus
from schemas.service_accounting import ExpenseReportRequest
from schemas.service_expenses import CreateExpenses
from services.services_accounting import generate_expense_report
from services.services_expenses import create_expenses


def test_custom_expense_type_can_be_created_and_reported():
    engine = create_engine("sqlite://")
    event.listen(
        engine,
        "connect",
        lambda connection, _: connection.create_function(
            "now", 0, lambda: datetime.now().isoformat()
        ),
    )
    Expenses.__table__.create(engine)

    with Session(engine) as db:
        created = create_expenses(
            db,
            CreateExpenses(
                name="Belanja operasional",
                description="Belanja supermarket",
                expense_type="  SUPERMARKET  ",
                status=ExpenseStatus.open,
                amount=Decimal("125000"),
                date=date(2026, 10, 14),
            ),
        )

        assert created["expense_type"] == "SUPERMARKET"

        report = generate_expense_report(
            db,
            ExpenseReportRequest(
                start_date=date(2026, 10, 14),
                end_date=date(2026, 10, 14),
            ),
        )

        assert report.total_count == 1
        assert report.items[0].expense_type == "SUPERMARKET"
