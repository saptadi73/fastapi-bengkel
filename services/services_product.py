from schemas.service_workorder_update import UpdateWorkorderOrders, UpdateProductOrder, UpdateServiceOrder
from schemas.service_workorder import CreateWorkorderOnly
from models.inventory import Inventory, ProductMovedHistory
from sqlalchemy.exc import IntegrityError
from datetime import datetime
from sqlalchemy.orm import Session
from models.workorder import Product, Brand, Satuan, Category, Service, Workorder, ProductOrdered, ServiceOrdered, WorkOrderActivityLog
import uuid
from models.database import get_db
from schemas.service_product import CreateProduct, ProductResponse, BrandResponse, SatuanResponse, CategoryResponse, CreateService, ServiceResponse
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

def CreateProduct(db:Session, product_data: CreateProduct):
    new_product = Product(
        id=str(uuid.uuid4()),
        name=product_data.name,
        type=product_data.type,
        description=product_data.description,
        price=product_data.price,
        min_stock=product_data.min_stock,
        brand_id=product_data.brand_id,
        satuan_id=product_data.satuan_id,
        categor_id=product_data.category_id
    )
    db.add(new_product)
    db.commit()
    db.refresh(new_product)
    return to_dict(new_product)

def get_all_products(db: Session):
    products = db.query(Product).all()
    result = []
    for product in products:
        p_dict = to_dict(product)
        p_dict['category_name'] = product.category.name if product.category else None
        p_dict['brand_name'] = product.brand.name if product.brand else None
        p_dict['satuan_name'] = product.satuan.name if product.satuan else None
        result.append(p_dict)
    return result

def get_product_by_id(db: Session, product_id: str):
    product = db.query(Product).filter(Product.id == product_id).first()
    if product:
        p_dict = to_dict(product)
        p_dict['category_name'] = product.category.name if product.category else None
        p_dict['brand_name'] = product.brand.name if product.brand else None
        p_dict['satuan_name'] = product.satuan.name if product.satuan else None
        return p_dict
    return None

def createServie(db: Session, service_data: CreateService):
    new_service = Service(
        id=str(uuid.uuid4()),
        name=service_data.name,
        description=service_data.description,
        price=service_data.price,
        cost=service_data.cost
    )
    db.add(new_service)
    db.commit()
    db.refresh(new_service)
    return to_dict(new_service)

def get_all_services(db: Session):
    services = db.query(Service).all()
    result = [to_dict(service) for service in services]
    return result

def getAllInventoryProducts(db: Session):
    products = db.query(Product).all()
    result = []
    for product in products:
        p_dict = to_dict(product)
        p_dict['category_name'] = product.category.name if product.category else None
        p_dict['brand_name'] = product.brand.name if product.brand else None
        p_dict['satuan_name'] = product.satuan.name if product.satuan else None
        # Hitung total stock dari inventory
        total_stock = sum(inv.stock for inv in product.inventory) if product.inventory else 0
        p_dict['total_stock'] = float(total_stock)  # Konversi Decimal ke float
        result.append(p_dict)
    return result

def createProductMove(db: Session, move_data):
    # move_data: CreateProductMove
    product_id = str(move_data.product_id)
    type_move = move_data.type.lower()
    qty = float(move_data.quantity)
    performed_by = move_data.performed_by
    notes = move_data.notes
    timestamp = move_data.timestamp or datetime.utcnow()

    # Cari inventory untuk produk terkait
    inventory = db.query(Inventory).filter(Inventory.product_id == product_id).first()
    if not inventory:
        if type_move == 'incoming':
            # Buat inventory baru jika belum ada dan incoming
            inventory = Inventory(
                id=str(uuid.uuid4()),
                product_id=product_id,
                quantity=qty,
                cost=0,
                created_at=timestamp,
                updated_at=timestamp
            )
            db.add(inventory)
        else:
            # Tidak bisa outgoing jika inventory tidak ada
            raise ValueError('Inventory untuk produk ini belum ada, tidak bisa outgoing!')
    else:
        if type_move == 'incoming':
            inventory.quantity += qty
        elif type_move == 'outgoing':
            if inventory.quantity < qty:
                raise ValueError('Stock tidak cukup untuk outgoing!')
            inventory.quantity -= qty
        inventory.updated_at = timestamp

    # Catat ke product_moved_history
    moved = ProductMovedHistory(
        id=str(uuid.uuid4()),
        product_id=product_id,
        type=type_move,
        quantity=qty,
        timestamp=timestamp,
        performed_by=performed_by,
        notes=notes
    )
    db.add(moved)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise
    db.refresh(inventory)
    db.refresh(moved)
    return {
        'inventory': to_dict(inventory),
        'move_history': to_dict(moved)
    }

def createWorkorderWithProductsServices(db: Session, workorder_data):
    # workorder_data: CreateWorkorderWithProductsServices
    new_workorder = Workorder(
        id=str(uuid.uuid4()),
        customer_id=workorder_data.customer_id,
        vehicle_id=workorder_data.vehicle_id,
        status='open',
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )
    db.add(new_workorder)
    db.commit()
    db.refresh(new_workorder)

    # Tambah produk yang dipesan dan kurangi stok inventory
    for prod in workorder_data.products:
        product_ordered = ProductOrdered(
            id=str(uuid.uuid4()),
            workorder_id=new_workorder.id,
            product_id=prod.product_id,
            quantity=prod.quantity
        )
        db.add(product_ordered)

        # Jalankan productmove outgoing untuk mengurangi stok
        from schemas.service_product import CreateProductMove
        move_data = CreateProductMove(
            product_id=prod.product_id,
            type='outgoing',
            quantity=prod.quantity,
            performed_by=getattr(workorder_data, 'performed_by', 'system'),
            notes=f'Workorder {new_workorder.id} - ProductOrdered'
        )
        createProductMove(db, move_data)

    # Tambah layanan yang dipesan
    for serv in workorder_data.services:
        service_ordered = ServiceOrdered(
            id=str(uuid.uuid4()),
            workorder_id=new_workorder.id,
            service_id=serv.service_id,
            notes=serv.notes
        )
        db.add(service_ordered)

    # Catat log aktivitas pembuatan workorder
    log_entry = WorkOrderActivityLog(
        id=str(uuid.uuid4()),
        workorder_id=new_workorder.id,
        activity='Workorder created',
        timestamp=datetime.utcnow()
    )
    db.add(log_entry)

    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise

    db.refresh(new_workorder)
    return to_dict(new_workorder)

# ...existing code...

def createWorkorderOnly(db: Session, workorder_data: 'CreateWorkorderOnly'):
    new_workorder = Workorder(
        id=str(uuid.uuid4()),
        customer_id=workorder_data.customer_id,
        vehicle_id=workorder_data.vehicle_id,
        status=getattr(workorder_data, 'status', 'open'),
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )
    db.add(new_workorder)
    db.commit()
    db.refresh(new_workorder)
    # Catat log aktivitas pembuatan workorder
    log_entry = WorkOrderActivityLog(
        id=str(uuid.uuid4()),
        workorder_id=new_workorder.id,
        activity='Workorder created',
        timestamp=datetime.utcnow()
    )
    db.add(log_entry)
    db.commit()
    return to_dict(new_workorder)

# ...existing code...

def updateWorkorderOrders(db: Session, update_data: 'UpdateWorkorderOrders'):
    workorder_id = str(update_data.workorder_id)
    workorder = db.query(Workorder).filter(Workorder.id == workorder_id).first()
    if not workorder:
        raise ValueError('Workorder not found')

    # Update ProductOrdered
    if update_data.products:
        for prod in update_data.products:
            # Cek apakah sudah ada product_ordered untuk workorder ini dan produk ini
            product_ordered = db.query(ProductOrdered).filter_by(workorder_id=workorder_id, product_id=str(prod.product_id)).first()
            if product_ordered:
                # Update quantity
                product_ordered.quantity = prod.quantity
            else:
                # Tambah baru
                product_ordered = ProductOrdered(
                    id=str(uuid.uuid4()),
                    workorder_id=workorder_id,
                    product_id=str(prod.product_id),
                    quantity=prod.quantity
                )
                db.add(product_ordered)
            # Jalankan productmove outgoing untuk update stok
            from schemas.service_product import CreateProductMove
            move_data = CreateProductMove(
                product_id=prod.product_id,
                type='outgoing',
                quantity=prod.quantity,
                performed_by=getattr(update_data, 'performed_by', 'system'),
                notes=f'Update Workorder {workorder_id} - ProductOrdered'
            )
            createProductMove(db, move_data)

    # Update ServiceOrdered
    if update_data.services:
        for serv in update_data.services:
            service_ordered = db.query(ServiceOrdered).filter_by(workorder_id=workorder_id, service_id=str(serv.service_id)).first()
            if service_ordered:
                service_ordered.notes = serv.notes
            else:
                service_ordered = ServiceOrdered(
                    id=str(uuid.uuid4()),
                    workorder_id=workorder_id,
                    service_id=str(serv.service_id),
                    notes=serv.notes
                )
                db.add(service_ordered)

    db.commit()
    return {'workorder_id': workorder_id, 'status': 'updated'}





