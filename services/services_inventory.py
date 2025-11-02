from schemas.service_inventory import CreateProductMovedHistory, ProductMoveHistoryReportRequest, ProductMoveHistoryReport, ProductMoveHistoryReportItem, ManualAdjustment, PurchaseOrderUpdateCost
from models.inventory import Inventory, ProductMovedHistory
from services.services_costing import calculate_average_cost_for_adjustment
from services.services_accounting import create_lost_goods_journal_entry
from schemas.service_accounting import LostGoodsJournalEntry
from services.services_product import getInventoryByProductID
from sqlalchemy.exc import IntegrityError
from datetime import datetime
from sqlalchemy.orm import Session
from sqlalchemy import func, select
import uuid
import decimal
import datetime
from models.workorder import Product  # Product model is in workorder.py
from models.customer import Customer
from models.supplier import Supplier

def to_dict(obj):
    result = {}
    for c in obj.__table__.columns:
        value = getattr(obj, c.name)
        # Konversi UUID ke string
        if isinstance(value, uuid.UUID):
            value = str(value)
        # Konversi Decimal ke float
        elif isinstance(value, decimal.Decimal):
            value = float(value)
        # Konversi datetime/date/time ke isoformat string
        elif isinstance(value, (datetime.datetime, datetime.date, datetime.time)):
            value = value.isoformat()
        # Konversi bytes ke string (opsional, jika ada kolom bytes)
        elif isinstance(value, bytes):
            value = value.decode('utf-8')
        result[c.name] = value
    return result

def get_or_create_inventory(db: Session, product_id: str):
    inventory = db.query(Inventory).filter(Inventory.product_id == product_id).first()
    now_utc = datetime.datetime.now(datetime.timezone.utc)
    if not inventory:
        inventory = Inventory(
            id=str(uuid.uuid4()),
            product_id=product_id,
            quantity=0,
            created_at=now_utc,
            updated_at=now_utc
        )
        db.add(inventory)
        db.commit()
        db.refresh(inventory)
    return to_dict(inventory)

def createProductMoveHistoryNew(db: Session, move_data: CreateProductMovedHistory):
    inventory = db.query(Inventory).filter(Inventory.product_id == move_data.product_id).first()
    if move_data.type.lower() == 'income':
        now_utc = move_data.timestamp or datetime.datetime.now(datetime.timezone.utc)
        if not inventory:
            # Buat inventory baru
            inventory = Inventory(
                id=str(uuid.uuid4()),
                product_id=move_data.product_id,
                quantity=move_data.quantity,
                created_at=now_utc,
                updated_at=now_utc
            )
            db.add(inventory)
        else:
            # Update quantity lama + quantity baru
            inventory.quantity += move_data.quantity
            inventory.updated_at = now_utc
    elif move_data.type.lower() == 'outcome':
        now_utc = move_data.timestamp or datetime.datetime.now(datetime.timezone.utc)
        if not inventory:
            raise ValueError('Inventory untuk produk ini belum ada, tidak bisa outcome!')
        if inventory.quantity < move_data.quantity:
            raise ValueError('Stock tidak cukup untuk outcome!')
        inventory.quantity -= move_data.quantity
        inventory.updated_at = now_utc
    # Catat ke ProductMovedHistory
    now_utc = move_data.timestamp or datetime.datetime.now(datetime.timezone.utc)
    if move_data.type.lower() == 'income':
        quantityku = move_data.quantity
    else:
        quantityku = -move_data.quantity

    new_move = ProductMovedHistory(
        id=str(uuid.uuid4()),
        product_id=move_data.product_id,
        type=move_data.type,
        quantity=quantityku,
        performed_by=move_data.performed_by,
        notes=move_data.notes,
        timestamp=now_utc
    )
    db.add(new_move)
    db.commit()
    db.refresh(new_move)

    # Setelah commit, update inventory.quantity = sum seluruh ProductMovedHistory.quantity untuk product_id terkait
    inventory = db.query(Inventory).filter(Inventory.product_id == move_data.product_id).first()
    if inventory:
        total_quantity = db.scalar(select(func.sum(ProductMovedHistory.quantity)).where(ProductMovedHistory.product_id == move_data.product_id)) or 0
        inventory.quantity = total_quantity
        inventory.updated_at = datetime.datetime.now(datetime.timezone.utc)
        db.commit()
        db.refresh(inventory)

    return to_dict(new_move)

def createProductMoveHistoryNewLoss(db: Session, move_data: CreateProductMovedHistory):
    if move_data.type.lower() != 'outcome':
        raise ValueError("Type must be 'outcome' for product loss")

    inventory = db.query(Inventory).filter(Inventory.product_id == move_data.product_id).first()

    now_utc = move_data.timestamp or datetime.datetime.now(datetime.timezone.utc)
    if not inventory:
        raise ValueError('Inventory untuk produk ini belum ada, tidak bisa outcome!')
    if inventory.quantity < move_data.quantity:
        raise ValueError('Stock tidak cukup untuk outcome!')
    inventory.quantity -= move_data.quantity
    inventory.updated_at = now_utc

    # Catat ke ProductMovedHistory
    quantityku = -move_data.quantity

    new_move = ProductMovedHistory(
        id=str(uuid.uuid4()),
        product_id=move_data.product_id,
        type=move_data.type,
        quantity=quantityku,
        performed_by=move_data.performed_by,
        notes=move_data.notes,
        timestamp=now_utc
    )
    db.add(new_move)
    db.commit()
    db.refresh(new_move)

    # Setelah commit, update inventory.quantity = sum seluruh ProductMovedHistory.quantity untuk product_id terkait
    inventory = db.query(Inventory).filter(Inventory.product_id == move_data.product_id).first()
    if inventory:
        total_quantity = db.scalar(select(func.sum(ProductMovedHistory.quantity)).where(ProductMovedHistory.product_id == move_data.product_id)) or 0
        inventory.quantity = total_quantity
        inventory.updated_at = datetime.datetime.now(datetime.timezone.utc)
        db.commit()
        db.refresh(inventory)

    journal_entry = create_lost_goods_journal_entry(db, LostGoodsJournalEntry(
        product_id=move_data.product_id,
        quantity=move_data.quantity,
        memo='Kehilangan Produk Gudang',
        loss_account_code="6003",
        inventory_account_code="2002",
        date=now_utc,))

    return {
        'move': to_dict(new_move),
        'journal': journal_entry
    }


def generate_product_move_history_report(db: Session, request: ProductMoveHistoryReportRequest) -> ProductMoveHistoryReport:
    """
    Generate a product move history report within a date range.
    Lists all product movement entries with product details, customer for outcome, supplier for income.
    """
    

    # Query ProductMovedHistory with product join
    query = db.query(ProductMovedHistory, Product).join(Product, ProductMovedHistory.product_id == Product.id).filter(
        ProductMovedHistory.timestamp >= request.start_date,
        ProductMovedHistory.timestamp <= request.end_date
    ).order_by(ProductMovedHistory.timestamp)

    moves = query.all()

    items = []
    for move, product in moves:
        customer_name = None
        supplier_name = None

        # For outcome, get customer from related workorder or sale
        if move.type.lower() == 'outcome':
            # Assuming notes or performed_by might contain customer info, or we need to join with workorder
            # For simplicity, if notes contain customer name, or we can add logic to fetch from workorder
            # Since the model doesn't have direct customer_id, we might need to parse notes or add a field
            # For now, leave as None, or assume notes contain customer name
            if move.notes and "customer:" in move.notes.lower():
                # Parse customer name from notes if present
                customer_name = move.notes.split("customer:")[1].strip() if "customer:" in move.notes.lower() else None

        # For income, get supplier from related purchase
        elif move.type.lower() == 'income':
            if move.notes and "supplier:" in move.notes.lower():
                supplier_name = move.notes.split("supplier:")[1].strip() if "supplier:" in move.notes.lower() else None

        items.append(ProductMoveHistoryReportItem(
            product_id=str(move.product_id),
            product_name=product.name,
            type=move.type,
            quantity=move.quantity,
            timestamp=move.timestamp,
            performed_by=move.performed_by,
            notes=move.notes,
            customer_name=customer_name,
            supplier_name=supplier_name
        ))

    return ProductMoveHistoryReport(
        total_entries=len(items),
        items=items
    )

def manual_adjustment_inventory(db: Session, adjustment_data: ManualAdjustment):
    """
    Perform manual adjustment to inventory quantity.
    This creates a ProductMovedHistory entry with type 'adjustment'.
    """
    # Get or create inventory
    inventory = db.query(Inventory).filter(Inventory.product_id == adjustment_data.product_id).first()
    now_utc = adjustment_data.timestamp or datetime.datetime.now(datetime.timezone.utc)
    if not inventory:
        inventory = Inventory(
            id=str(uuid.uuid4()),
            product_id=adjustment_data.product_id,
            quantity=adjustment_data.quantity,
            created_at=now_utc,
            updated_at=now_utc
        )
        db.add(inventory)
    else:
        # Update quantity with adjustment
        inventory.quantity += adjustment_data.quantity
        inventory.updated_at = now_utc

    # Create ProductMovedHistory entry for adjustment
    new_move = ProductMovedHistory(
        id=str(uuid.uuid4()),
        product_id=adjustment_data.product_id,
        type='adjustment',
        quantity=adjustment_data.quantity,
        performed_by=adjustment_data.performed_by,
        notes=adjustment_data.notes,
        timestamp=now_utc
    )
    db.add(new_move)
    db.commit()
    db.refresh(new_move)

    # Update inventory quantity based on sum of all ProductMovedHistory
    total_quantity = db.scalar(select(func.sum(ProductMovedHistory.quantity)).where(ProductMovedHistory.product_id == adjustment_data.product_id)) or 0
    inventory.quantity = total_quantity
    inventory.updated_at = datetime.datetime.now(datetime.timezone.utc)
    db.commit()
    db.refresh(inventory)

    # Track cost history for adjustment (cost doesn't change, but we track quantity change)
    try:
        cost_result = calculate_average_cost_for_adjustment(
            db=db,
            product_id=str(adjustment_data.product_id),
            adjustment_quantity=adjustment_data.quantity,
            created_by=adjustment_data.performed_by,
            notes=adjustment_data.notes or 'Manual inventory adjustment'
        )
        print(f"Cost history tracked for adjustment: {cost_result}")
    except Exception as e:
        print(f"Error tracking cost history for adjustment: {str(e)}")
        # Continue even if cost tracking fails

    return to_dict(new_move)

def updateCostCostingMethodeAverage(db: Session, dataPurchase: PurchaseOrderUpdateCost):
    """
    Update the average cost for a product based on current inventory and costing method.
    """
    try:
        # Get the current cost of the product
        product = db.query(Product).filter(Product.id == dataPurchase.product_id).first()
        if not product:
            raise ValueError("Product not found")
        current_cost = product.cost

        # Get current stock quantity
        inventory = getInventoryByProductID(db, dataPurchase.product_id)
        current_stock = inventory['total_stock'] if inventory else 0

        # Calculate new average cost
        total_cost = (decimal.Decimal(current_cost) * decimal.Decimal(current_stock)) + (decimal.Decimal(dataPurchase.price) * decimal.Decimal(dataPurchase.quantity))
        total_quantity = decimal.Decimal(current_stock) + decimal.Decimal(dataPurchase.quantity)
        if total_quantity == 0:
            new_average_cost = decimal.Decimal("0.00")
        else:
            new_average_cost = total_cost / total_quantity

        # Update product cost
        product.cost = new_average_cost
        db.commit()
        db.refresh(product)
        return {
            "new_average_cost": round(float(new_average_cost)),
            "error_product": None,
            "error_inventory": None
        }
    except Exception as e:
        raise ValueError(f"Error updating average cost: {str(e)}")




