from sqlalchemy.exc import IntegrityError
from datetime import datetime
from sqlalchemy.orm import Session
from sqlalchemy import text
from models.purchase_order import PurchaseOrder, PurchaseOrderLine
import uuid
from schemas.service_purchase_order import CreatePurchaseOrder, UpdatePurchaseOrder, CreatePurchaseOrderLine
import decimal
from decimal import Decimal

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

def create_purchase_order(db: Session, data: CreatePurchaseOrder):
    # Calculate total
    total = sum(line.subtotal for line in data.lines)

    # Generate PO number
    result = db.execute(text("SELECT nextval('purchase_order_seq')")).scalar()
    po_no = f"PO{result:03d}"

    # Create PurchaseOrder
    purchase_order = PurchaseOrder(
        po_no=po_no,
        supplier_id=data.supplier_id,
        date=data.date,
        total=total,
        status=data.status,
        bukti_transfer=data.bukti_transfer
    )
    db.add(purchase_order)
    db.flush()  # Get id

    # Create lines
    for line_data in data.lines:
        line = PurchaseOrderLine(
            purchase_order_id=purchase_order.id,
            product_id=line_data.product_id,
            quantity=line_data.quantity,
            price=line_data.price,
            discount=line_data.discount,
            subtotal=line_data.subtotal
        )
        db.add(line)

    db.commit()
    db.refresh(purchase_order)
    return to_dict(purchase_order)

def get_all_purchase_orders(db: Session):
    purchase_orders = db.query(PurchaseOrder).all()
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

def get_purchase_order_by_id(db: Session, purchase_order_id: str):
    po = db.query(PurchaseOrder).filter(PurchaseOrder.id == purchase_order_id).first()
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

        # Update fields
        if data.supplier_id:
            po.supplier_id = data.supplier_id
        if data.date:
            po.date = data.date
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
        return to_dict(po)
    except IntegrityError:
        db.rollback()
        return {"message": "Error updating PurchaseOrder"}
