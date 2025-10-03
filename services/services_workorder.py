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
        status=workorder_data.status,
        total_discount=workorder_data.total_discount,
        total_biaya=workorder_data.total_biaya,
        customer_id=workorder_data.customer_id,
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
                subtotal=srv.subtotal,
                discount=srv.discount,
                workorder_id=workorder.id
            )
            db.add(service_ordered)

    db.commit()
    db.refresh(workorder)
    return to_dict(workorder)

def getAllWorkorders(db: Session):
    workorders = db.query(Workorder).all()
    result = []
    for wo in workorders:
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

        result.append(wo_dict)
    return result

def getWorkorderByID(db: Session, workorder_id: str):
    wo = db.query(Workorder).filter(Workorder.id == workorder_id).first()
    if not wo:
        return None

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

def updateStatusWorkorder(db: Session, workorder_id: str, new_status: str, performed_by: str = 'system'):
    wo = db.query(Workorder).filter(Workorder.id == workorder_id).first()
    if not wo:
        return None

    old_status = wo.status
    wo.status = new_status
    db.add(wo)

    # Log perubahan status
    log_entry = WorkOrderActivityLog(
        id=uuid.uuid4(),
        workorder_id=wo.id,
        activity=f"Status changed from {old_status} to {new_status}",
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

def UpdateWorkorderOrdersnya(db: Session, workorder_id: str, update_data: UpdateWorkorderOrders, performed_by: str = 'system'):
    wo = db.query(Workorder).filter(Workorder.id == workorder_id).first()
    if not wo:
        return None

    # Update ProductOrdered
    if update_data.product_ordered:
        for prod in update_data.product_ordered:
            po = db.query(ProductOrdered).filter(ProductOrdered.id == prod.id, ProductOrdered.workorder_id == workorder_id).first()
            if po:
                old_quantity = po.quantity
                old_subtotal = po.subtotal
                old_discount = po.discount

                po.quantity = prod.quantity
                po.subtotal = prod.subtotal
                po.discount = prod.discount
                db.add(po)

                # Log perubahan pada ProductOrdered
                log_entry = WorkOrderActivityLog(
                    id=uuid.uuid4(),
                    workorder_id=wo.id,
                    activity=f"ProductOrdered {po.id} updated: quantity {old_quantity} -> {prod.quantity}, subtotal {old_subtotal} -> {prod.subtotal}, discount {old_discount} -> {prod.discount}",
                    performed_by=performed_by,
                    timestamp=datetime.datetime.now()
                )
                db.add(log_entry)

    # Update ServiceOrdered
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
                db.add(so)

                # Log perubahan pada ServiceOrdered
                log_entry = WorkOrderActivityLog(
                    id=uuid.uuid4(),
                    workorder_id=wo.id,
                    activity=f"ServiceOrdered {so.id} updated: quantity {old_quantity} -> {srv.quantity}, subtotal {old_subtotal} -> {srv.subtotal}, discount {old_discount} -> {srv.discount}",
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
