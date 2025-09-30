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
    # Step 1: Create the PacketOrder and commit to get its id
    packetorder = PacketOrder(
        id=uuid.uuid4(),
        name=data.name
    )
    db.add(packetorder)
    db.commit()  # Commit to generate the packet_order.id
    db.refresh(packetorder)  # Refresh the packetorder object to get the generated id

    # Step 2: Add ProductLinePacketOrder, linking each product to the packet_order_id
    if data.product_line_packet_order:
        for productnya in data.product_line_packet_order:
            product_line = ProductLinePacketOrder(
                id=uuid.uuid4(),
                product_id=productnya.product_id,
                price=productnya.price,
                quantity=productnya.quantity,
                discount=productnya.discount,
                subtotal=productnya.subtotal,
                packet_order_id=packetorder.id  # Associate with the PacketOrder
            )
            db.add(product_line)
    
    # Step 3: Add ServiceLinePacketOrder, linking each service to the packet_order_id
    if data.service_line_packet_order:
        for servicenya in data.service_line_packet_order:
            service_line = ServiceLinePacketOrder(
                id=uuid.uuid4(),
                service_id=servicenya.service_id,
                price=servicenya.price,
                quantity=servicenya.quantity,
                discount=servicenya.discount,
                subtotal=servicenya.subtotal,
                packet_order_id=packetorder.id  # Associate with the PacketOrder
            )
            db.add(service_line)

    # Step 4: Commit the product and service line insertions
    db.commit()  # Commit the product and service line changes

    # Step 5: Refresh the packetorder again if needed, or just return it
    db.refresh(packetorder)

    # Step 6: Return the PacketOrder as a dictionary (response to the client)
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
    
def deletePacketOrder(db: Session, packet_order_id: str):
    try:
        # Step 1: Find the PacketOrder by ID
        packet_order = db.query(PacketOrder).filter(PacketOrder.id == packet_order_id).first()
        
        if not packet_order:
            return {"message": "PacketOrder not found"}

        # Step 2: Delete associated ProductLinePacketOrder records
        for product_line in packet_order.product_line_packet_order:
            db.delete(product_line)

        # Step 3: Delete associated ServiceLinePacketOrder records
        for service_line in packet_order.service_line_packet_order:
            db.delete(service_line)

        # Step 4: Delete the PacketOrder record
        db.delete(packet_order)
        
        # Step 5: Commit the changes
        db.commit()
        
        return {"message": "PacketOrder deleted successfully"}

    except IntegrityError:
        db.rollback()
        return {"message": "Error deleting PacketOrder, possible foreign key constraint violation"}

def updatePacketOrder(db: Session, packet_order_id: str, data: CreatePacketOrder):
    try:
        # Step 1: Find the existing PacketOrder by ID
        packet_order = db.query(PacketOrder).filter(PacketOrder.id == packet_order_id).first()

        if not packet_order:
            return {"message": "PacketOrder not found"}

        # Step 2: Update the PacketOrder fields
        packet_order.name = data.name

        # Step 3: Update ProductLinePacketOrder entries
        # First, delete the old product lines
        for product_line in packet_order.product_line_packet_order:
            db.delete(product_line)

        # Then, add the new product lines
        if data.product_line_packet_order:
            for productnya in data.product_line_packet_order:
                product_line = ProductLinePacketOrder(
                    id=uuid.uuid4(),
                    product_id=productnya.product_id,
                    price=productnya.price,
                    quantity=productnya.quantity,
                    discount=productnya.discount,
                    subtotal=productnya.subtotal,
                    packet_order_id=packet_order.id
                )
                db.add(product_line)

        # Step 4: Update ServiceLinePacketOrder entries
        # First, delete the old service lines
        for service_line in packet_order.service_line_packet_order:
            db.delete(service_line)

        # Then, add the new service lines
        if data.service_line_packet_order:
            for servicenya in data.service_line_packet_order:
                service_line = ServiceLinePacketOrder(
                    id=uuid.uuid4(),
                    service_id=servicenya.service_id,
                    price=servicenya.price,
                    quantity=servicenya.quantity,
                    discount=servicenya.discount,
                    subtotal=servicenya.subtotal,
                    packet_order_id=packet_order.id
                )
                db.add(service_line)

        # Step 5: Commit the changes
        db.commit()

        # Step 6: Refresh and return the updated packet order
        db.refresh(packet_order)
        return to_dict(packet_order)

    except IntegrityError:
        db.rollback()
        return {"message": "Error updating PacketOrder, possible foreign key constraint violation"}

