"""
Extended Services untuk Inventory Management (Update/Delete operations)
"""

from sqlalchemy.orm import Session
from uuid import UUID
from datetime import datetime
from decimal import Decimal
from models.inventory import ProductMovedHistory, Inventory
from models.workorder import Product

# ==================== ADJUSTMENT UPDATE/DELETE ====================

def update_inventory_adjustment(db: Session, adjustment_id: UUID, update_data: dict) -> ProductMovedHistory:
    """
    Update an existing inventory adjustment record
    
    Args:
        db: Database session
        adjustment_id: ID of the adjustment to update
        update_data: Dictionary with fields to update {quantity, reason, etc}
    """
    try:
        adjustment = db.query(ProductMovedHistory).filter(
            ProductMovedHistory.id == adjustment_id,
            ProductMovedHistory.type == 'adjustment'
        ).first()
        
        if not adjustment:
            raise ValueError(f"Adjustment with ID {adjustment_id} not found")
        
        # Calculate the difference to adjust inventory
        old_quantity = adjustment.quantity
        new_quantity = update_data.get('quantity', old_quantity)
        quantity_difference = new_quantity - old_quantity
        
        # Update ProductMovedHistory
        adjustment.quantity = new_quantity
        if 'notes' in update_data:
            adjustment.notes = update_data.get('notes')
        
        # Update Inventory if quantity changed
        if quantity_difference != 0:
            inventory = db.query(Inventory).filter(
                Inventory.product_id == adjustment.product_id
            ).first()
            
            if inventory:
                inventory.quantity += Decimal(str(quantity_difference))
                inventory.updated_at = datetime.utcnow()
        
        db.commit()
        db.refresh(adjustment)
        
        return adjustment
    except Exception as e:
        db.rollback()
        raise Exception(f"Failed to update adjustment: {str(e)}")

def delete_inventory_adjustment(db: Session, adjustment_id: UUID) -> dict:
    """
    Delete an inventory adjustment record and reverse its effects on inventory
    
    Args:
        db: Database session
        adjustment_id: ID of the adjustment to delete
    """
    try:
        adjustment = db.query(ProductMovedHistory).filter(
            ProductMovedHistory.id == adjustment_id,
            ProductMovedHistory.type == 'adjustment'
        ).first()
        
        if not adjustment:
            raise ValueError(f"Adjustment with ID {adjustment_id} not found")
        
        # Reverse the adjustment on inventory (subtract the adjustment quantity)
        inventory = db.query(Inventory).filter(
            Inventory.product_id == adjustment.product_id
        ).first()
        
        if inventory:
            # Reverse: if adjustment was -5, add 5 back
            inventory.quantity -= adjustment.quantity
            inventory.updated_at = datetime.utcnow()
        
        # Delete the adjustment record
        db.delete(adjustment)
        db.commit()
        
        return {
            "message": f"Adjustment deleted successfully",
            "deleted_id": str(adjustment_id),
            "reversed_quantity": float(adjustment.quantity)
        }
    except Exception as e:
        db.rollback()
        raise Exception(f"Failed to delete adjustment: {str(e)}")

# ==================== LOSS UPDATE/DELETE ====================

def update_inventory_loss(db: Session, loss_id: UUID, update_data: dict) -> ProductMovedHistory:
    """
    Update an existing inventory loss record
    
    Args:
        db: Database session
        loss_id: ID of the loss to update
        update_data: Dictionary with fields to update {quantity, reason, etc}
    """
    try:
        loss = db.query(ProductMovedHistory).filter(
            ProductMovedHistory.id == loss_id,
            ProductMovedHistory.type == 'loss'
        ).first()
        
        if not loss:
            raise ValueError(f"Loss record with ID {loss_id} not found")
        
        # Calculate the difference to adjust inventory
        old_quantity = loss.quantity  # This is negative
        new_quantity = update_data.get('quantity', old_quantity)
        quantity_difference = new_quantity - old_quantity
        
        # Update ProductMovedHistory
        loss.quantity = new_quantity
        if 'notes' in update_data:
            loss.notes = update_data.get('notes')
        
        # Update Inventory if quantity changed
        if quantity_difference != 0:
            inventory = db.query(Inventory).filter(
                Inventory.product_id == loss.product_id
            ).first()
            
            if inventory:
                # quantity_difference will be the adjustment
                inventory.quantity += Decimal(str(quantity_difference))
                inventory.updated_at = datetime.utcnow()
        
        db.commit()
        db.refresh(loss)
        
        return loss
    except Exception as e:
        db.rollback()
        raise Exception(f"Failed to update loss record: {str(e)}")

def delete_inventory_loss(db: Session, loss_id: UUID) -> dict:
    """
    Delete an inventory loss record and reverse its effects on inventory
    
    Args:
        db: Database session
        loss_id: ID of the loss to delete
    """
    try:
        loss = db.query(ProductMovedHistory).filter(
            ProductMovedHistory.id == loss_id,
            ProductMovedHistory.type == 'loss'
        ).first()
        
        if not loss:
            raise ValueError(f"Loss record with ID {loss_id} not found")
        
        # Reverse the loss on inventory
        # If loss was -2, add 2 back to inventory
        inventory = db.query(Inventory).filter(
            Inventory.product_id == loss.product_id
        ).first()
        
        if inventory:
            inventory.quantity -= loss.quantity  # loss.quantity is negative, so this adds back
            inventory.updated_at = datetime.utcnow()
        
        # Delete the loss record
        db.delete(loss)
        db.commit()
        
        return {
            "message": f"Loss record deleted successfully",
            "deleted_id": str(loss_id),
            "reversed_quantity": float(abs(loss.quantity))
        }
    except Exception as e:
        db.rollback()
        raise Exception(f"Failed to delete loss record: {str(e)}")

def get_loss_by_id(db: Session, loss_id: UUID) -> dict:
    """
    Get a specific loss record by ID
    """
    try:
        loss = db.query(ProductMovedHistory).filter(
            ProductMovedHistory.id == loss_id,
            ProductMovedHistory.type == 'loss'
        ).first()
        
        if not loss:
            raise ValueError(f"Loss record with ID {loss_id} not found")
        
        return {
            'id': str(loss.id),
            'product_id': str(loss.product_id),
            'type': loss.type,
            'quantity': loss.quantity,
            'timestamp': loss.timestamp.isoformat(),
            'performed_by': loss.performed_by,
            'notes': loss.notes
        }
    except Exception as e:
        raise Exception(f"Failed to fetch loss record: {str(e)}")

def get_adjustment_by_id(db: Session, adjustment_id: UUID) -> dict:
    """
    Get a specific adjustment record by ID
    """
    try:
        adjustment = db.query(ProductMovedHistory).filter(
            ProductMovedHistory.id == adjustment_id,
            ProductMovedHistory.type == 'adjustment'
        ).first()
        
        if not adjustment:
            raise ValueError(f"Adjustment with ID {adjustment_id} not found")
        
        return {
            'id': str(adjustment.id),
            'product_id': str(adjustment.product_id),
            'type': adjustment.type,
            'quantity': adjustment.quantity,
            'timestamp': adjustment.timestamp.isoformat(),
            'performed_by': adjustment.performed_by,
            'notes': adjustment.notes
        }
    except Exception as e:
        raise Exception(f"Failed to fetch adjustment record: {str(e)}")
