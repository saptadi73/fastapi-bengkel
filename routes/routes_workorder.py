from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from models.database import SessionLocal
from services.services_customer import create_customer_with_vehicles,getListCustomersWithvehicles, getListCustomersWithVehiclesCustomersID
from services.services_product import CreateProductNew, get_all_products, get_product_by_id, createServie,get_all_services, createBrand, createCategory, createSatuan, getAllBrands, getAllCategories, getAllSatuans, getAllInventoryProducts, getInventoryByProductID, createProductMoveHistoryNew
from services.services_workorder import createNewWorkorder,getAllWorkorders, getWorkorderByID, updateServiceorderedOnlynya,updateStatusWorkorder,updateWorkOrdeKeluhannya,UpdateDateWorkordernya,UpdateWorkorderOrdersnya,updateProductOrderedOnlynya
from schemas.service_inventory import CreateProductMovedHistory
from schemas.service_product import CreateProduct, ProductResponse, CreateService, ServiceResponse
from schemas.service_workorder import CreateWorkOrder,UpdateProductOrderedOnly,UpdateServiceOrderedOnly,UpdateWorkoderOrders,UpdateWorkorderComplaint,UpdateWorkorderDates,UpdateWorkorderStatus,UpdateWorkorderTotalCost,DeleteProductOrderedOnly,DeleteServiceOrderedOnly
from supports.utils_json_response import success_response, error_response
from middleware.jwt_required import jwt_required
from schemas.service_customer import CreateCustomerWithVehicles, CustomerWithVehicleResponse

router = APIRouter(prefix="/workorders")

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("/create/new", dependencies=[Depends(jwt_required)])
def createWorkorderRouter(
    workorder_data: CreateWorkOrder,
    db: Session = Depends(get_db)
):
    try:
        result = createNewWorkorder(db, workorder_data)
        if not result:
            return error_response(message="Failed to create workorder")
        return success_response(data=result)
    except Exception as e:
        return error_response(message=str(e))   
    finally:
        db.close()

@router.get("/all", response_model=list[CreateWorkOrder])
def listAllWorkorders(
    db: Session = Depends(get_db)
):
    try:
        result = getAllWorkorders(db)
        return success_response(data=result)
    except Exception as e:
        return error_response(message=str(e))   
    finally:
        db.close()

@router.get("/{workorder_id}", response_model=CreateWorkOrder)
def getWorkorder(
    workorder_id: str,
    db: Session = Depends(get_db)
):
    try:
        result = getWorkorderByID(db, workorder_id)
        if not result:
            raise HTTPException(status_code=404, detail="Workorder not found")
        return success_response(data=result)
    except Exception as e:
        return error_response(message=str(e))   
    finally:
        db.close()

@router.post("/update/{workorder_id}", dependencies=[Depends(jwt_required)])
def updateWorkorderRouter(
    workorder_id: str,
    workorder_data: UpdateWorkoderOrders,
    db: Session = Depends(get_db)
):
    try:
        result = UpdateWorkorderOrdersnya(db, workorder_id, workorder_data)
        if not result:
            return error_response(message="Failed to update workorder")
        return success_response(data=result)
    except Exception as e:
        return error_response(message=str(e))   
    finally:
        db.close()

@router.post("/update/keluhan/{workorder_id}", dependencies=[Depends(jwt_required)])
def updateWorkorderKeluhanRouter(
    workorder_id: str,
    data: UpdateWorkorderComplaint,
    db: Session = Depends(get_db)
):
    try:
        result = updateWorkOrdeKeluhannya(db, workorder_id, data)
        if not result:
            return error_response(message="Failed to update workorder keluhan")
        return success_response(data=result)
    except Exception as e:
        return error_response(message=str(e))   
    finally:
        db.close()

def updateDateWorkOrdernya(db: Session, workorder_id: str, tanggal_keluar: str):
    try:
        result = UpdateDateWorkorder(db, workorder_id, tanggal_keluar)
        if not result:
            return error_response(message="Failed to update workorder tanggal keluar")
        return success_response(data=result)
    except Exception as e:
        return error_response(message=str(e))   
    finally:
        db.close()

@router.post("/update/status/{workorder_id}", dependencies=[Depends(jwt_required)])
def updateWorkorderStatusRouter(
    workorder_id: str,
    status: str,
    db: Session = Depends(get_db)
):
    try:
        result = updateStatusWorkorder(db, workorder_id, status)
        if not result:
            return error_response(message="Failed to update workorder status")
        return success_response(data=result)
    except Exception as e:
        return error_response(message=str(e))   
    finally:
        db.close()

