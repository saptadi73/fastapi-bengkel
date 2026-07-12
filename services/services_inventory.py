# type: ignore
from schemas.service_inventory import CreateProductMovedHistory, ProductMoveHistoryReportRequest, ProductMoveHistoryReport, ProductMoveHistoryReportItem, ManualAdjustment, PurchaseOrderUpdateCost
from schemas.service_accounting import InternalConsumptionCreate
from models.inventory import Inventory, ProductMovedHistory
from services.services_costing import calculate_average_cost_for_adjustment
from services.services_accounting import create_lost_goods_journal_entry, create_internal_consumption_journal_entry
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
        timestamp=now_utc,
        reference_type=move_data.reference_type,
        reference_id=move_data.reference_id,
        purchase_order_id=move_data.purchase_order_id,
        workorder_id=move_data.workorder_id,
        supplier_id=move_data.supplier_id,
        customer_id=move_data.customer_id,
        vehicle_id=move_data.vehicle_id,
        purchase_price=move_data.purchase_price,
        selling_price=move_data.selling_price,
        hpp_snapshot=move_data.hpp_snapshot,
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


def consume_internal_product(db: Session, consumption_data: InternalConsumptionCreate):
    """Konsumsi internal: keluarkan stok dan catat jurnal pengeluaran barang."""
    try:
        # Step 1: keluarkan stok (outcome)
        move_data = CreateProductMovedHistory(
            product_id=consumption_data.product_id,
            type='outcome',
            quantity=consumption_data.quantity,
            performed_by=consumption_data.created_by or 'system',
            notes=consumption_data.memo,
            timestamp=datetime.datetime.now(datetime.timezone.utc),
            reference_type='internal_consumption',
            reference_id=consumption_data.product_id,
            hpp_snapshot=consumption_data.cost_per_unit,
        )
        movement = createProductMoveHistoryNew(db, move_data)

        # Step 2: catat jurnal pengeluaran barang internal
        journal = create_internal_consumption_journal_entry(db, consumption_data=consumption_data)

        return {
            "movement": movement,
            "journal": journal
        }
    except Exception:
        db.rollback()
        raise

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
        timestamp=now_utc,
        reference_type=move_data.reference_type or 'loss',
        reference_id=move_data.reference_id,
        purchase_order_id=move_data.purchase_order_id,
        workorder_id=move_data.workorder_id,
        supplier_id=move_data.supplier_id,
        customer_id=move_data.customer_id,
        vehicle_id=move_data.vehicle_id,
        purchase_price=move_data.purchase_price,
        selling_price=move_data.selling_price,
        hpp_snapshot=move_data.hpp_snapshot,
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
    """Generate a paginated stock card from structured movement references."""
    from models.customer import Customer, Vehicle
    from models.supplier import Supplier
    from models.purchase_order import PurchaseOrder, PurchaseOrderLine
    from models.workorder import Workorder, ProductOrdered

    start_at = datetime.datetime.combine(request.start_date, datetime.time.min)
    end_at = datetime.datetime.combine(
        request.end_date + datetime.timedelta(days=1), datetime.time.min
    )

    if request.product_id and not db.query(Product.id).filter(Product.id == request.product_id).first():
        raise LookupError('Product tidak ditemukan')
    if request.supplier_id and not db.query(Supplier.id).filter(Supplier.id == request.supplier_id).first():
        raise LookupError('Supplier tidak ditemukan')
    if request.customer_id and not db.query(Customer.id).filter(Customer.id == request.customer_id).first():
        raise LookupError('Customer tidak ditemukan')

    opening_query = db.query(
        ProductMovedHistory.product_id,
        func.coalesce(func.sum(ProductMovedHistory.quantity), 0),
    ).filter(ProductMovedHistory.timestamp < start_at)
    if request.product_id:
        opening_query = opening_query.filter(ProductMovedHistory.product_id == request.product_id)
    opening_rows = opening_query.group_by(ProductMovedHistory.product_id).all()
    opening_by_product = {row[0]: decimal.Decimal(row[1]) for row in opening_rows}

    query = db.query(ProductMovedHistory, Product).join(
        Product, ProductMovedHistory.product_id == Product.id
    ).filter(
        ProductMovedHistory.timestamp >= start_at,
        ProductMovedHistory.timestamp < end_at,
    )
    if request.product_id:
        query = query.filter(ProductMovedHistory.product_id == request.product_id)
    if request.movement_type:
        query = query.filter(ProductMovedHistory.type == request.movement_type)
    if request.reference_type:
        query = query.filter(ProductMovedHistory.reference_type == request.reference_type)
    if request.supplier_id:
        query = query.filter(ProductMovedHistory.supplier_id == request.supplier_id)
    if request.customer_id:
        query = query.filter(ProductMovedHistory.customer_id == request.customer_id)
    if request.search:
        pattern = f'%{request.search}%'
        query = query.filter(
            (Product.name.ilike(pattern)) | (ProductMovedHistory.notes.ilike(pattern))
        )
    rows = query.order_by(ProductMovedHistory.timestamp.asc(), ProductMovedHistory.id.asc()).all()

    po_ids = {move.purchase_order_id for move, _ in rows if move.purchase_order_id}
    wo_ids = {move.workorder_id for move, _ in rows if move.workorder_id}
    supplier_ids = {move.supplier_id for move, _ in rows if move.supplier_id}
    customer_ids = {move.customer_id for move, _ in rows if move.customer_id}
    vehicle_ids = {move.vehicle_id for move, _ in rows if move.vehicle_id}

    po_map = {po.id: po for po in db.query(PurchaseOrder).filter(PurchaseOrder.id.in_(po_ids)).all()} if po_ids else {}
    wo_map = {wo.id: wo for wo in db.query(Workorder).filter(Workorder.id.in_(wo_ids)).all()} if wo_ids else {}
    supplier_map = {s.id: s for s in db.query(Supplier).filter(Supplier.id.in_(supplier_ids)).all()} if supplier_ids else {}
    customer_map = {c.id: c for c in db.query(Customer).filter(Customer.id.in_(customer_ids)).all()} if customer_ids else {}
    vehicle_map = {v.id: v for v in db.query(Vehicle).filter(Vehicle.id.in_(vehicle_ids)).all()} if vehicle_ids else {}

    balances = dict(opening_by_product)
    items = []
    total_in = decimal.Decimal('0')
    total_out = decimal.Decimal('0')
    total_adjustment = decimal.Decimal('0')
    for move, product in rows:
        quantity = decimal.Decimal(move.quantity)
        movement_type = (move.type or '').lower()
        if movement_type in {'outcome', 'loss', 'internal_consumption'} and quantity > 0:
            quantity = -quantity
        quantity_in = quantity if quantity > 0 else decimal.Decimal('0')
        quantity_out = abs(quantity) if quantity < 0 else decimal.Decimal('0')
        before = balances.get(move.product_id, decimal.Decimal('0'))
        after = before + quantity
        balances[move.product_id] = after
        if movement_type == 'adjustment':
            total_adjustment += quantity
        elif quantity > 0:
            total_in += quantity
        elif quantity < 0:
            total_out += abs(quantity)

        po = po_map.get(move.purchase_order_id)
        wo = wo_map.get(move.workorder_id)
        supplier = supplier_map.get(move.supplier_id)
        customer = customer_map.get(move.customer_id)
        vehicle = vehicle_map.get(move.vehicle_id)
        reference_type = move.reference_type
        reference_no = po.po_no if po else (wo.no_wo if wo else None)
        price = move.purchase_price if quantity > 0 else move.selling_price

        items.append(ProductMoveHistoryReportItem(
            movement_id=str(move.id), product_id=str(move.product_id),
            product_name=product.name, type=move.type, quantity=quantity,
            quantity_in=quantity_in, quantity_out=quantity_out,
            balance_before=before, balance_after=after,
            purchase_price=move.purchase_price, selling_price=move.selling_price,
            price=price, hpp=move.hpp_snapshot,
            reference_type=reference_type,
            reference_id=str(move.reference_id) if move.reference_id else None,
            reference_no=reference_no,
            purchase_order_id=str(move.purchase_order_id) if move.purchase_order_id else None,
            purchase_order_no=po.po_no if po else None,
            workorder_id=str(move.workorder_id) if move.workorder_id else None,
            workorder_no=wo.no_wo if wo else None,
            supplier_id=str(move.supplier_id) if move.supplier_id else None,
            vendor_code=supplier.supplier_code if supplier else None,
            vendor_name=supplier.nama if supplier else None,
            customer_id=str(move.customer_id) if move.customer_id else None,
            customer_name=customer.nama if customer else None,
            vehicle_id=str(move.vehicle_id) if move.vehicle_id else None,
            nopol=vehicle.no_pol if vehicle else None,
            timestamp=move.timestamp, performed_by=move.performed_by, notes=move.notes,
        ))

    total = len(items)
    total_pages = (total + request.limit - 1) // request.limit if total else 0
    if request.sort_order == 'desc':
        items.reverse()
    start = (request.page - 1) * request.limit
    paginated_items = items[start:start + request.limit]
    opening_balance = sum(opening_by_product.values(), decimal.Decimal('0'))

    from schemas.service_inventory import ProductMoveHistorySummary, ProductMoveHistoryPagination
    return ProductMoveHistoryReport(
        summary=ProductMoveHistorySummary(
            opening_balance=opening_balance, total_in=total_in, total_out=total_out,
            total_adjustment=total_adjustment,
            closing_balance=opening_balance + total_in - total_out + total_adjustment,
        ),
        total_entries=total,
        items=paginated_items,
        pagination=ProductMoveHistoryPagination(
            page=request.page, limit=request.limit, total=total,
            total_pages=total_pages, has_previous=request.page > 1,
            has_next=request.page < total_pages,
        ),
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
        timestamp=now_utc,
        reference_type='adjustment',
        hpp_snapshot=product.cost if (product := db.query(Product).filter(Product.id == adjustment_data.product_id).first()) else None,
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




