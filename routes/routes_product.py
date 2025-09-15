from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from models.database import SessionLocal
from services.services_customer import create_customer_with_vehicles,getListCustomersWithvehicles, getListCustomersWithVehiclesCustomersID
from services.services_product import CreateProduct, get_all_products, get_product_by_id, createServie,get_all_services
from schemas.service_product import CreateProduct, ProductResponse, CreateService, ServiceResponse
from supports.utils_json_response import success_response, error_response
from middleware.jwt_required import jwt_required
from schemas.service_customer import CreateCustomerWithVehicles, CustomerWithVehicleResponse

router = APIRouter(prefix="/products")

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("/create/new", response_model=ProductResponse, dependencies=[Depends(jwt_required)])
def create_product_router(
    product_data: CreateProduct,
    db: Session = Depends(get_db)
):
    try:
        result = CreateProduct(db, product_data)
        if not result:
            return error_response(message="Failed to create product")
        return success_response(data=result)
    except Exception as e:
        return error_response(message=str(e))
    finally:
        db.close()
    
@router.get("/all", response_model=list[ProductResponse])
def list_all_products(
    db: Session = Depends(get_db)
):
    try:
        result = get_all_products(db)
        return success_response(data=result)
    except Exception as e:
        return error_response(message=str(e))   
    finally:
        db.close()

@router.get("/{product_id}", response_model=ProductResponse)
def get_product(
    product_id: str,
    db: Session = Depends(get_db)
):
    try:
        result = get_product_by_id(db, product_id)
        if not result:
            raise HTTPException(status_code=404, detail="Product not found")
        return success_response(data=result)
    except Exception as e:
        return error_response(message=str(e))
    finally:
        db.close()

@router.post("/service/create/new", response_model=ServiceResponse, dependencies=[Depends(jwt_required)])
def create_service_router(
    service_data: CreateService,
    db: Session = Depends(get_db)
):
    try:
        result = createServie(db, service_data)
        if not result:
            return error_response(message="Failed to create service")
        return success_response(data=result)
    except Exception as e:
        return error_response(message=str(e))
    finally:
        db.close()

@router.get("/service/all", response_model=list[ServiceResponse])
def list_all_services( 
    db: Session = Depends(get_db)
):
    try:
        result = get_all_services(db)
        return success_response(data=result)
    except Exception as e:
        return error_response(message=str(e))
    finally:
        db.close()
    
@router.get("/service/{service_id}", response_model=ServiceResponse)
def get_service(
    service_id: str,
    db: Session = Depends(get_db)
):
    try:
        result = get_product_by_id(db, service_id)
        if not result:
            raise HTTPException(status_code=404, detail="Service not found")
        return success_response(data=result)
    except Exception as e:
        return error_response(message=str(e))
    finally:
        db.close()