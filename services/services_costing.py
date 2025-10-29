"""
Average Costing Service
Handles automatic cost calculation using average costing method
"""
from sqlalchemy.orm import Session
from sqlalchemy import and_
from models.inventory import Inventory, ProductCostHistory
from models.workorder import Product
from decimal import Decimal
import uuid
import datetime
from typing import Optional, Dict, Any
import logging

logger = logging.getLogger(__name__)

def to_dict(obj):
    """Convert SQLAlchemy object to dictionary"""
    result = {}
    for c in obj.__table__.columns:
        value = getattr(obj, c.name)
        if isinstance(value, uuid.UUID):
            value = str(value)
        elif isinstance(value, Decimal):
            value = float(value)
        elif isinstance(value, (datetime.datetime, datetime.date, datetime.time)):
            value = value.isoformat()
        result[c.name] = value
    return result


def calculate_average_cost(
    db: Session,
    product_id: str,
    purchase_quantity: Decimal,
    purchase_price: Decimal,
    created_by: str = 'system',
    notes: Optional[str] = None
) -> Dict[str, Any]:
    """
    Calculate average cost for a product based on new purchase.
    
    Formula:
    - If current_quantity == 0: new_cost = purchase_price
    - Else: new_cost = (current_qty * current_cost + purchase_qty * purchase_price) / (current_qty + purchase_qty)
    
    Args:
        db: Database session
        product_id: UUID of the product
        purchase_quantity: Quantity being purchased
        purchase_price: Price per unit of the purchase
        created_by: User performing the action
        notes: Additional notes for the cost history
    
    Returns:
        Dictionary with calculation results and updated product info
    """
    try:
        # Get product
        product = db.query(Product).filter(Product.id == product_id).first()
        if not product:
            raise ValueError(f'Product with ID {product_id} not found')
        
        # Skip calculation for consignment products
        if product.is_consignment:
            logger.info(f'Skipping average cost calculation for consignment product: {product.name}')
            return {
                'success': True,
                'skipped': True,
                'reason': 'consignment_product',
                'product_id': str(product_id),
                'product_name': product.name
            }
        
        # Get current inventory
        inventory = db.query(Inventory).filter(Inventory.product_id == product_id).first()
        current_quantity = inventory.quantity if inventory else Decimal('0')
        current_cost = product.cost if product.cost else Decimal('0')
        
        # Store old values for history
        old_cost = current_cost
        old_quantity = current_quantity
        
        # Calculate new average cost
        if current_quantity == 0:
            # No existing stock, use purchase price directly
            new_cost = purchase_price
            calculation_notes = f'Initial cost set to purchase price (no existing stock)'
        else:
            # Calculate weighted average
            total_value = (current_quantity * current_cost) + (purchase_quantity * purchase_price)
            total_quantity = current_quantity + purchase_quantity
            new_cost = total_value / total_quantity
            calculation_notes = f'Average cost: ({current_quantity} × {current_cost}) + ({purchase_quantity} × {purchase_price}) / {total_quantity}'
        
        # Round to 2 decimal places
        new_cost = new_cost.quantize(Decimal('0.01'))
        new_quantity = current_quantity + purchase_quantity
        
        # Update product cost
        product.cost = new_cost
        db.flush()
        
        # Create cost history record
        cost_history = ProductCostHistory(
            id=uuid.uuid4(),
            product_id=product_id,
            old_cost=old_cost,
            new_cost=new_cost,
            old_quantity=old_quantity,
            new_quantity=new_quantity,
            purchase_quantity=purchase_quantity,
            purchase_price=purchase_price,
            calculation_method='average',
            notes=notes or calculation_notes,
            created_at=datetime.datetime.now(datetime.timezone.utc),
            created_by=created_by
        )
        db.add(cost_history)
        db.commit()
        db.refresh(product)
        db.refresh(cost_history)
        
        logger.info(f'Average cost calculated for product {product.name}: {old_cost} → {new_cost}')
        
        return {
            'success': True,
            'skipped': False,
            'product_id': str(product_id),
            'product_name': product.name,
            'old_cost': float(old_cost),
            'new_cost': float(new_cost),
            'old_quantity': float(old_quantity),
            'new_quantity': float(new_quantity),
            'purchase_quantity': float(purchase_quantity),
            'purchase_price': float(purchase_price),
            'cost_history_id': str(cost_history.id)
        }
        
    except Exception as e:
        db.rollback()
        logger.error(f'Error calculating average cost: {str(e)}')
        raise


def calculate_average_cost_for_adjustment(
    db: Session,
    product_id: str,
    adjustment_quantity: Decimal,
    created_by: str = 'system',
    notes: Optional[str] = None
) -> Dict[str, Any]:
    """
    Handle cost calculation for manual inventory adjustments.
    For adjustments, we don't change the cost, but we record the quantity change.
    
    Args:
        db: Database session
        product_id: UUID of the product
        adjustment_quantity: Quantity being adjusted (positive or negative)
        created_by: User performing the action
        notes: Additional notes for the cost history
    
    Returns:
        Dictionary with adjustment results
    """
    try:
        # Get product
        product = db.query(Product).filter(Product.id == product_id).first()
        if not product:
            raise ValueError(f'Product with ID {product_id} not found')
        
        # Skip for consignment products
        if product.is_consignment:
            logger.info(f'Skipping cost tracking for consignment product adjustment: {product.name}')
            return {
                'success': True,
                'skipped': True,
                'reason': 'consignment_product',
                'product_id': str(product_id),
                'product_name': product.name
            }
        
        # Get current inventory
        inventory = db.query(Inventory).filter(Inventory.product_id == product_id).first()
        current_quantity = inventory.quantity if inventory else Decimal('0')
        current_cost = product.cost if product.cost else Decimal('0')
        
        # For adjustments, cost remains the same
        old_quantity = current_quantity
        new_quantity = current_quantity + adjustment_quantity
        
        # Create cost history record for tracking
        cost_history = ProductCostHistory(
            id=uuid.uuid4(),
            product_id=product_id,
            old_cost=current_cost,
            new_cost=current_cost,  # Cost doesn't change for adjustments
            old_quantity=old_quantity,
            new_quantity=new_quantity,
            purchase_quantity=adjustment_quantity,
            purchase_price=None,  # No purchase price for adjustments
            calculation_method='adjustment',
            notes=notes or f'Manual inventory adjustment: {adjustment_quantity}',
            created_at=datetime.datetime.now(datetime.timezone.utc),
            created_by=created_by
        )
        db.add(cost_history)
        db.commit()
        db.refresh(cost_history)
        
        logger.info(f'Cost history recorded for adjustment on product {product.name}: quantity {old_quantity} → {new_quantity}')
        
        return {
            'success': True,
            'skipped': False,
            'product_id': str(product_id),
            'product_name': product.name,
            'cost': float(current_cost),
            'old_quantity': float(old_quantity),
            'new_quantity': float(new_quantity),
            'adjustment_quantity': float(adjustment_quantity),
            'cost_history_id': str(cost_history.id)
        }
        
    except Exception as e:
        db.rollback()
        logger.error(f'Error recording cost history for adjustment: {str(e)}')
        raise


def get_product_cost_history(
    db: Session,
    product_id: Optional[str] = None,
    start_date: Optional[datetime.datetime] = None,
    end_date: Optional[datetime.datetime] = None,
    calculation_method: Optional[str] = None
) -> list:
    """
    Get cost history records with optional filters.
    
    Args:
        db: Database session
        product_id: Filter by product ID
        start_date: Filter by start date
        end_date: Filter by end date
        calculation_method: Filter by calculation method
    
    Returns:
        List of cost history records with product names
    """
    query = db.query(ProductCostHistory, Product).join(
        Product, ProductCostHistory.product_id == Product.id
    )
    
    # Apply filters
    if product_id:
        query = query.filter(ProductCostHistory.product_id == product_id)
    if start_date:
        query = query.filter(ProductCostHistory.created_at >= start_date)
    if end_date:
        query = query.filter(ProductCostHistory.created_at <= end_date)
    if calculation_method:
        query = query.filter(ProductCostHistory.calculation_method == calculation_method)
    
    # Order by date descending
    query = query.order_by(ProductCostHistory.created_at.desc())
    
    results = query.all()
    
    # Format results
    history_list = []
    for cost_history, product in results:
        history_dict = to_dict(cost_history)
        history_dict['product_name'] = product.name
        history_list.append(history_dict)
    
    return history_list


def get_product_cost_summary(db: Session, product_id: str) -> Dict[str, Any]:
    """
    Get summary of cost changes for a product.
    
    Args:
        db: Database session
        product_id: UUID of the product
    
    Returns:
        Dictionary with cost summary information
    """
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise ValueError(f'Product with ID {product_id} not found')
    
    # Get latest cost history
    latest_history = db.query(ProductCostHistory).filter(
        ProductCostHistory.product_id == product_id
    ).order_by(ProductCostHistory.created_at.desc()).first()
    
    # Get total number of cost changes
    total_changes = db.query(ProductCostHistory).filter(
        ProductCostHistory.product_id == product_id
    ).count()
    
    # Get current inventory
    inventory = db.query(Inventory).filter(Inventory.product_id == product_id).first()
    current_quantity = inventory.quantity if inventory else Decimal('0')
    
    return {
        'product_id': str(product_id),
        'product_name': product.name,
        'current_cost': float(product.cost) if product.cost else None,
        'current_quantity': float(current_quantity),
        'is_consignment': product.is_consignment,
        'total_cost_changes': total_changes,
        'latest_change': to_dict(latest_history) if latest_history else None
    }
