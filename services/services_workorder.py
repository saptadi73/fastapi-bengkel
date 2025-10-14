from schemas.service_workorder_update import UpdateWorkorderOrders, UpdateProductOrder, UpdateServiceOrder
from schemas.service_workorder import CreateWorkOrder,CreateServiceOrder,CreateProductOrder, CreateWorkorderOnly, CreateProductOrderedOnly, CreateServiceOrderedOnly, UpdateWorkorderComplaint, AddProductOrderById, UpdateProductOrderById, DeleteProductOrderById, AddServiceOrderById, UpdateServiceOrderById, DeleteServiceOrderById
from schemas.service_inventory import CreateProductMovedHistory
from models.inventory import Inventory, ProductMovedHistory
from sqlalchemy.exc import IntegrityError
from datetime import datetime
from sqlalchemy.orm import Session
from models.workorder import Product, Brand, Satuan, Category, Service, Workorder, ProductOrdered, ServiceOrdered
import uuid
from models.database import get_db
from schemas.service_product import CreateProduct, ProductResponse, BrandResponse, SatuanResponse, CategoryResponse, CreateService, ServiceResponse
from services.services_product import createProductMoveHistoryNew, EditProductMovedHistory, deleteProductMovedHistory, createProductMoveHistoryNew
import decimal
import datetime
from collections.abc import Iterable

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


def createNewWorkorder(db: Session, workorder_data: CreateWorkOrder):


    # Generate nomor workorder otomatis: WO-YYYYMM-XXXX (increment, tidak error jika ada yang terhapus)
    today = datetime.datetime.now()
    prefix = f"WO-{today.year}{today.month:02d}-"
    # Ambil nomor terbesar bulan ini
    last_wo = db.query(Workorder).filter(Workorder.no_wo.like(f"{prefix}%")).order_by(Workorder.no_wo.desc()).first()
    if last_wo and last_wo.no_wo[-4:].isdigit():
        last_num = int(last_wo.no_wo[-4:])
        next_num = last_num + 1
    else:
        next_num = 1
    auto_no_wo = f"{prefix}{next_num:04d}"

    workorder = Workorder(
        id=uuid.uuid4(),
        no_wo=auto_no_wo,
        tanggal_masuk=workorder_data.tanggal_masuk,
        tanggal_keluar=workorder_data.tanggal_keluar,
        keluhan=workorder_data.keluhan,
        saran=workorder_data.saran,
        status=workorder_data.status,
        total_discount=workorder_data.total_discount,
        total_biaya=workorder_data.total_biaya,
        customer_id=workorder_data.customer_id,
        karyawan_id=workorder_data.karyawan_id,
        vehicle_id=workorder_data.vehicle_id,
        pajak=workorder_data.pajak
    )
    db.add(workorder)
    db.flush()  # Agar workorder.id tersedia

    # Tambahkan ProductOrdered jika ada
    if workorder_data.product_ordered:
        for prod in workorder_data.product_ordered:
            product_ordered = ProductOrdered(
                id=uuid.uuid4(),
                product_id=prod.product_id,
                quantity=prod.quantity,
                subtotal=prod.subtotal,
                price=prod.price,
                satuan_id=prod.satuan_id,
                discount=prod.discount,
                workorder_id=workorder.id
            )
            db.add(product_ordered)

    # Tambahkan ServiceOrdered jika ada
    if workorder_data.service_ordered:
        for srv in workorder_data.service_ordered:
            service_ordered = ServiceOrdered(
                id=uuid.uuid4(),
                service_id=srv.service_id,
                quantity=srv.quantity,
                price=srv.price,
                subtotal=srv.subtotal,
                discount=srv.discount,
                workorder_id=workorder.id
            )
            db.add(service_ordered)

    db.commit()
    db.refresh(workorder)
    return to_dict(workorder)


def ProductMovedCausedProductOrdered(db: Session, product_ordered, performed_by: str = 'system'):
    # Cek apakah product_ordered iterable (list/tuple/set), tapi bukan string/bytes
    
    if isinstance(product_ordered, Iterable) and not isinstance(product_ordered, (str, bytes)):
        for po in product_ordered:
            move_data = CreateProductMovedHistory(
                product_id=po.product_id,
                type='outcome',
                quantity=po.quantity,
                performed_by=performed_by,
                notes=f"Product ordered in Workorder {po.workorder_id}",
                timestamp=datetime.datetime.now(datetime.timezone.utc)
            )
            createProductMoveHistoryNew(db, move_data)
    else:
        po = product_ordered
        move_data = CreateProductMovedHistory(
            product_id=po.product_id,
            type='outcome',
            quantity=po.quantity,
            performed_by=performed_by,
            notes=f"Product ordered in Workorder {po.workorder_id}",
            timestamp=datetime.datetime.now(datetime.timezone.utc)
        )
        createProductMoveHistoryNew(db, move_data)


def getAllWorkorders(db: Session):
    workorders = db.query(Workorder).all()
    result = []
    for wo in workorders:
        wo_dict = to_dict(wo)
        wo_dict['customer_name'] = wo.customer.nama if wo.customer else None
        wo_dict['vehicle_no_pol'] = wo.vehicle.no_pol if wo.vehicle else None
        wo_dict['karyawan_name'] = wo.karyawan.nama if wo.karyawan else None
        wo_dict['vehicle_model'] = wo.vehicle.model if wo.vehicle else None
        wo_dict['vehicle_brand'] = wo.vehicle.brand.name if wo.vehicle else None
        wo_dict['vehicle_color'] = wo.vehicle.warna if wo.vehicle else None
        wo_dict['customer_hp'] = wo.customer.hp if wo.customer else None

        # Tambahkan detail product_ordered
        product_ordered_list = []
        for po in wo.product_ordered:
            po_dict = to_dict(po)
            # Tambahkan info produk jika perlu
            if po.product:
                po_dict['product_name'] = po.product.name
            product_ordered_list.append(po_dict)
        wo_dict['product_ordered'] = product_ordered_list

        # Tambahkan detail service_ordered
        service_ordered_list = []
        for so in wo.service_ordered:
            so_dict = to_dict(so)
            # Tambahkan info service jika perlu
            if so.service:
                so_dict['service_name'] = so.service.name
            service_ordered_list.append(so_dict)
        wo_dict['service_ordered'] = service_ordered_list

        result.append(wo_dict)
    return result

def getWorkorderByID(db: Session, workorder_id: str):
    wo = db.query(Workorder).filter(Workorder.id == workorder_id).first()
    if not wo:
        return None

    wo_dict = to_dict(wo)
    wo_dict['customer_name'] = wo.customer.nama if wo.customer else None
    wo_dict['vehicle_no_pol'] = wo.vehicle.no_pol if wo.vehicle else None
    wo_dict['customer_alamat'] = wo.customer.alamat if wo.customer else None
    wo_dict['customer_email'] = wo.customer.email if wo.customer else None
    wo_dict['customer_hp'] = wo.customer.hp if wo.customer else None
    wo_dict['karyawan_name'] = wo.karyawan.nama if wo.karyawan else None
    wo_dict['vehicle_model'] = wo.vehicle.model if wo.vehicle else None
    wo_dict['vehicle_brand'] = wo.vehicle.brand.name if wo.vehicle else None
    wo_dict['vehicle_no_pol'] = wo.vehicle.no_pol if wo.vehicle else None
    wo_dict['vehicle_kapasitas'] = wo.vehicle.kapasitas if wo.vehicle else None
    wo_dict['vehicle_type'] = wo.vehicle.type if wo.vehicle else None

    # Tambahkan detail product_ordered
    product_ordered_list = []
    for po in wo.product_ordered:
        po_dict = to_dict(po)
        # Tambahkan info produk jika perlu
        if po.product:
            po_dict['product_name'] = po.product.name
        product_ordered_list.append(po_dict)
    wo_dict['product_ordered'] = product_ordered_list

    # Tambahkan detail service_ordered
    service_ordered_list = []
    for so in wo.service_ordered:
        so_dict = to_dict(so)
        # Tambahkan info service jika perlu
        if so.service:
            so_dict['service_name'] = so.service.name
        service_ordered_list.append(so_dict)
    wo_dict['service_ordered'] = service_ordered_list

    return wo_dict

# --- Tambahkan helper ini di services_workorder.py (mis. di atas updateStatusWorkorder) ---
def _wo_stock_already_moved(db: Session, wo_id: str) -> bool:
    """
    Cek apakah riwayat pergerakan stok untuk WO ini sudah pernah dibuat
    (berdasarkan pola 'WO:{wo_id}' di kolom notes ProductMovedHistory).
    """
    exists = db.query(ProductMovedHistory.id).filter(
        ProductMovedHistory.notes.ilike(f"%WO:{wo_id}%")
    ).first()
    return exists is not None


# --- Gantikan fungsi updateStatusWorkorder dengan versi yang memproses stok saat complete ---
def updateStatusWorkorder(db: Session, workorder_id: str, new_status: str, performed_by: str = 'system'):
    wo = db.query(Workorder).filter(Workorder.id == workorder_id).first()
    if not wo:
        return None

    old_status = wo.status
    wo.status = new_status
    db.add(wo)

    

    # === Jika status menjadi COMPLETE, pindahkan stok sesuai ProductOrdered ===
    if (old_status or "").lower() != "selesai" and (new_status or "").lower() == "selesai":
        # Hindari dobel jika fungsi ini terpanggil dua kali (idempotent)
        if not _wo_stock_already_moved(db, str(wo.id)):
            for po in wo.product_ordered:
                # Catatan memakai jejak 'WO:{wo.id}' agar _wo_stock_already_moved bisa mendeteksi
                move_data = CreateProductMovedHistory(
                    product_id=po.product_id,
                    type='outcome',
                    quantity=po.quantity,
                    performed_by=performed_by,
                    notes=f"WO:{wo.id} ({wo.no_wo}) complete → deduct for ProductOrdered:{po.id}",
                    timestamp=datetime.datetime.now(datetime.timezone.utc)
                )
                # Utilitas ini akan:
                # - membuat riwayat ProductMovedHistory
                # - update Inventory.quantity sesuai akumulasi history
                createProductMoveHistoryNew(db, move_data)

           
        # else: sudah pernah dipindah—diamkan agar tidak minus dobel

    db.commit()
    db.refresh(wo)

    # Susun response (konsisten dengan fungsi-fungsi lain)
    wo_dict = to_dict(wo)
    wo_dict['customer_name']   = wo.customer.nama if wo.customer else None
    wo_dict['vehicle_no_pol']  = wo.vehicle.no_pol if wo.vehicle else None

    product_ordered_list = []
    for po in wo.product_ordered:
        po_dict = to_dict(po)
        if po.product:
            po_dict['product_name'] = po.product.name
        product_ordered_list.append(po_dict)
    wo_dict['product_ordered'] = product_ordered_list

    service_ordered_list = []
    for so in wo.service_ordered:
        so_dict = to_dict(so)
        if so.service:
            so_dict['service_name'] = so.service.name
        service_ordered_list.append(so_dict)
    wo_dict['service_ordered'] = service_ordered_list

    return wo_dict


def UpdateDateWorkordernya(db: Session, workorder_id: str, new_tanggal_keluar: datetime.datetime, performed_by: str = 'system'):
    wo = db.query(Workorder).filter(Workorder.id == workorder_id).first()
    if not wo:
        return None

    old_tanggal_keluar = wo.tanggal_keluar
    wo.tanggal_keluar = new_tanggal_keluar
    db.add(wo)

    

    db.commit()
    db.refresh(wo)

    wo_dict = to_dict(wo)
    wo_dict['customer_name'] = wo.customer.nama if wo.customer else None
    wo_dict['vehicle_no_pol'] = wo.vehicle.no_pol if wo.vehicle else None

    # Tambahkan detail product_ordered
    product_ordered_list = []
    for po in wo.product_ordered:
        po_dict = to_dict(po)
        # Tambahkan info produk jika perlu
        if po.product:
            po_dict['product_name'] = po.product.name
        product_ordered_list.append(po_dict)
    wo_dict['product_ordered'] = product_ordered_list

    # Tambahkan detail service_ordered
    service_ordered_list = []
    for so in wo.service_ordered:
        so_dict = to_dict(so)
        # Tambahkan info service jika perlu
        if so.service:
            so_dict['service_name'] = so.service.name
        service_ordered_list.append(so_dict)
    wo_dict['service_ordered'] = service_ordered_list
    return wo_dict

def updateWorkOrdeKeluhannya(db: Session, workorder_id: str, data: UpdateWorkorderComplaint):
    wo = db.query(Workorder).filter(Workorder.id == workorder_id).first()
    if not wo:
        return None

    old_keluhan = wo.keluhan
    wo.keluhan = data['keluhan']
    db.add(wo)

    # Log perubahan keluhan
    

    db.commit()
    db.refresh(wo)

    wo_dict = to_dict(wo)
    wo_dict['customer_name'] = wo.customer.nama if wo.customer else None
    wo_dict['vehicle_no_pol'] = wo.vehicle.no_pol if wo.vehicle else None

    # Tambahkan detail product_ordered
    product_ordered_list = []
    for po in wo.product_ordered:
        po_dict = to_dict(po)
        # Tambahkan info produk jika perlu
        if po.product:
            po_dict['product_name'] = po.product.name
        product_ordered_list.append(po_dict)
    wo_dict['product_ordered'] = product_ordered_list

    # Tambahkan detail service_ordered
    service_ordered_list = []
    for so in wo.service_ordered:
        so_dict = to_dict(so)
        # Tambahkan info service jika perlu
        if so.service:
            so_dict['service_name'] = so.service.name
        service_ordered_list.append(so_dict)
    wo_dict['service_ordered'] = service_ordered_list
    return wo_dict

def UpdateWorkorderOrdersnya(db: Session, workorder_id: str, update_data: CreateWorkOrder, performed_by: str = 'system'):
    wo = db.query(Workorder).filter(Workorder.id == workorder_id).first()
    if not wo:
        return None

    # Sinkronisasi ProductOrdered
    if update_data.product_ordered is not None:
        # Collect set of ids dari list baru yang memiliki id
        new_po_ids = set()
        for prod in update_data.product_ordered:
            if prod.id:
                new_po_ids.add(prod.id)

        # Update atau Add berdasarkan id jika ada, atau product_id
        for prod in update_data.product_ordered:
            if prod.id:
                # Update berdasarkan id
                po = db.query(ProductOrdered).filter(ProductOrdered.id == prod.id, ProductOrdered.workorder_id == workorder_id).first()
                if po:
                    po.product_id = prod.product_id
                    po.quantity = prod.quantity
                    po.price = prod.price
                    po.subtotal = prod.subtotal
                    po.discount = prod.discount
                    po.satuan_id = getattr(prod, 'satuan_id', None)
                    db.add(po)
            else:
                # Cari berdasarkan product_id, jika ada update, jika tidak add
                po = db.query(ProductOrdered).filter(ProductOrdered.workorder_id == workorder_id, ProductOrdered.product_id == prod.product_id).first()
                if po:
                    po.quantity = prod.quantity
                    po.price = prod.price
                    po.subtotal = prod.subtotal
                    po.discount = prod.discount
                    po.satuan_id = getattr(prod, 'satuan_id', None)
                    db.add(po)
                else:
                    new_po = ProductOrdered(
                        id=uuid.uuid4(),
                        workorder_id=workorder_id,
                        product_id=prod.product_id,
                        quantity=prod.quantity,
                        price=prod.price,
                        subtotal=prod.subtotal,
                        discount=prod.discount,
                        satuan_id=getattr(prod, 'satuan_id', None)
                    )
                    db.add(new_po)

        # Delete ProductOrdered yang id-nya tidak ada di new_po_ids
        for po in list(wo.product_ordered):
            if po.id not in new_po_ids:
                db.delete(po)

    # Sinkronisasi ServiceOrdered
    if update_data.service_ordered is not None:
        # Collect set of ids dari list baru yang memiliki id
        new_so_ids = set()
        for srv in update_data.service_ordered:
            if srv.id:
                new_so_ids.add(srv.id)

        # Update atau Add berdasarkan id jika ada, atau service_id
        for srv in update_data.service_ordered:
            if srv.id:
                # Update berdasarkan id
                so = db.query(ServiceOrdered).filter(ServiceOrdered.id == srv.id, ServiceOrdered.workorder_id == workorder_id).first()
                if so:
                    so.service_id = srv.service_id
                    so.quantity = srv.quantity
                    so.price = srv.price
                    so.subtotal = srv.subtotal
                    so.discount = srv.discount
                    db.add(so)
            else:
                # Cari berdasarkan service_id, jika ada update, jika tidak add
                so = db.query(ServiceOrdered).filter(ServiceOrdered.workorder_id == workorder_id, ServiceOrdered.service_id == srv.service_id).first()
                if so:
                    so.quantity = srv.quantity
                    so.price = srv.price
                    so.subtotal = srv.subtotal
                    so.discount = srv.discount
                    so.satuan = getattr(srv, 'satuan', None)
                    db.add(so)
                else:
                    new_so = ServiceOrdered(
                        id=uuid.uuid4(),
                        workorder_id=workorder_id,
                        service_id=srv.service_id,
                        quantity=srv.quantity,
                        price=srv.price,
                        subtotal=srv.subtotal,
                        discount=srv.discount,
                        satuan=getattr(srv, 'satuan', None)
                    )
                    db.add(new_so)

        # Delete ServiceOrdered yang id-nya tidak ada di new_so_ids
        for so in list(wo.service_ordered):
            if so.id not in new_so_ids:
                db.delete(so)

    db.commit()
    db.refresh(wo)

    wo_dict = to_dict(wo)
    wo_dict['customer_name'] = wo.customer.nama if wo.customer else None
    wo_dict['vehicle_no_pol'] = wo.vehicle.no_pol if wo.vehicle else None

def updateServiceorderedOnlynya(db: Session, service_ordered_data: CreateServiceOrderedOnly):
    so = db.query(ServiceOrdered).filter(ServiceOrdered.workorder_id == service_ordered_data.workorder_id, ServiceOrdered.service_id == service_ordered_data.service_id).first()
    if so:
        return None  # Sudah ada, tidak ditambahkan lagi

    new_so = ServiceOrdered(
        id=uuid.uuid4(),
        workorder_id=service_ordered_data.workorder_id,
        service_id=service_ordered_data.service_id,
        quantity=service_ordered_data.quantity,
        subtotal=service_ordered_data.subtotal,
        discount=service_ordered_data.discount
    )
    db.add(new_so)
    db.commit()
    db.refresh(new_so)

    wo = db.query(Workorder).filter(Workorder.id == service_ordered_data.workorder_id).first()
    if not wo:
        return None

    wo_dict = to_dict(wo)
    wo_dict['customer_name'] = wo.customer.nama if wo.customer else None
    wo_dict['vehicle_no_pol'] = wo.vehicle.no_pol if wo.vehicle else None
    return wo_dict

def updateProductOrderedOnlynya(db: Session, product_ordered_data: CreateProductOrderedOnly):
    po = db.query(ProductOrdered).filter(ProductOrdered.workorder_id == product_ordered_data.workorder_id, ProductOrdered.product_id == product_ordered_data.product_id).first()
    if po:
        return None  # Sudah ada, tidak ditambahkan lagi

    new_po = ProductOrdered(
        id=uuid.uuid4(),
        workorder_id=product_ordered_data.workorder_id,
        product_id=product_ordered_data.product_id,
        quantity=product_ordered_data.quantity,
        subtotal=product_ordered_data.subtotal,
        discount=product_ordered_data.discount
    )
    db.add(new_po)
    db.commit()
    db.refresh(new_po)

    wo = db.query(Workorder).filter(Workorder.id == product_ordered_data.workorder_id).first()
    if not wo:
        return None
    wo_dict = to_dict(wo)
    wo_dict['customer_name'] = wo.customer.nama if wo.customer else None
    wo_dict['vehicle_no_pol'] = wo.vehicle.no_pol if wo.vehicle else None
    return wo_dict



def update_only_workorder(db: Session, workorder_id: str, data: CreateWorkorderOnly):
    wo = db.query(Workorder).filter(Workorder.id == workorder_id).first()
    if not wo:
        return None

    wo.tanggal_masuk = data.tanggal_masuk
    wo.tanggal_keluar = data.tanggal_keluar
    wo.keluhan = data.keluhan
    wo.saran = data.saran
    wo.status = data.status
    wo.total_discount = data.total_discount
    wo.total_biaya = data.total_biaya
    wo.customer_id = data.customer_id
    wo.karyawan_id = data.karyawan_id
    wo.vehicle_id = data.vehicle_id
    wo.pajak = data.pajak

    db.add(wo)
    db.commit()
    db.refresh(wo)
    wo_dict = to_dict(wo)
    return wo_dict

def update_only_productordered(db: Session, product_ordered_id: str, data: CreateProductOrderedOnly):
    po = db.query(ProductOrdered).filter(ProductOrdered.id == product_ordered_id).first()
    if not po:
        return None

    po.product_id = data.product_id
    po.quantity = data.quantity
    po.subtotal = data.subtotal
    po.discount = data.discount

    db.add(po)
    db.commit()
    db.refresh(po)

    wo = db.query(Workorder).filter(Workorder.id == po.workorder_id).first()
    if not wo:
        return None

    wo_dict = to_dict(wo)
    return wo_dict

def update_only_serviceordered(db: Session, service_ordered_id: str, data: CreateServiceOrderedOnly):
    so = db.query(ServiceOrdered).filter(ServiceOrdered.id == service_ordered_id).first()
    if not so:
        return None

    so.service_id = data.service_id
    so.quantity = data.quantity
    so.subtotal = data.subtotal
    so.discount = data.discount

    db.add(so)
    db.commit()
    db.refresh(so)

    wo = db.query(Workorder).filter(Workorder.id == so.workorder_id).first()
    if not wo:
        return None

    wo_dict = to_dict(wo)
    return wo_dict

def deleteWorkorder(db: Session, workorder_id: str):
    wo = db.query(Workorder).filter(Workorder.id == workorder_id).first()
    if not wo:
        return None

    # Hapus semua ProductOrdered terkait
    for po in wo.product_ordered:
        db.delete(po)

    # Hapus semua ServiceOrdered terkait
    for so in wo.service_ordered:
        db.delete(so)

    
    
    db.delete(wo)
    db.commit()
    return True

def update_workorder_lengkap(db: Session, workorder_id: str, data: CreateWorkOrder):
    wo = db.query(Workorder).filter(Workorder.id == workorder_id).first()
    if not wo:
        return None

    # Update field utama
    wo.tanggal_masuk = data.tanggal_masuk
    wo.tanggal_keluar = data.tanggal_keluar
    wo.keluhan = data.keluhan
    wo.saran = data.saran
    wo.status = data.status
    wo.total_discount = data.total_discount
    wo.total_biaya = data.total_biaya
    wo.customer_id = data.customer_id
    wo.karyawan_id = data.karyawan_id
    wo.vehicle_id = data.vehicle_id
    wo.pajak = data.pajak
    db.add(wo)
    db.commit()
    db.refresh(wo)
    wo_dict = to_dict(wo)
    wo_dict['customer_name'] = wo.customer.nama if wo.customer else None
    wo_dict['vehicle_no_pol'] = wo.vehicle.no_pol if wo.vehicle else None
    return wo_dict

def addProductOrder(db: Session, data: AddProductOrderById):
    # Create new ProductOrdered
    new_po = ProductOrdered(
        id=uuid.uuid4(),
        workorder_id=data.workorder_id,
        product_id=data.product_id,
        quantity=data.quantity,
        subtotal=data.subtotal,
        discount=data.discount,
        satuan_id=data.satuan_id,
        price=data.price
    )
    db.add(new_po)
    db.commit()
    db.refresh(new_po)

    # Return updated workorder
    wo = db.query(Workorder).filter(Workorder.id == data.workorder_id).first()
    if not wo:
        return None

    wo_dict = to_dict(wo)
    wo_dict['customer_name'] = wo.customer.nama if wo.customer else None
    wo_dict['vehicle_no_pol'] = wo.vehicle.no_pol if wo.vehicle else None
    return wo_dict

def updateProductOrder(db: Session, product_ordered_id: str, data: UpdateProductOrderById):
    po = db.query(ProductOrdered).filter(ProductOrdered.id == product_ordered_id).first()
    if not po:
        return None

    # Update only provided fields
    if data.product_id is not None:
        po.product_id = data.product_id
    if data.quantity is not None:
        po.quantity = data.quantity
    if data.subtotal is not None:
        po.subtotal = data.subtotal
    if data.discount is not None:
        po.discount = data.discount
    if data.satuan_id is not None:
        po.satuan_id = data.satuan_id
    if data.price is not None:
        po.price = data.price

    db.add(po)
    db.commit()
    db.refresh(po)

    # Return updated workorder
    wo = db.query(Workorder).filter(Workorder.id == po.workorder_id).first()
    if not wo:
        return None

    wo_dict = to_dict(wo)
    wo_dict['customer_name'] = wo.customer.nama if wo.customer else None
    wo_dict['vehicle_no_pol'] = wo.vehicle.no_pol if wo.vehicle else None
    return wo_dict

def deleteProductOrder(db: Session, product_ordered_id: str):
    po = db.query(ProductOrdered).filter(ProductOrdered.id == product_ordered_id).first()
    if not po:
        return None

    workorder_id = po.workorder_id
    db.delete(po)
    db.commit()

    # Return updated workorder
    wo = db.query(Workorder).filter(Workorder.id == workorder_id).first()
    if not wo:
        return None

    wo_dict = to_dict(wo)
    wo_dict['customer_name'] = wo.customer.nama if wo.customer else None
    wo_dict['vehicle_no_pol'] = wo.vehicle.no_pol if wo.vehicle else None
    return wo_dict

def addServiceOrder(db: Session, data: AddServiceOrderById):
    # Create new ServiceOrdered
    new_so = ServiceOrdered(
        id=uuid.uuid4(),
        workorder_id=data.workorder_id,
        service_id=data.service_id,
        quantity=data.quantity,
        subtotal=data.subtotal,
        discount=data.discount,
        price=data.price
    )
    db.add(new_so)
    db.commit()
    db.refresh(new_so)

    # Return updated workorder
    wo = db.query(Workorder).filter(Workorder.id == data.workorder_id).first()
    if not wo:
        return None

    wo_dict = to_dict(wo)
    wo_dict['customer_name'] = wo.customer.nama if wo.customer else None
    wo_dict['vehicle_no_pol'] = wo.vehicle.no_pol if wo.vehicle else None
    return wo_dict

def updateServiceOrder(db: Session, service_ordered_id: str, data: UpdateServiceOrderById):
    so = db.query(ServiceOrdered).filter(ServiceOrdered.id == service_ordered_id).first()
    if not so:
        return None

    # Update only provided fields
    if data.service_id is not None:
        so.service_id = data.service_id
    if data.quantity is not None:
        so.quantity = data.quantity
    if data.subtotal is not None:
        so.subtotal = data.subtotal
    if data.discount is not None:
        so.discount = data.discount
    if data.price is not None:
        so.price = data.price

    db.add(so)
    db.commit()
    db.refresh(so)

    # Return updated workorder
    wo = db.query(Workorder).filter(Workorder.id == so.workorder_id).first()
    if not wo:
        return None

    wo_dict = to_dict(wo)
    wo_dict['customer_name'] = wo.customer.nama if wo.customer else None
    wo_dict['vehicle_no_pol'] = wo.vehicle.no_pol if wo.vehicle else None
    return wo_dict

def deleteServiceOrder(db: Session, service_ordered_id: str):
    so = db.query(ServiceOrdered).filter(ServiceOrdered.id == service_ordered_id).first()
    if not so:
        return None

    workorder_id = so.workorder_id
    db.delete(so)
    db.commit()

    # Return updated workorder
    wo = db.query(Workorder).filter(Workorder.id == workorder_id).first()
    if not wo:
        return None

    wo_dict = to_dict(wo)
    wo_dict['customer_name'] = wo.customer.nama if wo.customer else None
    wo_dict['vehicle_no_pol'] = wo.vehicle.no_pol if wo.vehicle else None
    return wo_dict

