from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from models.database import SessionLocal
from models.packet_order import PacketOrder, ProductLinePacketOrder, ServiceLinePacketOrder
from schemas.service_packet_order import CreatePacketOrder, CreateProductLinePacketOrder,CreateServiceLinePacketOrder
from services.services_packet_order import CreatePacketOrdernya,getAllPacketOrders, getPacketOrderById
from supports.utils_json_response import success_response, error_response
from middleware.jwt_required import jwt_required

router = APIRouter(prefix="/packetorders", tags=["Packet Order"])

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.post("/create/new", dependencies=[Depends(jwt_required)])
def createNewPacketOrders(
    dataOrder: CreatePacketOrder,
    db: Session = Depends(get_db)
):
    try:
        result = CreatePacketOrdernya(db, dataOrder)
        if not result:
            return error_response(message="Failed to create Packet Orders")
        return success_response(data=result)
    except Exception as e:
        return error_response(message=str(e))
    finally:
        db.close()

@router.get("/all", response_model=CreatePacketOrder)
def getAllPacketOrderAllRouter(
    db: Session=Depends(get_db)
):
    try:
        result = getAllPacketOrders(db)
        if not result:
            return error_response(message="Failed to grt All Packet Orders")
        return success_response(data=result)
    except Exception as e:
        return error_response(message=str(e))
    finally:
        db.close()

@router.get("/{packet_id}", response_model=CreatePacketOrder)
def getPacketOrderByIdRouter(
    packet_id: str,
    db: Session=Depends(get_db)
):
    try:
        result = getPacketOrderById(db, packet_id)
        if not result:
            return error_response(message="Failed to grt All Packet Orders")
        return success_response(data=result)
    except Exception as e:
        return error_response(message=str(e))
    finally:
        db.close()

