from schemas.service_workorder_update import UpdateWorkorderOrders, UpdateProductOrder, UpdateServiceOrder
from schemas.service_workorder import CreateWorkorderOnly
from schemas.service_inventory import CreateProductMovedHistory
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

def CreateProductNew(db:Session, product_data: CreateProduct):
    new_product = Product(
        id=str(uuid.uuid4()),
        name=product_data.name,
        type=product_data.type,
        description=product_data.description,
        price=product_data.price,
        min_stock=product_data.min_stock,
        brand_id=product_data.brand_id,
        satuan_id=product_data.satuan_id,
        category_id=product_data.category_id
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
        total_stock = sum(inv.quantity for inv in product.inventory) if product.inventory else 0
        p_dict['total_stock'] = float(total_stock)  # Konversi Decimal ke float
        result.append(p_dict)
    return result

def getInventoryByProductID(db: Session, product_id: str):
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        return None
    p_dict = to_dict(product)
    p_dict['category_name'] = product.category.name if product.category else None
    p_dict['brand_name'] = product.brand.name if product.brand else None
    p_dict['satuan_name'] = product.satuan.name if product.satuan else None
    # Hitung total stock dari inventory
    total_stock = sum(inv.stock for inv in product.inventory) if product.inventory else 0
    p_dict['total_stock'] = float(total_stock)  # Konversi Decimal ke float
    return p_dict

def createProductMoveHistoryNew(db: Session, move_data: CreateProductMovedHistory):
    inventory = db.query(Inventory).filter(Inventory.product_id == move_data.product_id).first()
    if move_data.type.lower() == 'income':
        if not inventory:
            # Buat inventory baru
            inventory = Inventory(
                id=str(uuid.uuid4()),
                product_id=move_data.product_id,
                quantity=move_data.quantity,
                cost=0,
                created_at=move_data.timestamp or datetime.utcnow(),
                updated_at=move_data.timestamp or datetime.utcnow()
            )
            db.add(inventory)
        else:
            # Update quantity lama + quantity baru
            inventory.quantity += move_data.quantity
            inventory.updated_at = move_data.timestamp or datetime.utcnow()
    elif move_data.type.lower() == 'outcome':
        if not inventory:
            raise ValueError('Inventory untuk produk ini belum ada, tidak bisa outcome!')
        if inventory.quantity < move_data.quantity:
            raise ValueError('Stock tidak cukup untuk outcome!')
        inventory.quantity -= move_data.quantity
        inventory.updated_at = move_data.timestamp or datetime.utcnow()
    # Catat ke ProductMovedHistory
    new_move = ProductMovedHistory(
        id=str(uuid.uuid4()),
        product_id=move_data.product_id,
        type=move_data.type,
        quantity=move_data.quantity,
        performed_by=move_data.performed_by,
        notes=move_data.notes,
        timestamp=move_data.timestamp or datetime.utcnow()
    )
    db.add(new_move)
    db.commit()
    db.refresh(new_move)
    return to_dict(new_move)



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
        createProductMoveHistoryNew(db, move_data)

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
            createProductMoveHistoryNew(db, move_data)

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

def createBrand(db: Session, brand_name: str):
    new_brand = Brand(
        id=str(uuid.uuid4()),
        name=brand_name
    )
    db.add(new_brand)
    db.commit()
    db.refresh(new_brand)
    return to_dict(new_brand)

def createCategory(db: Session, category_name: str):
    new_category = Category(
        id=str(uuid.uuid4()),
        name=category_name
    )
    db.add(new_category)
    db.commit()
    db.refresh(new_category)
    return to_dict(new_category)

def createSatuan(db: Session, satuan_name: str):
    new_satuan = Satuan(
        id=str(uuid.uuid4()),
        name=satuan_name
    )
    db.add(new_satuan)
    db.commit()
    db.refresh(new_satuan)
    return to_dict(new_satuan)

def getAllBrands(db: Session):
    brands = db.query(Brand).all()
    result = [to_dict(brand) for brand in brands]
    return result

def getAllSatuans(db: Session):
    satuans = db.query(Satuan).all()
    result = [to_dict(satuan) for satuan in satuans]
    return result

def getAllCategories(db: Session):
    categories = db.query(Category).all()
    result = [to_dict(category) for category in categories]
    return result







