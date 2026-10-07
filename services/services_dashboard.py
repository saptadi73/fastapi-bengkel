from datetime import date, datetime
from typing import Dict, List, Union
from decimal import Decimal
from sqlalchemy.orm import Session
from sqlalchemy import func, cast, Date, String, or_

from models.workorder import Workorder
from models.attendance import Attendance
from models.purchase_order import PurchaseOrder, PurchaseOrderStatus
from models.expenses import Expenses
from models.customer import Customer, Vehicle
from models.supplier import Supplier


# Helpers

def _start_month(months: int) -> date:
    today = date.today()
    first_this_month = today.replace(day=1)
    # Walk back (months-1) months to include current month
    month = first_this_month.month - (months - 1)
    year = first_this_month.year
    while month <= 0:
        month += 12
        year -= 1
    return date(year, month, 1)


def _month_label(dt: date) -> str:
    return dt.strftime("%Y-%m")


def _normalize_decimal(value) -> float:
    if value is None:
        return 0.0
    if isinstance(value, Decimal):
        return float(value)
    return float(value)


def _completed_status_filter(query):
    # Treat these as completed keywords (lowercased)
    completed = [
        "selesai",
        "finished",
        "done",
        "complete",
        "completed",
    ]
    return query.filter(func.lower(Workorder.status).in_(completed))


# Public services

def _compact_search_value(value):
    for separator in (" ", "-", "+", "(", ")", "."):
        value = func.replace(value, separator, "")
    return func.lower(value)


def search_dashboard_records(db: Session, kind: str, q: str, page: int = 1, limit: int = 5):
    term = q.strip().lower()
    if not term:
        raise ValueError("Kata pencarian tidak boleh kosong.")

    if kind == "workorders":
        query = (
            db.query(
                Workorder.id, Workorder.no_wo, Workorder.tanggal_masuk,
                Workorder.status, Customer.nama.label("customer_name"),
                Customer.hp, Vehicle.no_pol,
            )
            .outerjoin(Customer, Workorder.customer_id == Customer.id)
            .outerjoin(Vehicle, Workorder.vehicle_id == Vehicle.id)
        )
        filters = [
            func.lower(Workorder.no_wo).contains(term, autoescape=True),
            func.lower(Customer.nama).contains(term, autoescape=True),
            func.lower(Customer.hp).contains(term, autoescape=True),
            func.lower(Vehicle.no_pol).contains(term, autoescape=True),
        ]
        compact_term = term
        for separator in (" ", "-", "+", "(", ")", "."):
            compact_term = compact_term.replace(separator, "")
        if compact_term:
            filters.extend([
                _compact_search_value(Customer.hp).contains(compact_term, autoescape=True),
                _compact_search_value(Vehicle.no_pol).contains(compact_term, autoescape=True),
            ])
        query = query.filter(or_(*filters))
        ordering = (Workorder.tanggal_masuk.desc(), Workorder.id.desc())
    elif kind == "purchase-orders":
        query = (
            db.query(
                PurchaseOrder.id, PurchaseOrder.po_no, PurchaseOrder.date,
                PurchaseOrder.status, PurchaseOrder.total,
                Supplier.nama.label("vendor_name"), Supplier.perusahaan, Supplier.toko,
            )
            .outerjoin(Supplier, PurchaseOrder.supplier_id == Supplier.id)
            .filter(or_(
                func.lower(PurchaseOrder.po_no).contains(term, autoescape=True),
                func.lower(Supplier.nama).contains(term, autoescape=True),
                func.lower(Supplier.perusahaan).contains(term, autoescape=True),
                func.lower(Supplier.toko).contains(term, autoescape=True),
            ))
        )
        ordering = (PurchaseOrder.date.desc(), PurchaseOrder.id.desc())
    elif kind == "expenses":
        query = db.query(
            Expenses.id, Expenses.name, Expenses.description, Expenses.expense_type,
            Expenses.date, Expenses.amount, Expenses.status,
        ).filter(or_(
            func.lower(Expenses.name).contains(term, autoescape=True),
            func.lower(Expenses.description).contains(term, autoescape=True),
            func.lower(cast(Expenses.expense_type, String)).contains(term, autoescape=True),
            func.replace(func.lower(cast(Expenses.expense_type, String)), "_", "-")
            .contains(term.replace("_", "-"), autoescape=True),
        ))
        ordering = (Expenses.date.desc(), Expenses.id.desc())
    else:
        raise ValueError("Jenis pencarian tidak didukung.")

    total = query.count()
    rows = query.order_by(*ordering).offset((page - 1) * limit).limit(limit).all()
    return {
        "items": [dict(row._mapping) for row in rows],
        "pagination": {
            "page": page,
            "limit": limit,
            "total": total,
            "total_pages": (total + limit - 1) // limit,
            "has_previous": page > 1,
            "has_next": page * limit < total,
        },
    }

def get_dashboard_summary(db: Session) -> Dict[str, float]:
    today = date.today()

    workorders_today = (
        db.query(func.count(Workorder.id))
        .filter(cast(Workorder.tanggal_masuk, Date) == today)
        .scalar()
        or 0
    )

    completed_q = _completed_status_filter(db.query(func.count(Workorder.id)))
    workorders_finished = completed_q.scalar() or 0

    total_workorders = db.query(func.count(Workorder.id)).scalar() or 0
    workorders_pending = max(total_workorders - workorders_finished, 0)

    employees_present = (
        db.query(func.count(Attendance.id))
        .filter(Attendance.date == today)
        .filter(func.lower(Attendance.status) == "present")
        .scalar()
        or 0
    )

    return {
        "workorders_today": workorders_today,
        "workorders_finished": workorders_finished,
        "workorders_pending": workorders_pending,
        "employees_present": employees_present,
    }


def get_workorder_pie(db: Session) -> Dict[str, float]:
    completed = _completed_status_filter(db.query(func.count(Workorder.id))).scalar() or 0
    total = db.query(func.count(Workorder.id)).scalar() or 0
    pending = max(total - completed, 0)
    return {
        "completed": completed,
        "pending": pending,
    }


def _monthly_series(db: Session, query, date_column, value_column, months: int) -> List[Dict[str, Union[str, float]]]:
    start = _start_month(months)
    rows = (
        query
        .filter(date_column >= start)
        .group_by(func.date_trunc("month", date_column))
        .with_entities(
            func.date_trunc("month", date_column).label("month"),
            func.sum(value_column).label("total"),
        )
        .order_by("month")
        .all()
    )

    buckets = {_month_label(r.month.date()): _normalize_decimal(r.total) for r in rows}

    # Fill missing months with zero
    series: List[Dict[str, Union[str, float]]] = []
    current = _start_month(months)
    for _ in range(months):
        label = _month_label(current)
        series.append({"month": label, "total": buckets.get(label, 0.0)})
        # advance one month
        if current.month == 12:
            current = date(current.year + 1, 1, 1)
        else:
            current = date(current.year, current.month + 1, 1)
    return series


def get_sales_monthly(db: Session, months: int = 6) -> List[Dict[str, Union[str, float]]]:
    # Sales diambil dari total_biaya workorder yang selesai
    q = _completed_status_filter(db.query(Workorder))
    return _monthly_series(db, q, Workorder.tanggal_masuk, Workorder.total_biaya, months)


def get_purchase_monthly(db: Session, months: int = 6) -> List[Dict[str, Union[str, float]]]:
    allowed_status = [
        PurchaseOrderStatus.dijalankan,
        PurchaseOrderStatus.diterima,
        PurchaseOrderStatus.dibayarkan,
    ]
    q = (
        db.query(PurchaseOrder)
        .filter(PurchaseOrder.status.in_(allowed_status))
    )
    return _monthly_series(db, q, PurchaseOrder.date, PurchaseOrder.total, months)


def get_expenses_monthly(db: Session, months: int = 6) -> List[Dict[str, Union[str, float]]]:
    q = db.query(Expenses)
    return _monthly_series(db, q, Expenses.date, Expenses.amount, months)


def get_combined_monthly(db: Session, months: int = 6) -> List[Dict[str, Union[str, float]]]:
    sales = {item["month"]: item["total"] for item in get_sales_monthly(db, months)}
    purchase = {item["month"]: item["total"] for item in get_purchase_monthly(db, months)}
    expenses = {item["month"]: item["total"] for item in get_expenses_monthly(db, months)}

    labels = list({*sales.keys(), *purchase.keys(), *expenses.keys()})
    labels.sort()

    series: List[Dict[str, Union[str, float]]] = []
    for label in labels:
        series.append({
            "month": label,
            "sales": sales.get(label, 0.0),
            "purchase": purchase.get(label, 0.0),
            "expenses": expenses.get(label, 0.0),
        })
    return series
