"""
Service untuk manage WhatsApp Report tracking.
Mencatat setiap pengiriman WhatsApp ke customer dan vehicle tertentu.
"""
from sqlalchemy.orm import Session
from sqlalchemy import func
from models.whatsapp_report import WhatsappReport
from models.customer import Customer, Vehicle
from schemas.whatsapp_report import (
    WhatsappReportCreate,
    WhatsappReportUpdate,
    WhatsappReportResponse,
    WhatsappReportStatistics,
    WhatsappReportDetail
)
from datetime import datetime
from typing import List, Optional
from uuid import UUID
import logging

logger = logging.getLogger(__name__)


def create_or_update_whatsapp_report(
    db: Session,
    id_customer: UUID,
    id_vehicle: UUID
) -> WhatsappReportResponse:
    """
    Create atau update WhatsApp report saat pesan terkirim.
    Jika sudah ada record untuk customer+vehicle ini, increment frequency dan update date.
    Jika belum ada, buat record baru.
    
    Args:
        db: Database session
        id_customer: UUID customer
        id_vehicle: UUID vehicle
    
    Returns:
        WhatsappReportResponse: Report yang baru dibuat atau diupdate
    """
    try:
        # Cek apakah sudah ada record
        existing_report = db.query(WhatsappReport).filter(
            WhatsappReport.id_customer == id_customer,
            WhatsappReport.id_vehicle == id_vehicle
        ).first()
        
        if existing_report:
            # Update existing report
            existing_report.last_message_date = datetime.now()  # type: ignore
            existing_report.frequency += 1  # type: ignore
            existing_report.updated_at = datetime.now()  # type: ignore
            db.commit()
            db.refresh(existing_report)
            logger.info(f"Updated WhatsApp report for customer {id_customer}, vehicle {id_vehicle}")
            return WhatsappReportResponse.from_orm(existing_report)
        else:
            # Create new report
            new_report = WhatsappReport(
                id_customer=id_customer,
                id_vehicle=id_vehicle,
                last_message_date=datetime.now(),
                frequency=1
            )
            db.add(new_report)
            db.commit()
            db.refresh(new_report)
            logger.info(f"Created new WhatsApp report for customer {id_customer}, vehicle {id_vehicle}")
            return WhatsappReportResponse.from_orm(new_report)
    
    except Exception as e:
        db.rollback()
        logger.error(f"Error creating/updating whatsapp report: {str(e)}")
        raise


def get_all_whatsapp_reports(db: Session) -> List[WhatsappReportResponse]:
    """
    Get semua WhatsApp reports.
    
    Args:
        db: Database session
    
    Returns:
        List[WhatsappReportResponse]: List semua reports
    """
    try:
        reports = db.query(WhatsappReport).all()
        return [WhatsappReportResponse.from_orm(report) for report in reports]
    except Exception as e:
        logger.error(f"Error getting whatsapp reports: {str(e)}")
        raise


def get_whatsapp_report_by_customer_vehicle(
    db: Session,
    id_customer: UUID,
    id_vehicle: UUID
) -> Optional[WhatsappReportResponse]:
    """
    Get report untuk customer dan vehicle tertentu.
    
    Args:
        db: Database session
        id_customer: UUID customer
        id_vehicle: UUID vehicle
    
    Returns:
        WhatsappReportResponse atau None jika tidak ada
    """
    try:
        report = db.query(WhatsappReport).filter(
            WhatsappReport.id_customer == id_customer,
            WhatsappReport.id_vehicle == id_vehicle
        ).first()
        
        if report:
            return WhatsappReportResponse.from_orm(report)
        return None
    except Exception as e:
        logger.error(f"Error getting whatsapp report: {str(e)}")
        raise


def get_whatsapp_reports_by_customer(
    db: Session,
    id_customer: UUID
) -> List[WhatsappReportResponse]:
    """
    Get semua reports untuk customer tertentu.
    
    Args:
        db: Database session
        id_customer: UUID customer
    
    Returns:
        List[WhatsappReportResponse]: List reports untuk customer
    """
    try:
        reports = db.query(WhatsappReport).filter(
            WhatsappReport.id_customer == id_customer
        ).all()
        return [WhatsappReportResponse.from_orm(report) for report in reports]
    except Exception as e:
        logger.error(f"Error getting customer whatsapp reports: {str(e)}")
        raise


def get_whatsapp_report_details(db: Session) -> List[WhatsappReportDetail]:
    """
    Get detail WhatsApp reports dengan informasi customer dan vehicle.
    
    Args:
        db: Database session
    
    Returns:
        List[WhatsappReportDetail]: List reports dengan detail lengkap
    """
    try:
        reports = db.query(
            WhatsappReport.id,
            Customer.nama,
            Customer.hp,
            Vehicle.model,
            Vehicle.no_pol,
            WhatsappReport.last_message_date,
            WhatsappReport.frequency,
            WhatsappReport.created_at,
            WhatsappReport.updated_at
        ).join(
            Customer, WhatsappReport.id_customer == Customer.id
        ).join(
            Vehicle, WhatsappReport.id_vehicle == Vehicle.id
        ).all()
        
        result = []
        for report in reports:
            detail = WhatsappReportDetail(
                id=report.id,
                customer_name=report.nama,
                customer_phone=report.hp,
                vehicle_model=report.model,
                vehicle_nopol=report.no_pol,
                last_message_date=report.last_message_date,
                frequency=report.frequency,
                created_at=report.created_at,
                updated_at=report.updated_at
            )
            result.append(detail)
        
        return result
    except Exception as e:
        logger.error(f"Error getting whatsapp report details: {str(e)}")
        raise


def get_whatsapp_report_statistics(db: Session) -> WhatsappReportStatistics:
    """
    Get statistik WhatsApp reports.
    
    Args:
        db: Database session
    
    Returns:
        WhatsappReportStatistics: Statistik reports
    """
    try:
        # Total customers dengan vehicles yang pernah dikirim pesan
        total_records = db.query(func.count(WhatsappReport.id)).scalar() or 0
        
        # Total pesan yang terkirim
        total_messages = db.query(func.sum(WhatsappReport.frequency)).scalar() or 0
        
        # Average messages per customer
        avg_messages = db.query(func.avg(WhatsappReport.frequency)).scalar() or 0.0
        
        # Group by frequency untuk analisis
        frequency_groups = db.query(
            WhatsappReport.frequency,
            func.count(WhatsappReport.id)
        ).group_by(WhatsappReport.frequency).all()
        
        customers_by_frequency = {str(freq): count for freq, count in frequency_groups}
        
        return WhatsappReportStatistics(
            total_customers_with_vehicles=total_records,
            total_messages_sent=int(total_messages),
            average_messages_per_customer=float(avg_messages),
            customers_by_frequency=customers_by_frequency
        )
    except Exception as e:
        logger.error(f"Error getting whatsapp statistics: {str(e)}")
        raise


def delete_whatsapp_report(db: Session, report_id: UUID) -> bool:
    """
    Delete WhatsApp report.
    
    Args:
        db: Database session
        report_id: UUID report yang akan dihapus
    
    Returns:
        bool: True jika berhasil dihapus
    """
    try:
        report = db.query(WhatsappReport).filter(WhatsappReport.id == report_id).first()
        
        if not report:
            logger.warning(f"Report {report_id} not found")
            return False
        
        db.delete(report)
        db.commit()
        logger.info(f"Deleted WhatsApp report {report_id}")
        return True
    except Exception as e:
        db.rollback()
        logger.error(f"Error deleting whatsapp report: {str(e)}")
        raise


def reset_frequency(db: Session, id_customer: Optional[UUID] = None) -> int:
    """
    Reset frequency untuk semua reports atau untuk customer tertentu.
    Biasanya dijalankan setiap bulan atau periode tertentu.
    
    Args:
        db: Database session
        id_customer: UUID customer (optional, jika None reset semua)
    
    Returns:
        int: Jumlah records yang direset
    """
    try:
        query = db.query(WhatsappReport)
        
        if id_customer:
            query = query.filter(WhatsappReport.id_customer == id_customer)
        
        count = query.update({WhatsappReport.frequency: 0})
        db.commit()
        logger.info(f"Reset frequency for {count} whatsapp reports")
        return count
    except Exception as e:
        db.rollback()
        logger.error(f"Error resetting frequency: {str(e)}")
        raise
