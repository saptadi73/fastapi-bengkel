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
from schemas.service_product import CreateProduct, ProductResponse, BrandResponse, SatuanResponse, CategoryResponse, CreateService, ServiceResponse, CreateBrand, CreateCategory,CreateSatuan
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

def createServicenya(db: Session, service_data: CreateService):
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

def get_service_by_id(db: Session, service_id: str):
    service = db.query(Service).filter(Service.id == service_id).first()
    if service:
        s_dict = to_dict(service)
        return s_dict

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
    total_stock = sum(inv.quantity for inv in product.inventory) if product.inventory else 0
    p_dict['total_stock'] = float(total_stock)  # Konversi Decimal ke float
    return p_dict

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
                cost=0,
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
        total_quantity = db.query(db.func.sum(ProductMovedHistory.quantity)).filter(ProductMovedHistory.product_id == move_data.product_id).scalar() or 0
        inventory.quantity = total_quantity
        inventory.updated_at = datetime.datetime.now(datetime.timezone.utc)
        db.commit()
        db.refresh(inventory)

    return to_dict(new_move)

def EditProductMovedHistory(db: Session, move_id: str, move_data: CreateProductMovedHistory):
    move_record = db.query(ProductMovedHistory).filter(ProductMovedHistory.id == move_id).first()
    if not move_record:
        raise ValueError('ProductMovedHistory dengan ID tersebut tidak ditemukan!')

    # Simpan nilai lama untuk penyesuaian inventory
    old_type = move_record.type.lower()
    old_quantity = move_record.quantity

    # Update record dengan data baru
    move_record.product_id = move_data.product_id
    move_record.type = move_data.type
    move_record.quantity = move_data.quantity if move_data.type.lower() == 'income' else -move_data.quantity
    move_record.performed_by = move_data.performed_by
    move_record.notes = move_data.notes
    move_record.timestamp = move_data.timestamp or datetime.datetime.now(datetime.timezone.utc)

    # Sesuaikan inventory berdasarkan perubahan
    inventory = db.query(Inventory).filter(Inventory.product_id == move_data.product_id).first()
    if not inventory:
        raise ValueError('Inventory untuk produk ini belum ada, tidak bisa mengedit history!')

    # Setelah update, set inventory.quantity = sum seluruh ProductMovedHistory.quantity untuk product_id terkait
    total_quantity = db.query(db.func.sum(ProductMovedHistory.quantity)).filter(ProductMovedHistory.product_id == move_data.product_id).scalar() or 0
    inventory.quantity = total_quantity
    inventory.updated_at = datetime.datetime.now(datetime.timezone.utc)

    db.commit()
    db.refresh(move_record)
    return to_dict(move_record)

def deleteProductMovedHistory(db: Session, move_id: str):
    move_record = db.query(ProductMovedHistory).filter(ProductMovedHistory.id == move_id).first()
    if not move_record:
        raise ValueError('ProductMovedHistory dengan ID tersebut tidak ditemukan!')
    product_id = move_record.product_id
    db.delete(move_record)
    db.commit()
    # Setelah delete, set inventory.quantity = sum seluruh ProductMovedHistory.quantity untuk product_id terkait
    inventory = db.query(Inventory).filter(Inventory.product_id == product_id).first()  
    if inventory:
        total_quantity = db.query(db.func.sum(ProductMovedHistory.quantity)).filter(ProductMovedHistory.product_id == product_id).scalar() or 0
        inventory.quantity = total_quantity
        inventory.updated_at = datetime.datetime.now(datetime.timezone.utc)
        db.commit()
    return True


def createBrandnya(db: Session, dataBrand: CreateBrand):
    new_brand = Brand(
        id=str(uuid.uuid4()),
        name=dataBrand.name
    )
    db.add(new_brand)
    db.commit()
    db.refresh(new_brand)
    return to_dict(new_brand)

def createCategorynya(db: Session, dataCategory: CreateCategory):
    new_category = Category(
        id=str(uuid.uuid4()),
        name=dataCategory.name
    )
    db.add(new_category)
    db.commit()
    db.refresh(new_category)
    return to_dict(new_category)

def createSatuannya(db: Session, dataSatuan: CreateSatuan):
    new_satuan = Satuan(
        id=str(uuid.uuid4()),
        name=dataSatuan.name
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







