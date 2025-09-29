from sqlalchemy.exc import IntegrityError
from datetime import datetime
from sqlalchemy.orm import Session
from models.packet_order import PacketOrder,ProductLinePacketOrder,ServiceLinePacketOrder
import uuid
from models.database import get_db
from schemas.service_packet_order import CreatePacketOrder, CreateProductLinePacketOrder, CreateServiceLinePacketOrder
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

def CreatePacketOrdernya(db: Session, data: CreatePacketOrder):
    packetorder = PacketOrder(
        id=uuid.uuid4(),
        name= data.name
    )
    db.add(packetorder)
    db.flush()

    if data.product_line_packet_order:
        for productnya in data.product_line_packet_order:
            product_line = ProductLinePacketOrder(
                id=uuid.uuid4(),
                product_id=productnya.product_id,
                price=productnya.price,
                quantity=productnya.quantity,
                discount=productnya.discount,
                subtotal = productnya.subtotal
            )
            db.add(product_line)

    if data.service_line_packet_order:
        for servicenya in data.service_line_packet_order:
            service_line = ServiceLinePacketOrder(
                id=uuid.uuid4(),
                sevice_id = servicenya.service_id,
                price = servicenya.price,
                quantity = servicenya.quantity,
                discount = servicenya.discount,
                subtotal = servicenya.subtotal
            )
            db.add(service_line)

    db.commit
    db.refresh(packetorder)
    return to_dict(packetorder)

def getAllPacketOrders(db: Session):
    packetorders = db.query(PacketOrder).all()
    result = []

    for po in packetorders:
        po_dict = to_dict(po)

        product_line_list =[]
        for pr in po.product_line_packet_order:
            pr_dict = to_dict(pr)

            pr_dict['product_name'] = pr.product.name if pr.product else None
            pr_dict['satuan_name'] = pr.product.satuan.name if pr.product.satuan else None
            product_line_list.append(pr_dict)
            po_dict['product_line'] = product_line_list

        service_line_list = []
        for srv in po.service_line_packet_order:
            srv_dict = to_dict(srv)

            srv_dict['service_name'] = srv.service.name if srv.service else None
            service_line_list.append(srv_dict)
            po_dict['service_line'] = service_line_list

        result.append(po_dict)
        return result
    
def getPacketOrderById(db: Session, packet_order_id: str):
    packetorders = db.query(PacketOrder).filter(PacketOrder.id==packet_order_id).first()
    result = []

    for po in packetorders:
        po_dict = to_dict(po)

        product_line_list =[]
        for pr in po.product_line_packet_order:
            pr_dict = to_dict(pr)

            pr_dict['product_name'] = pr.product.name if pr.product else None
            pr_dict['satuan_name'] = pr.product.satuan.name if pr.product.satuan else None
            product_line_list.append(pr_dict)
            po_dict['product_line'] = product_line_list

        service_line_list = []
        for srv in po.service_line_packet_order:
            srv_dict = to_dict(srv)

            srv_dict['service_name'] = srv.service.name if srv.service else None
            service_line_list.append(srv_dict)
            po_dict['service_line'] = service_line_list

        result.append(po_dict)
        return result
