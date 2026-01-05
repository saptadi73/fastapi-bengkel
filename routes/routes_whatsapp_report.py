"""
Route untuk WhatsApp Report tracking.
Endpoint untuk melihat tracking pengiriman WhatsApp ke customer dan vehicle.
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from models.database import SessionLocal
from uuid import UUID
from typing import List
import logging

from services.services_whatsapp_report import (
    get_all_whatsapp_reports,
    get_whatsapp_report_by_customer_vehicle,
    get_whatsapp_reports_by_customer,
    get_whatsapp_report_details,
    get_whatsapp_report_statistics,
    delete_whatsapp_report,
    reset_frequency
)
from schemas.whatsapp_report import (
    WhatsappReportResponse,
    WhatsappReportStatistics,
    WhatsappReportDetail
)

router = APIRouter(
    prefix="/whatsapp-report",
    tags=["WhatsApp Report"]
)

logger = logging.getLogger(__name__)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.get("/", response_model=List[WhatsappReportResponse])
def list_whatsapp_reports(db: Session = Depends(get_db)):
    """
    Get semua WhatsApp reports (format minimal).
    
    Returns:
        List[WhatsappReportResponse]: List semua reports
    """
    try:
        return get_all_whatsapp_reports(db)
    except Exception as e:
        logger.error(f"Error listing whatsapp reports: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/detail", response_model=List[WhatsappReportDetail])
def list_whatsapp_reports_detail(db: Session = Depends(get_db)):
    """
    Get semua WhatsApp reports dengan detail lengkap (customer name, vehicle info, etc).
    
    Returns:
        List[WhatsappReportDetail]: List reports dengan detail lengkap
    """
    try:
        return get_whatsapp_report_details(db)
    except Exception as e:
        logger.error(f"Error listing whatsapp report details: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/statistics", response_model=WhatsappReportStatistics)
def get_statistics(db: Session = Depends(get_db)):
    """
    Get statistik WhatsApp reports.
    Menampilkan:
    - Total customer+vehicle yang pernah dikirim pesan
    - Total pesan yang terkirim
    - Average pesan per customer+vehicle
    - Breakdown by frequency
    
    Returns:
        WhatsappReportStatistics: Statistik reports
    """
    try:
        return get_whatsapp_report_statistics(db)
    except Exception as e:
        logger.error(f"Error getting statistics: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/customer/{id_customer}", response_model=List[WhatsappReportResponse])
def get_customer_reports(
    id_customer: UUID,
    db: Session = Depends(get_db)
):
    """
    Get semua WhatsApp reports untuk customer tertentu.
    
    Args:
        id_customer: UUID customer
    
    Returns:
        List[WhatsappReportResponse]: List reports untuk customer
    """
    try:
        return get_whatsapp_reports_by_customer(db, id_customer)
    except Exception as e:
        logger.error(f"Error getting customer reports: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/customer/{id_customer}/vehicle/{id_vehicle}", response_model=WhatsappReportResponse)
def get_customer_vehicle_report(
    id_customer: UUID,
    id_vehicle: UUID,
    db: Session = Depends(get_db)
):
    """
    Get WhatsApp report untuk customer dan vehicle tertentu.
    
    Args:
        id_customer: UUID customer
        id_vehicle: UUID vehicle
    
    Returns:
        WhatsappReportResponse: Report untuk customer+vehicle
    """
    try:
        report = get_whatsapp_report_by_customer_vehicle(db, id_customer, id_vehicle)
        if not report:
            raise HTTPException(status_code=404, detail="Report tidak ditemukan")
        return report
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting customer vehicle report: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/{report_id}")
def delete_report(
    report_id: UUID,
    db: Session = Depends(get_db)
):
    """
    Delete WhatsApp report.
    
    Args:
        report_id: UUID report yang akan dihapus
    
    Returns:
        dict: Pesan sukses
    """
    try:
        success = delete_whatsapp_report(db, report_id)
        if not success:
            raise HTTPException(status_code=404, detail="Report tidak ditemukan")
        return {"message": "Report berhasil dihapus"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting report: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/reset-frequency")
def reset_frequency_endpoint(
    id_customer: UUID = Query(None),
    db: Session = Depends(get_db)
):
    """
    Reset frequency untuk semua reports atau untuk customer tertentu.
    
    Args:
        id_customer: UUID customer (optional, jika tidak diberikan reset semua)
    
    Returns:
        dict: Jumlah records yang direset
    """
    try:
        count = reset_frequency(db, id_customer)
        message = f"Frequency untuk {count} report"
        if id_customer:
            message += f" customer {id_customer}"
        message += " berhasil direset"
        return {"message": message, "count": count}
    except Exception as e:
        logger.error(f"Error resetting frequency: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
