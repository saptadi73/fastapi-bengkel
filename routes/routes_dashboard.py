from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import Optional

from models.database import SessionLocal
from services.services_dashboard import (
    get_dashboard_summary,
    get_workorder_pie,
    get_sales_monthly,
    get_purchase_monthly,
    get_expenses_monthly,
    get_combined_monthly,
)
from supports.utils_json_response import success_response, error_response
from middleware.jwt_required import jwt_required

router = APIRouter(prefix="/dashboard", tags=["Dashboard"])


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.get("/summary", dependencies=[Depends(jwt_required)])
def dashboard_summary(db: Session = Depends(get_db)):
    try:
        data = get_dashboard_summary(db)
        return success_response(data=data)
    except Exception as e:
        return error_response(message=str(e))


@router.get("/workorders-pie", dependencies=[Depends(jwt_required)])
def workorders_pie(db: Session = Depends(get_db)):
    try:
        data = get_workorder_pie(db)
        return success_response(data=data)
    except Exception as e:
        return error_response(message=str(e))


@router.get("/sales-monthly", dependencies=[Depends(jwt_required)])
def sales_monthly(months: Optional[int] = 6, db: Session = Depends(get_db)):
    try:
        months = months or 6
        if months < 1 or months > 24:
            raise HTTPException(status_code=400, detail="months must be between 1 and 24")
        data = get_sales_monthly(db, months=months)
        return success_response(data=data)
    except Exception as e:
        if isinstance(e, HTTPException):
            raise e
        return error_response(message=str(e))


@router.get("/purchase-monthly", dependencies=[Depends(jwt_required)])
def purchase_monthly(months: Optional[int] = 6, db: Session = Depends(get_db)):
    try:
        months = months or 6
        if months < 1 or months > 24:
            raise HTTPException(status_code=400, detail="months must be between 1 and 24")
        data = get_purchase_monthly(db, months=months)
        return success_response(data=data)
    except Exception as e:
        if isinstance(e, HTTPException):
            raise e
        return error_response(message=str(e))


@router.get("/expenses-monthly", dependencies=[Depends(jwt_required)])
def expenses_monthly(months: Optional[int] = 6, db: Session = Depends(get_db)):
    try:
        months = months or 6
        if months < 1 or months > 24:
            raise HTTPException(status_code=400, detail="months must be between 1 and 24")
        data = get_expenses_monthly(db, months=months)
        return success_response(data=data)
    except Exception as e:
        if isinstance(e, HTTPException):
            raise e
        return error_response(message=str(e))


@router.get("/combined-monthly", dependencies=[Depends(jwt_required)])
def combined_monthly(months: Optional[int] = 6, db: Session = Depends(get_db)):
    try:
        months = months or 6
        if months < 1 or months > 24:
            raise HTTPException(status_code=400, detail="months must be between 1 and 24")
        data = get_combined_monthly(db, months=months)
        return success_response(data=data)
    except Exception as e:
        if isinstance(e, HTTPException):
            raise e
        return error_response(message=str(e))
