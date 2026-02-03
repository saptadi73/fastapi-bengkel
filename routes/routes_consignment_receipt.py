"""
Routes untuk Consignment Receipt Management
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from datetime import date
from decimal import Decimal
from typing import Any, Optional, cast
from uuid import UUID
from models.database import get_db
from schemas.consignment_receipt import (
    ConsignmentReceiptCreate, 
    ConsignmentReceiptUpdate,
    ConsignmentReceiptResponse,
    ConsignmentReceiptListResponse
)
from services.services_consignment_receipt import (
    create_consignment_receipt,
    get_consignment_receipt,
    get_all_consignment_receipts,
    get_consignment_receipts_by_supplier,
    update_consignment_receipt,
    delete_consignment_receipt,
    get_consignment_receipts_by_date_range,
    get_consignment_receipt_summary
)
from middleware.jwt_required import jwt_required
from supports.utils_json_response import success_response, error_response

router = APIRouter(
    prefix="/inventory/consignment-receipt",
    tags=["Consignment Receipt Management"]
)

def to_float(value: Any) -> float:
    return float(cast(Decimal, value))

@router.post("/create", response_model=dict, dependencies=[Depends(jwt_required)])
def create_receipt(
    request: ConsignmentReceiptCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(jwt_required)
):
    """
    Create a new consignment receipt record
    
    **Required fields:**
    - product_id: UUID of consignment product
    - supplier_id: UUID of supplier
    - receipt_number: Unique receipt number (e.g., CR-2025-001)
    - receipt_date: Date of receipt
    - quantity_received: Quantity received
    - received_by: User who received the goods
    
    **Optional fields:**
    - unit_price: Price per unit at time of receipt
    - total_value: Total value of receipt
    - notes: Additional notes
    """
    try:
        username = current_user.get("username", "system") if current_user else "system"
        result = create_consignment_receipt(db, request, username)
        return success_response(
            data={
                "id": str(result.id),
                "receipt_number": result.receipt_number,
                "receipt_date": result.receipt_date.isoformat(),
                "quantity_received": to_float(result.quantity_received),
                "total_value": to_float(result.total_value) if result.total_value is not None else None,
                "created_at": result.created_at.isoformat()
            },
            message="Consignment receipt created successfully"
        )
    except ValueError as e:
        return error_response(message=str(e), status_code=400)
    except Exception as e:
        return error_response(message=f"Failed to create receipt: {str(e)}", status_code=500)

@router.get("/{receipt_id}", response_model=dict)
def get_receipt(
    receipt_id: UUID,
    db: Session = Depends(get_db)
):
    """
    Get a single consignment receipt by ID
    """
    try:
        receipt = get_consignment_receipt(db, receipt_id)
        return success_response(
            data={
                "id": str(receipt.id),
                "receipt_number": receipt.receipt_number,
                "receipt_date": receipt.receipt_date.isoformat(),
                "product_id": str(receipt.product_id),
                "supplier_id": str(receipt.supplier_id),
                "quantity_received": to_float(receipt.quantity_received),
                "unit_price": to_float(receipt.unit_price) if receipt.unit_price is not None else None,
                "total_value": to_float(receipt.total_value) if receipt.total_value is not None else None,
                "notes": receipt.notes,
                "received_by": receipt.received_by,
                "created_at": receipt.created_at.isoformat(),
                "updated_at": receipt.updated_at.isoformat() if receipt.updated_at is not None else None
            }
        )
    except ValueError as e:
        return error_response(message=str(e), status_code=404)
    except Exception as e:
        return error_response(message=f"Failed to fetch receipt: {str(e)}", status_code=500)

@router.get("", response_model=dict)
def list_receipts(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """
    List all consignment receipts with pagination
    
    **Query parameters:**
    - skip: Number of records to skip (default: 0)
    - limit: Number of records to return (default: 100)
    """
    try:
        receipts = get_all_consignment_receipts(db, skip, limit)
        return success_response(
            data=receipts,
            message=f"Retrieved {len(receipts)} consignment receipts"
        )
    except Exception as e:
        return error_response(message=f"Failed to fetch receipts: {str(e)}", status_code=500)

@router.get("/supplier/{supplier_id}", response_model=dict)
def list_receipts_by_supplier(
    supplier_id: UUID,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """
    Get all consignment receipts for a specific supplier
    
    **Path parameters:**
    - supplier_id: UUID of the supplier
    
    **Query parameters:**
    - skip: Number of records to skip (default: 0)
    - limit: Number of records to return (default: 100)
    """
    try:
        receipts = get_consignment_receipts_by_supplier(db, supplier_id, skip, limit)
        return success_response(
            data=receipts,
            message=f"Retrieved {len(receipts)} receipts for supplier"
        )
    except Exception as e:
        return error_response(message=f"Failed to fetch receipts: {str(e)}", status_code=500)

@router.put("/{receipt_id}", response_model=dict, dependencies=[Depends(jwt_required)])
def update_receipt(
    receipt_id: UUID,
    request: ConsignmentReceiptUpdate,
    db: Session = Depends(get_db)
):
    """
    Update an existing consignment receipt
    
    **Path parameters:**
    - receipt_id: UUID of the receipt to update
    
    **Optional fields to update:**
    - receipt_date: New receipt date
    - quantity_received: New quantity
    - unit_price: New unit price
    - total_value: New total value
    - notes: New notes
    """
    try:
        result = update_consignment_receipt(db, receipt_id, request)
        return success_response(
            data={
                "id": str(result.id),
                "receipt_number": result.receipt_number,
                "receipt_date": result.receipt_date.isoformat(),
                "quantity_received": to_float(result.quantity_received),
                "total_value": to_float(result.total_value) if result.total_value is not None else None,
                "updated_at": result.updated_at.isoformat()
            },
            message="Consignment receipt updated successfully"
        )
    except ValueError as e:
        return error_response(message=str(e), status_code=404)
    except Exception as e:
        return error_response(message=f"Failed to update receipt: {str(e)}", status_code=500)

@router.delete("/{receipt_id}", response_model=dict, dependencies=[Depends(jwt_required)])
def delete_receipt(
    receipt_id: UUID,
    db: Session = Depends(get_db)
):
    """
    Delete a consignment receipt
    
    **Path parameters:**
    - receipt_id: UUID of the receipt to delete
    """
    try:
        result = delete_consignment_receipt(db, receipt_id)
        return success_response(
            data=result,
            message="Consignment receipt deleted successfully"
        )
    except ValueError as e:
        return error_response(message=str(e), status_code=404)
    except Exception as e:
        return error_response(message=f"Failed to delete receipt: {str(e)}", status_code=500)

@router.post("/report/date-range", response_model=dict)
def get_receipts_by_date(
    start_date: date,
    end_date: date,
    db: Session = Depends(get_db)
):
    """
    Get consignment receipts within a date range
    
    **Query parameters:**
    - start_date: Start date (YYYY-MM-DD)
    - end_date: End date (YYYY-MM-DD)
    """
    try:
        receipts = get_consignment_receipts_by_date_range(db, start_date, end_date)
        return success_response(
            data=receipts,
            message=f"Retrieved {len(receipts)} receipts for date range"
        )
    except Exception as e:
        return error_response(message=f"Failed to fetch receipts: {str(e)}", status_code=500)

@router.get("/summary/report", response_model=dict)
def get_receipt_summary(
    supplier_id: Optional[UUID] = None,
    db: Session = Depends(get_db)
):
    """
    Get summary of consignment receipts (total quantity, total value)
    
    **Query parameters:**
    - supplier_id (optional): Filter by specific supplier
    """
    try:
        summary = get_consignment_receipt_summary(db, supplier_id)
        return success_response(
            data=summary,
            message="Receipt summary retrieved successfully"
        )
    except Exception as e:
        return error_response(message=f"Failed to fetch summary: {str(e)}", status_code=500)
