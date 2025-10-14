from schemas.service_inventory import CreateProductMovedHistory
from models.inventory import Inventory, ProductMovedHistory
from sqlalchemy.exc import IntegrityError
from datetime import datetime
from sqlalchemy.orm import Session
from sqlalchemy import func, select
import uuid
import decimal
import datetime

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


