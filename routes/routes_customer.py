from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from models.database import SessionLocal
from services.services_customer import create_customer_with_vehicles,getListCustomersWithvehicles, getListCustomersWithVehiclesCustomersID, getServiceOrderedAndProductOrderedByVehicleID, createCustomerOnly, getListCustomersWithvehiclesId
from supports.utils_json_response import success_response, error_response
from middleware.jwt_required import jwt_required
from schemas.service_customer import CreateCustomerWithVehicles, CustomerWithVehicleResponse, CreateCustomer, CreateVehicle

router = APIRouter(prefix="/customers", tags=["Customer"])

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("/with-vehicle", dependencies=[Depends(jwt_required)])
def create_customer_with_vehicle_router(
    customer_data: CreateCustomerWithVehicles,
    db: Session = Depends(get_db)
):
    try:
        result = create_customer_with_vehicles(db, customer_data)
        return success_response(data=result)
    except Exception as e:
        return error_response(message=str(e))
    
@router.get("/with-vehicles")
def list_customers_with_vehicles(
    db: Session = Depends(get_db)
):
    try:
        result = getListCustomersWithvehicles(db)
        return success_response(data=result)
    except Exception as e:
        return error_response(message=str(e))

@router.get("/with-vehicles/{vehicle_id}")
def list_customers_with_vehicles(
    vehicle_id: str,
    db: Session = Depends(get_db)
):
    try:
        result = getListCustomersWithvehiclesId(db, vehicle_id)
        return success_response(data=result)
    except Exception as e:
        return error_response(message=str(e))

@router.get("/history/service/{vehicle_id}")
def get_service_history_by_vehicle(
    vehicle_id: str,
    db: Session = Depends(get_db)
):
    try:
        result = getServiceOrderedAndProductOrderedByVehicleID(db, vehicle_id)
        if not result:
            raise HTTPException(status_code=404, detail="Vehicle not found")
        return success_response(data=result)
    except Exception as e:
        return error_response(message=str(e))





@router.get("/{customer_id}/with-vehicles", response_model=CustomerWithVehicleResponse)
def get_customer_with_vehicles(
    customer_id: str,
    db: Session = Depends(get_db)
):
    try:
        result = getListCustomersWithVehiclesCustomersID(db, customer_id)
        if not result:
            raise HTTPException(status_code=404, detail="Customer not found")
        return success_response(data=result)
    except Exception as e:
        return error_response(message=str(e))

@router.post("/customer-only", dependencies=[Depends(jwt_required)])
def createCustomerOnlynya(
    customer_data: CreateCustomer,
    db: Session = Depends(get_db)
):
    try:
        result = createCustomerOnly(db, customer_data)
        return success_response(data=result)
    except Exception as e:
        return error_response(message=str(e))

@router.get("/all")
def getAllCustomersRouter(
    db: Session = Depends(get_db)
):
    try:
        from services.services_customer import getAllCustomers
        result = getAllCustomers(db)
        return success_response(data=result)
    except Exception as e:
        return error_response(message=str(e))
    
@router.post("/add-vehicle", dependencies=[Depends(jwt_required)])
def createVehicletoCustomerRouter(
    vehicle_data: CreateVehicle,
    db: Session = Depends(get_db)
):
    try:
        from services.services_customer import createVehicletoCustomer
        result = createVehicletoCustomer(db, vehicle_data)
        return success_response(data=result)
    except Exception as e:
        return error_response(message=str(e))


@router.post("/send-maintenance-reminder", dependencies=[Depends(jwt_required)])
def send_maintenance_reminder_router(
    db: Session = Depends(get_db)
):
    """
    Endpoint untuk mengirim reminder WhatsApp maintenance ke customer
    yang jadwal maintenance-nya kurang dari 3 hari.
    
    Returns:
        {
            "total_customers": int (jumlah total customer dengan vehicle),
            "reminder_sent": int (jumlah reminder yang berhasil dikirim),
            "details": list (detail setiap customer/vehicle)
        }
    """
    try:
        from services.services_customer import send_maintenance_reminder_whatsapp
        result = send_maintenance_reminder_whatsapp(db)
        return success_response(data=result)
    except Exception as e:
        return error_response(message=str(e))