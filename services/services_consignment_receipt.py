"""
Services untuk Consignment Receipt Management
"""

from sqlalchemy.orm import Session
from sqlalchemy import func
from uuid import UUID
from typing import Optional
from datetime import datetime, date
from decimal import Decimal
from models.consignment import ConsignmentReceipt
from models.workorder import Product
from models.customer import Supplier
from schemas.consignment_receipt import ConsignmentReceiptCreate, ConsignmentReceiptUpdate

def create_consignment_receipt(db: Session, receipt_data: ConsignmentReceiptCreate, username: str) -> ConsignmentReceipt:
    """
    Create a new consignment receipt record
    """
    try:
        # Validate product and supplier exist
        product = db.query(Product).filter(Product.id == receipt_data.product_id).first()
        if not product:
            raise ValueError(f"Product with ID {receipt_data.product_id} not found")
        
        if not product.is_consignment:
            raise ValueError(f"Product {product.name} is not marked as consignment")
        
        supplier = db.query(Supplier).filter(Supplier.id == receipt_data.supplier_id).first()
        if not supplier:
            raise ValueError(f"Supplier with ID {receipt_data.supplier_id} not found")
        
        # Calculate total_value if unit_price provided
        total_value = receipt_data.total_value
        if receipt_data.unit_price and not total_value:
            total_value = receipt_data.quantity_received * receipt_data.unit_price
        
        # Create receipt
        new_receipt = ConsignmentReceipt(
            product_id=receipt_data.product_id,
            supplier_id=receipt_data.supplier_id,
            receipt_number=receipt_data.receipt_number,
            receipt_date=receipt_data.receipt_date,
            quantity_received=receipt_data.quantity_received,
            unit_price=receipt_data.unit_price,
            total_value=total_value,
            notes=receipt_data.notes,
            received_by=receipt_data.received_by or username,
            created_at=datetime.utcnow()
        )
        
        db.add(new_receipt)
        db.commit()
        db.refresh(new_receipt)
        
        return new_receipt
    except Exception as e:
        db.rollback()
        raise Exception(f"Failed to create consignment receipt: {str(e)}")

def get_consignment_receipt(db: Session, receipt_id: UUID) -> ConsignmentReceipt:
    """
    Get single consignment receipt by ID
    """
    receipt = db.query(ConsignmentReceipt).filter(ConsignmentReceipt.id == receipt_id).first()
    if not receipt:
        raise ValueError(f"Consignment receipt with ID {receipt_id} not found")
    return receipt

def get_all_consignment_receipts(db: Session, skip: int = 0, limit: int = 100) -> list:
    """
    Get all consignment receipts with pagination
    """
    try:
        receipts = db.query(
            ConsignmentReceipt.id,
            ConsignmentReceipt.receipt_number,
            ConsignmentReceipt.receipt_date,
            Product.name.label('product_name'),
            Supplier.nama.label('supplier_name'),
            ConsignmentReceipt.quantity_received,
            ConsignmentReceipt.unit_price,
            ConsignmentReceipt.total_value,
            ConsignmentReceipt.received_by,
            ConsignmentReceipt.created_at
        ).join(
            Product, ConsignmentReceipt.product_id == Product.id
        ).join(
            Supplier, ConsignmentReceipt.supplier_id == Supplier.id
        ).order_by(
            ConsignmentReceipt.created_at.desc()
        ).offset(skip).limit(limit).all()
        
        result = []
        for receipt in receipts:
            result.append({
                'id': str(receipt.id),
                'receipt_number': receipt.receipt_number,
                'receipt_date': receipt.receipt_date.isoformat(),
                'product_name': receipt.product_name,
                'supplier_name': receipt.supplier_name,
                'quantity_received': receipt.quantity_received,
                'unit_price': receipt.unit_price,
                'total_value': receipt.total_value,
                'received_by': receipt.received_by,
                'created_at': receipt.created_at.isoformat()
            })
        
        return result
    except Exception as e:
        raise Exception(f"Failed to fetch consignment receipts: {str(e)}")

def get_consignment_receipts_by_supplier(db: Session, supplier_id: UUID, skip: int = 0, limit: int = 100) -> list:
    """
    Get all consignment receipts for a specific supplier
    """
    try:
        receipts = db.query(
            ConsignmentReceipt.id,
            ConsignmentReceipt.receipt_number,
            ConsignmentReceipt.receipt_date,
            Product.name.label('product_name'),
            Supplier.nama.label('supplier_name'),
            ConsignmentReceipt.quantity_received,
            ConsignmentReceipt.unit_price,
            ConsignmentReceipt.total_value,
            ConsignmentReceipt.received_by,
            ConsignmentReceipt.created_at
        ).join(
            Product, ConsignmentReceipt.product_id == Product.id
        ).join(
            Supplier, ConsignmentReceipt.supplier_id == Supplier.id
        ).filter(
            ConsignmentReceipt.supplier_id == supplier_id
        ).order_by(
            ConsignmentReceipt.created_at.desc()
        ).offset(skip).limit(limit).all()
        
        result = []
        for receipt in receipts:
            result.append({
                'id': str(receipt.id),
                'receipt_number': receipt.receipt_number,
                'receipt_date': receipt.receipt_date.isoformat(),
                'product_name': receipt.product_name,
                'supplier_name': receipt.supplier_name,
                'quantity_received': receipt.quantity_received,
                'unit_price': receipt.unit_price,
                'total_value': receipt.total_value,
                'received_by': receipt.received_by,
                'created_at': receipt.created_at.isoformat()
            })
        
        return result
    except Exception as e:
        raise Exception(f"Failed to fetch receipts for supplier: {str(e)}")

def update_consignment_receipt(db: Session, receipt_id: UUID, update_data: ConsignmentReceiptUpdate) -> ConsignmentReceipt:
    """
    Update an existing consignment receipt
    """
    try:
        receipt = db.query(ConsignmentReceipt).filter(ConsignmentReceipt.id == receipt_id).first()
        if not receipt:
            raise ValueError(f"Consignment receipt with ID {receipt_id} not found")
        
        # Update fields
        if update_data.receipt_date is not None:
            receipt.receipt_date = update_data.receipt_date
        if update_data.quantity_received is not None:
            receipt.quantity_received = update_data.quantity_received
        if update_data.unit_price is not None:
            receipt.unit_price = update_data.unit_price
        if update_data.total_value is not None:
            receipt.total_value = update_data.total_value
        elif receipt.unit_price and receipt.quantity_received:
            # Recalculate total_value if quantity or price changed
            receipt.total_value = receipt.quantity_received * receipt.unit_price
        if update_data.notes is not None:
            receipt.notes = update_data.notes
        
        receipt.updated_at = datetime.utcnow()
        
        db.commit()
        db.refresh(receipt)
        
        return receipt
    except Exception as e:
        db.rollback()
        raise Exception(f"Failed to update consignment receipt: {str(e)}")

def delete_consignment_receipt(db: Session, receipt_id: UUID) -> dict:
    """
    Delete a consignment receipt
    """
    try:
        receipt = db.query(ConsignmentReceipt).filter(ConsignmentReceipt.id == receipt_id).first()
        if not receipt:
            raise ValueError(f"Consignment receipt with ID {receipt_id} not found")
        
        receipt_number = receipt.receipt_number
        
        db.delete(receipt)
        db.commit()
        
        return {
            "message": f"Consignment receipt {receipt_number} deleted successfully",
            "deleted_id": str(receipt_id)
        }
    except Exception as e:
        db.rollback()
        raise Exception(f"Failed to delete consignment receipt: {str(e)}")

def get_consignment_receipts_by_date_range(db: Session, start_date: date, end_date: date) -> list:
    """
    Get consignment receipts within a date range
    """
    try:
        receipts = db.query(
            ConsignmentReceipt.id,
            ConsignmentReceipt.receipt_number,
            ConsignmentReceipt.receipt_date,
            Product.name.label('product_name'),
            Supplier.nama.label('supplier_name'),
            ConsignmentReceipt.quantity_received,
            ConsignmentReceipt.unit_price,
            ConsignmentReceipt.total_value,
            ConsignmentReceipt.received_by,
            ConsignmentReceipt.created_at
        ).join(
            Product, ConsignmentReceipt.product_id == Product.id
        ).join(
            Supplier, ConsignmentReceipt.supplier_id == Supplier.id
        ).filter(
            ConsignmentReceipt.receipt_date >= start_date,
            ConsignmentReceipt.receipt_date <= end_date
        ).order_by(
            ConsignmentReceipt.receipt_date.desc()
        ).all()
        
        result = []
        for receipt in receipts:
            result.append({
                'id': str(receipt.id),
                'receipt_number': receipt.receipt_number,
                'receipt_date': receipt.receipt_date.isoformat(),
                'product_name': receipt.product_name,
                'supplier_name': receipt.supplier_name,
                'quantity_received': receipt.quantity_received,
                'unit_price': receipt.unit_price,
                'total_value': receipt.total_value,
                'received_by': receipt.received_by,
                'created_at': receipt.created_at.isoformat()
            })
        
        return result
    except Exception as e:
        raise Exception(f"Failed to fetch receipts by date range: {str(e)}")

def get_consignment_receipt_summary(db: Session, supplier_id: Optional[UUID] = None) -> dict:
    """
    Get summary of consignment receipts (total quantity, total value)
    """
    try:
        query = db.query(
            func.sum(ConsignmentReceipt.quantity_received).label('total_quantity'),
            func.sum(ConsignmentReceipt.total_value).label('total_value'),
            func.count(ConsignmentReceipt.id).label('receipt_count')
        )
        
        if supplier_id is not None:
            query = query.filter(ConsignmentReceipt.supplier_id == supplier_id)
        
        summary = query.first()
        
        return {
            'total_quantity': summary.total_quantity or Decimal('0'),
            'total_value': summary.total_value or Decimal('0'),
            'receipt_count': summary.receipt_count or 0
        }
    except Exception as e:
        raise Exception(f"Failed to get receipt summary: {str(e)}")
