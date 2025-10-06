from schemas.service_workorder_update import UpdateWorkorderOrders, UpdateProductOrder, UpdateServiceOrder
from schemas.service_workorder import CreateWorkOrder,CreateServiceOrder,CreateProductOrder, CreateWorkorderOnly, CreateProductOrderedOnly, CreateServiceOrderedOnly, UpdateWorkorderComplaint, CreateWorkActivityLog
from schemas.service_inventory import CreateProductMovedHistory
from models.inventory import Inventory, ProductMovedHistory
from sqlalchemy.exc import IntegrityError
from datetime import datetime
from sqlalchemy.orm import Session
from models.workorder import Product, Brand, Satuan, Category, Service, Workorder, ProductOrdered, ServiceOrdered, WorkOrderActivityLog
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

    # Log perubahan status (selalu dicatat)
    log_entry = WorkOrderActivityLog(
        id=uuid.uuid4(),
        workorder_id=wo.id,
        activity=f"Status changed from {old_status} to {new_status}",
        performed_by=performed_by,
        timestamp=datetime.datetime.now()
    )
    db.add(log_entry)

    # === Jika status menjadi COMPLETE, pindahkan stok sesuai ProductOrdered ===
    if (old_status or "").lower() != "completed" and (new_status or "").lower() == "completed":
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

            # Tambah log aktivitas khusus perpindahan stok
            db.add(WorkOrderActivityLog(
                id=uuid.uuid4(),
                workorder_id=wo.id,
                activity=f"Stock deducted for all ProductOrdered due to WO COMPLETE (WO:{wo.id})",
                performed_by=performed_by,
                timestamp=datetime.datetime.now()
            ))
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

    # Log perubahan tanggal_keluar
    log_entry = WorkOrderActivityLog(
        id=uuid.uuid4(),
        workorder_id=wo.id,
        activity=f"Tanggal keluar changed from {old_tanggal_keluar} to {new_tanggal_keluar}",
        performed_by=performed_by,
        timestamp=datetime.datetime.now()
    )
    db.add(log_entry)

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
    log_entry = WorkOrderActivityLog(
        id=uuid.uuid4(),
        workorder_id=wo.id,
        activity=f"Keluhan changed from {old_keluhan} to {wo.keluhan}",
        performed_by=data['performed_by'],
        timestamp=datetime.datetime.now()
    )
    db.add(log_entry)

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

    # Update or Add ProductOrdered
    if update_data.product_ordered:
        for prod in update_data.product_ordered:
            po = db.query(ProductOrdered).filter(ProductOrdered.id == prod.id, ProductOrdered.workorder_id == workorder_id).first()
            if po:
                old_price = po.price
                old_quantity = po.quantity
                old_subtotal = po.subtotal
                old_discount = po.discount

                po.price = prod.price
                po.quantity = prod.quantity
                po.subtotal = prod.subtotal
                po.discount = prod.discount
                db.add(po)

                # Log perubahan pada ProductOrdered
                log_entry = WorkOrderActivityLog(
                    id=uuid.uuid4(),
                    workorder_id=wo.id,
                    activity=f"ProductOrdered {po.id} updated: quantity {old_quantity} -> {prod.quantity}, subtotal {old_subtotal} -> {prod.subtotal}, discount {old_discount} -> {prod.discount}, price {old_price} -> {prod.price}",
                    performed_by=performed_by,
                    timestamp=datetime.datetime.now()
                )
                db.add(log_entry)
            else:
                # Tambah baru jika belum ada
                new_po = ProductOrdered(
                    id=uuid.uuid4(),
                    workorder_id=workorder_id,
                    product_id=prod.product_id,
                    quantity=prod.quantity,
                    subtotal=prod.subtotal,
                    discount=prod.discount,
                    price=prod.price,
                    satuan_id=getattr(prod, 'satuan_id', None)
                )
                db.add(new_po)
                # Log penambahan baru
                log_entry = WorkOrderActivityLog(
                    id=uuid.uuid4(),
                    workorder_id=wo.id,
                    activity=f"ProductOrdered {new_po.id} created: quantity {prod.quantity}, subtotal {prod.subtotal}, discount {prod.discount}, price {prod.price}",
                    performed_by=performed_by,
                    timestamp=datetime.datetime.now()
                )
                db.add(log_entry)

    # Update or Add ServiceOrdered
    if update_data.service_ordered:
        for srv in update_data.service_ordered:
            so = db.query(ServiceOrdered).filter(ServiceOrdered.id == srv.id, ServiceOrdered.workorder_id == workorder_id).first()
            if so:
                old_quantity = so.quantity
                old_subtotal = so.subtotal
                old_discount = so.discount

                so.quantity = srv.quantity
                so.subtotal = srv.subtotal
                so.discount = srv.discount
                if hasattr(so, 'price'):
                    so.price = srv.price
                db.add(so)

                # Log perubahan pada ServiceOrdered
                log_entry = WorkOrderActivityLog(
                    id=uuid.uuid4(),
                    workorder_id=wo.id,
                    activity=f"ServiceOrdered {so.id} updated: quantity {old_quantity} -> {srv.quantity}, subtotal {old_subtotal} -> {srv.subtotal}, discount {old_discount} -> {srv.discount}, price {getattr(so, 'price', None)} -> {getattr(srv, 'price', None)}",
                    performed_by=performed_by,
                    timestamp=datetime.datetime.now()
                )
                db.add(log_entry)
            else:
                # Tambah baru jika belum ada
                new_so = ServiceOrdered(
                    id=uuid.uuid4(),
                    workorder_id=workorder_id,
                    service_id=srv.service_id,
                    quantity=srv.quantity,
                    subtotal=srv.subtotal,
                    discount=srv.discount,
                    price=getattr(srv, 'price', 0)
                )
                db.add(new_so)
                # Log penambahan baru
                log_entry = WorkOrderActivityLog(
                    id=uuid.uuid4(),
                    workorder_id=wo.id,
                    activity=f"ServiceOrdered {new_so.id} created: quantity {srv.quantity}, subtotal {srv.subtotal}, discount {srv.discount}, price {getattr(srv, 'price', 0)}",
                    performed_by=performed_by,
                    timestamp=datetime.datetime.now()
                )
                db.add(log_entry)

    db.commit()
    db.refresh(wo)

    wo_dict = to_dict(wo)
    wo_dict['customer_name'] = wo.customer.nama if wo.customer else None
    wo_dict['vehicle_no_pol'] = wo.vehicle.no_pol if wo.vehicle else None
    return wo_dict

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

def createNewWorkorderActivityLog(db: Session, log_data: CreateWorkActivityLog):
    wo = db.query(Workorder).filter(Workorder.id == log_data.workorder_id).first()
    if not wo:
        return None

    new_log = WorkOrderActivityLog(
        id=uuid.uuid4(),
        workorder_id=log_data.workorder_id,
        activity=log_data.activity,
        performed_by=log_data.performed_by,
        timestamp=datetime.datetime.now()
    )
    db.add(new_log)
    db.commit()
    db.refresh(new_log)

    wo_dict = to_dict(wo)
    wo_dict['customer_name'] = wo.customer.nama if wo.customer else None
    wo_dict['vehicle_no_pol'] = wo.vehicle.no_pol if wo.vehicle else None
    return wo_dict
def getWorkorderActivityLogs(db: Session, workorder_id: str):
    logs = db.query(WorkOrderActivityLog).filter(WorkOrderActivityLog.workorder_id == workorder_id).order_by(WorkOrderActivityLog.timestamp.desc()).all()
    result = []
    for log in logs:
        log_dict = to_dict(log)
        result.append(log_dict)
    return result

def get_workorder_activitylog_by_customer(db: Session, customer_id: str):
    # Ambil semua workorder milik customer
    workorders = db.query(Workorder).filter(Workorder.customer_id == customer_id).all()
    activity_logs = []
    for wo in workorders:
        logs = db.query(WorkOrderActivityLog).filter(WorkOrderActivityLog.workorder_id == wo.id).all()
        for log in logs:
            log_dict = to_dict(log)
            log_dict['workorder_no_wo'] = wo.no_wo
            activity_logs.append(log_dict)
    return activity_logs

def updateWorkorderActivityLognya(db: Session, log_id: str, data: CreateWorkActivityLog):
    log = db.query(WorkOrderActivityLog).filter(WorkOrderActivityLog.id == log_id).first()
    if not log:
        return None

    old_activity = log.activity
    log.activity = data.activity
    log.performed_by = data.performed_by
    log.timestamp = data.timestamp
    db.add(log)
    db.commit()
    db.refresh(log)

    wo = db.query(Workorder).filter(Workorder.id == log.workorder_id).first()
    if not wo:
        return None

    wo_dict = to_dict(wo)
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

    # Hapus semua WorkOrderActivityLog terkait
    for log in wo.activity_logs:
        db.delete(log)

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

    # --- Sinkronisasi ProductOrdered ---
    # Hapus yang tidak ada di data baru
    new_po_ids = set([str(po.product_id) for po in (data.product_ordered or [])])
    for po in list(wo.product_ordered):
        if str(po.product_id) not in new_po_ids:
            db.delete(po)

    # Tambah/update yang ada di data baru
    for prod in (data.product_ordered or []):
        po = db.query(ProductOrdered).filter(ProductOrdered.workorder_id == workorder_id, ProductOrdered.product_id == prod.product_id).first()
        if po:
            po.quantity = prod.quantity
            po.satuan_id = getattr(prod, 'satuan_id', None)
            po.price = prod.price
            po.subtotal = prod.subtotal
            po.discount = prod.discount
            db.add(po)
        else:
            new_po = ProductOrdered(
                id=uuid.uuid4(),
                workorder_id=workorder_id,
                product_id=prod.product_id,
                quantity=prod.quantity,
                satuan_id=getattr(prod, 'satuan_id', None),
                price=prod.price,
                subtotal=prod.subtotal,
                discount=prod.discount
            )
            db.add(new_po)

    # --- Sinkronisasi ServiceOrdered ---
    new_so_ids = set([str(so.service_id) for so in (data.service_ordered or [])])
    for so in list(wo.service_ordered):
        if str(so.service_id) not in new_so_ids:
            db.delete(so)

    for srv in (data.service_ordered or []):
        so = db.query(ServiceOrdered).filter(ServiceOrdered.workorder_id == workorder_id, ServiceOrdered.service_id == srv.service_id).first()
        if so:
            so.quantity = srv.quantity
            so.satuan = getattr(srv, 'satuan', None)
            so.price = srv.price
            so.subtotal = srv.subtotal
            so.discount = srv.discount
            db.add(so)
        else:
            new_so = ServiceOrdered(
                id=uuid.uuid4(),
                workorder_id=workorder_id,
                service_id=srv.service_id,
                quantity=srv.quantity,
                satuan=getattr(srv, 'satuan', None),
                price=srv.price,
                subtotal=srv.subtotal,
                discount=srv.discount
            )
            db.add(new_so)

    db.commit()
    db.refresh(wo)
    wo_dict = to_dict(wo)
    wo_dict['customer_name'] = wo.customer.nama if wo.customer else None
    wo_dict['vehicle_no_pol'] = wo.vehicle.no_pol if wo.vehicle else None
    return wo_dict

