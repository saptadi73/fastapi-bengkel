# type: ignore
# pyright: ignore[reportGeneralTypeIssues,reportAttributeAccessIssue,reportAssignmentType]
from sqlalchemy.exc import IntegrityError
import datetime
from sqlalchemy.orm import Session
from sqlalchemy import text
from models.purchase_order import PurchaseOrder, PurchaseOrderLine
from schemas.service_accounting import PurchaseJournalEntry
from services.services_accounting import create_purchase_journal_entry
from schemas.service_purchase_order import CreatePurchaseOrder, UpdatePurchaseOrder, CreatePurchaseOrderLine, UpdatePurchaseOrderLine, UpdatePurchaseOrderLineSingle, CreatePurchaseOrderLineSingle
from schemas.service_inventory import CreateProductMovedHistory, PurchaseOrderUpdateCost
from services.services_inventory import createProductMoveHistoryNew, updateCostCostingMethodeAverage
from services.services_costing import calculate_average_cost
from services.services_expenses import edit_expense_status
import decimal
from decimal import Decimal
from uuid import uuid4
import uuid
import enum
import logging

logger = logging.getLogger(__name__)


def _status_value(status):
    if isinstance(status, enum.Enum):
        return status.value
    return status


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
        # Konversi Enum ke value
        elif isinstance(value, enum.Enum):
            value = value.value
        # Konversi bytes ke string (opsional, jika ada kolom bytes)
        elif isinstance(value, bytes):
            value = value.decode('utf-8')
        result[c.name] = value
    return result

def create_purchase_order(db: Session, data: CreatePurchaseOrder):
    # Generate PO number
    result = db.execute(text("SELECT nextval('purchase_order_seq')")).scalar()
    po_no = f"PO{result:03d}"

    # Create PurchaseOrder
    purchase_order = PurchaseOrder(
        id=uuid.uuid4(),
        po_no=po_no,
        supplier_id=data.supplier_id,
        date=data.date,
        total=Decimal("0.00"),  # Will be calculated after lines
        pajak=data.pajak,
        pembayaran=data.pembayaran,
        dp=data.dp,
        status_pembayaran=data.status_pembayaran,
        status=data.status,
        bukti_transfer=data.bukti_transfer
    )
    db.add(purchase_order)
    db.flush()  # Get id

    # Create lines
    total = Decimal("0.00")
    for line_data in data.lines:
        discount = line_data.discount or Decimal("0")
        subtotal = (line_data.quantity * line_data.price) - discount
        line = PurchaseOrderLine(
            id=uuid.uuid4(),
            purchase_order_id=purchase_order.id,
            product_id=line_data.product_id,
            quantity=line_data.quantity,
            price=line_data.price,
            discount=line_data.discount,
            subtotal=subtotal
        )
        db.add(line)
        total += subtotal

    purchase_order.total = total

    db.commit()
    db.refresh(purchase_order)

    # If status is 'diterima', call productMovedHistoryNew with type 'income'
    status_value = _status_value(purchase_order.status)
    if status_value == 'diterima':
        for line in purchase_order.lines:
            move_data = CreateProductMovedHistory(
                product_id=line.product_id,
                type='income',
                quantity=line.quantity,
                performed_by='system',
                notes=f'Purchase order {purchase_order.po_no} received',
                timestamp=datetime.datetime.now()
            )
            createProductMoveHistoryNew(db, move_data)

    return to_dict(purchase_order)

def get_all_purchase_orders(db: Session):
    purchase_orders = db.query(PurchaseOrder).order_by(PurchaseOrder.date.desc()).all()
    result = []
    for po in purchase_orders:
        po_dict = to_dict(po)
        po_dict['supplier_name'] = po.supplier.nama if po.supplier else None
        lines = []
        for line in po.lines:
            line_dict = to_dict(line)
            line_dict['product_name'] = line.product.name if line.product else None
            lines.append(line_dict)
        po_dict['lines'] = lines
        result.append(po_dict)
    return result

def get_purchase_order_by_id(db: Session, purchase_order_identifier: str):
    # Try to parse as UUID
    try:
        import uuid
        uuid.UUID(purchase_order_identifier)
        # If valid UUID, query by id
        po = db.query(PurchaseOrder).filter(PurchaseOrder.id == purchase_order_identifier).first()
    except ValueError:
        # If not UUID, query by po_no
        po = db.query(PurchaseOrder).filter(PurchaseOrder.po_no == purchase_order_identifier).first()
    
    if not po:
        return None
    po_dict = to_dict(po)
    po_dict['supplier_name'] = po.supplier.nama if po.supplier else None
    lines = []
    for line in po.lines:
        line_dict = to_dict(line)
        line_dict['product_name'] = line.product.name if line.product else None
        lines.append(line_dict)
    po_dict['lines'] = lines
    return po_dict

def delete_purchase_order(db: Session, purchase_order_id: str):
    try:
        po = db.query(PurchaseOrder).filter(PurchaseOrder.id == purchase_order_id).first()
        if not po:
            return {"message": "PurchaseOrder not found"}

        # Delete lines first
        for line in po.lines:
            db.delete(line)

        db.delete(po)
        db.commit()
        return {"message": "PurchaseOrder deleted successfully"}
    except IntegrityError:
        db.rollback()
        return {"message": "Error deleting PurchaseOrder"}

def update_purchase_order(db: Session, purchase_order_id: str, data: UpdatePurchaseOrder):
    try:
        po = db.query(PurchaseOrder).filter(PurchaseOrder.id == purchase_order_id).first()
        if not po:
            return {"message": "PurchaseOrder not found"}

        # Store old status for comparison
        old_status = po.status

        # Update fields
        if data.supplier_id:
            po.supplier_id = data.supplier_id
        if data.date:
            po.date = datetime.date.fromisoformat(data.date)
        if data.pajak is not None:
            po.pajak = data.pajak
        if data.pembayaran is not None:
            po.pembayaran = data.pembayaran
        if data.dp is not None:
            po.dp = data.dp
        if data.status_pembayaran:
            po.status_pembayaran = data.status_pembayaran
        if data.status:
            po.status = data.status
        if data.bukti_transfer:
            po.bukti_transfer = data.bukti_transfer
        po.updated_at = datetime.datetime.now()

        # Update lines if provided
        if data.lines is not None:
            # Delete old lines
            for line in po.lines:
                db.delete(line)
            # Add new lines
            for line_data in data.lines:
                line = PurchaseOrderLine(
                    purchase_order_id=po.id,
                    product_id=line_data.product_id,
                    quantity=line_data.quantity,
                    price=line_data.price,
                    discount=line_data.discount,
                    subtotal=line_data.subtotal
                )
                db.add(line)
            # Recalculate total
            po.total = sum(line.subtotal for line in data.lines)

        db.commit()
        db.refresh(po)

        # If status changed to 'diterima', call productMovedHistoryNew with type 'income'
        old_status_value = _status_value(old_status)
        status_value = _status_value(po.status)
        if old_status_value != 'diterima' and status_value == 'diterima':
            for line in po.lines:
                move_data = CreateProductMovedHistory(
                    product_id=line.product_id,
                    type='income',
                    quantity=line.quantity,
                    performed_by='system',
                    notes=f'Purchase order {po.po_no} received',
                    timestamp=datetime.datetime.now()
                )
                createProductMoveHistoryNew(db, move_data)

        return to_dict(po)
    except IntegrityError:
        db.rollback()
        return {"message": "Error updating PurchaseOrder"}

def update_purchase_order_status(db: Session, purchase_order_id: str, status: str, created_by: str = None):
    try:
        po = db.query(PurchaseOrder).filter(PurchaseOrder.id == purchase_order_id).first()
        if not po:
            return {"message": "PurchaseOrder not found"}

        # Store old status for comparison
        old_status = po.status

        if status:
            po.status = status

        po.updated_at = datetime.datetime.now()

        db.commit()
        db.refresh(po)

        # If status changed to 'diterima', call productMovedHistoryNew with type 'income'
        old_status_value = _status_value(old_status)
        status_value = _status_value(po.status)
        if old_status_value != 'diterima' and status_value == 'diterima':
            for line in po.lines:
                move_data = CreateProductMovedHistory(
                    product_id=line.product_id,
                    type='income',
                    quantity=line.quantity,
                    performed_by=created_by or 'system',
                    notes=f'Purchase order {po.po_no} received',
                    timestamp=datetime.datetime.now()
                )
                createProductMoveHistoryNew(db, move_data)

        return to_dict(po)
    except IntegrityError:
        db.rollback()
        return {"message": "Error updating PurchaseOrder status"}

def edit_purchase_order(db: Session, purchase_order_id: str, data: UpdatePurchaseOrder):
    try:
        print(f"Starting edit_purchase_order for ID: {purchase_order_id}")
        po = db.query(PurchaseOrder).filter(PurchaseOrder.id == purchase_order_id).first()
        if not po:
            print(f"PurchaseOrder not found: {purchase_order_id}")
            return {"message": "PurchaseOrder not found"}

        # Store old status for comparison
        old_status = po.status
        lines_changed = data.lines is not None
        status_value = str(po.status)
        old_lines = list(po.lines) if lines_changed and status_value == 'diterima' else None

        print(f"Old status: {old_status}, New status: {data.status if data.status else 'unchanged'}")
        print(f"Lines changed: {lines_changed}, Old lines count: {len(old_lines) if old_lines else 0}")

        # Update fields
        if data.supplier_id:
            po.supplier_id = data.supplier_id
        if data.date:
            po.date = data.date
        if data.pajak is not None:
            po.pajak = data.pajak
        if data.pembayaran is not None:
            po.pembayaran = data.pembayaran
        if data.dp is not None:
            po.dp = data.dp
        if data.status_pembayaran:
            po.status_pembayaran = data.status_pembayaran
        if data.status:
            po.status = data.status
        if data.bukti_transfer:
            po.bukti_transfer = data.bukti_transfer
        
        po.updated_at = datetime.datetime.now()

        db.flush()
        db.commit()
        db.refresh(po)
        print("Database commit successful")
        print(f" purchase order id: {po.id}")
        # If status changed to 'diterima', call productMovedHistoryNew with type 'income' and create purchase journal entry
        old_status_value = _status_value(old_status)
        status_value = _status_value(data.status) if data.status is not None else old_status_value
        if old_status_value != 'diterima' and status_value == 'diterima':
            print("Status changed to 'diterima', creating product moves, calculating average cost, and journal entry")
            for line in po.lines:
                # Create product move history
                move_data = CreateProductMovedHistory(
                    product_id=line.product_id,
                    type='income',
                    quantity=line.quantity,
                    performed_by='system',
                    notes=f'Purchase order {po.po_no} received',
                    timestamp=datetime.datetime.now()
                )
                logger.info(f"Creating product move: {move_data.product_id}, type: {move_data.type}, quantity: {move_data.quantity}")
                hasil_create_move = createProductMoveHistoryNew(db, move_data)
                print(f"hasil moving : {hasil_create_move}")
                
                # Calculate average cost for the product
                try:
                    cost_result = calculate_average_cost(
                        db=db,
                        product_id=str(line.product_id),
                        purchase_quantity=line.quantity,
                        purchase_price=line.price,
                        created_by='system',
                        notes=f'Purchase order {po.po_no} received'
                    )
                    logger.info(f"Average cost calculation result: {cost_result}")
                    print(f"Average cost calculated: {cost_result}")
                except Exception as e:
                    logger.error(f"Error calculating average cost: {str(e)}")
                    print(f"Error calculating average cost: {str(e)}")
                    # Continue with other operations even if costing fails

                # Update cost using the new function
                try:
                    update_result = updateCostCostingMethodeAverage(
                        db=db,
                        dataPurchase=PurchaseOrderUpdateCost(
                            product_id=line.product_id,
                            quantity=line.quantity,
                            price=line.price
                        )
                    )
                    logger.info(f"Cost update result: {update_result}")
                    print(f"Cost updated: {update_result}")
                except Exception as e:
                    logger.error(f"Error updating cost: {str(e)}")
                    print(f"Error updating cost: {str(e)}")
                    # Continue with other operations even if cost update fails

            # Create purchase journal entry
            journal_data = PurchaseJournalEntry(
                date=po.date,
                memo=f'Purchase order {po.po_no} received',
                supplier_id=po.supplier_id,
                purchase_id=po.id,
                harga_product=po.total,
                pajak=po.pajak
            )
            print(f"Creating journal entry: {journal_data.memo}, total: {journal_data.harga_product}")
            print(f"po.id: {po.id}, type: {type(po.id)}")
            print(f"po.id is None: {po.id is None}")

            hasil_create_purchase = create_purchase_journal_entry(db, journal_data)
            print(f"hasil create : {hasil_create_purchase}")

        logger.info(f"edit_purchase_order completed successfully for ID: {purchase_order_id}")
        return to_dict(po)
    except IntegrityError as e:
        logger.error(f"IntegrityError in edit_purchase_order: {str(e)}")
        db.rollback()
        return {"message": f"IntegrityError: {str(e)}"}
    except Exception as e:
        logger.error(f"Unexpected error in edit_purchase_order: {str(e)}")
        db.rollback()
        return {"message": f"Unexpected error: {str(e)}"}

def update_purchase_order_line(db: Session, line_id: str, data: UpdatePurchaseOrderLineSingle):
    try:
        line = db.query(PurchaseOrderLine).filter(PurchaseOrderLine.id == line_id).first()
        if not line:
            return {"message": "PurchaseOrderLine not found"}

        # Update fields
        line.product_id = data.product_id
        line.quantity = data.quantity
        line.price = data.price
        line.discount = data.discount
        discount = data.discount or Decimal("0")
        line.subtotal = (data.quantity * data.price) - discount

        # Update PO total
        po = line.purchase_order
        po.total = sum(l.subtotal for l in po.lines)
        po.updated_at = datetime.datetime.now()

        db.commit()
        db.refresh(line)
        db.refresh(po)

        return to_dict(line)
    except IntegrityError:
        db.rollback()
        return {"message": "Error updating PurchaseOrderLine"}

def add_purchase_order_line(db: Session, purchase_order_id: str, data: CreatePurchaseOrderLineSingle):
    try:
        po = db.query(PurchaseOrder).filter(PurchaseOrder.id == purchase_order_id).first()
        if not po:
            return {"message": "PurchaseOrder not found"}

        # Create new line
        discount = data.discount or Decimal("0")
        subtotal = (data.quantity * data.price) - discount
        line = PurchaseOrderLine(
            id=uuid.uuid4(),
            purchase_order_id=purchase_order_id,
            product_id=data.product_id,
            quantity=data.quantity,
            price=data.price,
            discount=data.discount,
            subtotal=subtotal
        )
        db.add(line)

        # Update PO total
        po.total = sum(l.subtotal for l in po.lines) + subtotal
        po.updated_at = datetime.datetime.now()

        db.commit()
        db.refresh(line)
        db.refresh(po)

        return to_dict(line)
    except IntegrityError:
        db.rollback()
        return {"message": "Error adding PurchaseOrderLine"}

def delete_purchase_order_line(db: Session, line_id: str):
    try:
        line = db.query(PurchaseOrderLine).filter(PurchaseOrderLine.id == line_id).first()
        if not line:
            return {"message": "PurchaseOrderLine not found"}

        # Update PO total before deleting
        po = line.purchase_order
        po.total = sum(l.subtotal for l in po.lines if l.id != line_id)
        po.updated_at = datetime.datetime.now()

        db.delete(line)
        db.commit()

        return {"message": "PurchaseOrderLine deleted successfully"}
    except IntegrityError:
        db.rollback()
        return {"message": "Error deleting PurchaseOrderLine"}
    
def update_only_status_purchase_order(db: Session, purchase_id: str):
    try:

        po = db.query(PurchaseOrder).filter(PurchaseOrder.id == purchase_id).first()
        if not po:
            return {"message": "PurchaseOrder not found"}

        po.status = 'dibayarkan'
        po.status_pembayaran = 'lunas'
        po.updated_at = datetime.datetime.now()

        db.commit()
        db.refresh(po)

        return to_dict(po)
    except IntegrityError:
        db.rollback()
        return {"message": "Error updating PurchaseOrder status"}
    except Exception as e:
        db.rollback()
        return {"message": f"Unexpected error: {str(e)}"}

def getPurchaseOrdersBySupplierID(db: Session, supplier_id: str):
    purchase_orders = db.query(PurchaseOrder).filter(PurchaseOrder.supplier_id == supplier_id).order_by(PurchaseOrder.date.desc()).all()
    result = []
    for po in purchase_orders:
        po_dict = to_dict(po)
        po_dict['supplier_name'] = po.supplier.nama if po.supplier else None
        lines = []
        for line in po.lines:
            line_dict = to_dict(line)
            line_dict['product_name'] = line.product.name if line.product else None
            lines.append(line_dict)
        po_dict['lines'] = lines
        result.append(po_dict)
    return result

def get_purchase_order_status_pembayaran(db: Session, purchase_order_id: str):
    po = db.query(PurchaseOrder).filter(PurchaseOrder.id == purchase_order_id).first()
    if not po:
        return None
    return {"status_pembayaran": po.status_pembayaran}



