from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from models.database import SessionLocal
from services.services_customer import create_customer_with_vehicles,getListCustomersWithvehicles, getListCustomersWithVehiclesCustomersID
from supports.utils_json_response import success_response, error_response
from middleware.jwt_required import jwt_required
from schemas.service_customer import CreateCustomerWithVehicles, CustomerWithVehicleResponse

router = APIRouter(prefix="/customers")

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

