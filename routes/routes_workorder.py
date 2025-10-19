from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from uuid import UUID
from models.database import SessionLocal
from services.services_customer import create_customer_with_vehicles,getListCustomersWithvehicles, getListCustomersWithVehiclesCustomersID
from services.services_product import CreateProductNew, get_all_products, get_product_by_id, createServicenya,get_all_services, createBrandnya, createCategorynya, createSatuannya, getAllBrands, getAllCategories, getAllSatuans, getAllInventoryProducts, getInventoryByProductID, createProductMoveHistoryNew
from services.services_workorder import createNewWorkorder,getAllWorkorders, getWorkorderByID, updateServiceorderedOnlynya,updateWorkOrdeKeluhannya,UpdateDateWorkordernya,UpdateWorkorderOrdersnya,updateProductOrderedOnlynya,updateStatusWorkorder,update_only_productordered, update_only_serviceordered,update_only_workorder,update_workorder_lengkap, addProductOrder, updateProductOrder, deleteProductOrder, addServiceOrder, updateServiceOrder, deleteServiceOrder
from schemas.service_inventory import CreateProductMovedHistory
from schemas.service_product import CreateProduct, ProductResponse, CreateService, ServiceResponse
from schemas.service_accounting import SalesPaymentJournalEntry
from schemas.service_workorder import CreateWorkOrder,UpdateProductOrderedOnly,UpdateServiceOrderedOnly,UpdateWorkoderOrders,UpdateWorkorderComplaint,UpdateWorkorderDates,UpdateWorkorderStatus,UpdateWorkorderTotalCost,DeleteProductOrderedOnly,DeleteServiceOrderedOnly,UpdateProductOrderedOnly, UpdateServiceOrderedOnly, AddProductOrderById, UpdateProductOrderById, DeleteProductOrderById, AddServiceOrderById, UpdateServiceOrderById, DeleteServiceOrderById
from supports.utils_json_response import success_response, error_response
from middleware.jwt_required import jwt_required
from schemas.service_customer import CreateCustomerWithVehicles, CustomerWithVehicleResponse

router = APIRouter(prefix="/workorders", tags=["Workorder"])

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
    workorder_id: UUID,
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

@router.post("/update-only-status", dependencies=[Depends(jwt_required)])
def updateWorkorderStatusRouter(
    data_entry: SalesPaymentJournalEntry,
    db: Session = Depends(get_db)
):
    try:
        result = updateStatusWorkorder(db, data_entry)
        if not result:
            return error_response(message="Failed to update workorder status")
        return success_response(data=result)
    except Exception as e:
        return error_response(message=str(e))
    finally:
        db.close()

@router.post("/update/{workorder_id}", dependencies=[Depends(jwt_required)])
def updateWorkorderRouter(
    workorder_id: UUID,
    workorder_data: CreateWorkOrder,
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
    workorder_id: UUID,
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
        result = UpdateDateWorkordernya(db, workorder_id, tanggal_keluar)
        if not result:
            return error_response(message="Failed to update workorder tanggal keluar")
        return success_response(data=result)
    except Exception as e:
        return error_response(message=str(e))
    finally:
        db.close()



@router.post("/update/onlyproductordered/{workorder_id}", dependencies=[Depends(jwt_required)])
def updateOnlyProductOrderedRouter(
    workorder_id: UUID,
    product_ordered_data: UpdateProductOrderedOnly,
    db: Session = Depends(get_db)
):
    try:
        result = update_only_productordered(db, workorder_id, product_ordered_data)
        if not result:
            return error_response(message="Failed to update only product ordered")
        return success_response(data=result)
    except Exception as e:
        return error_response(message=str(e))
    finally:
        db.close()

@router.post("/update/onlyserviceordered/{workorder_id}", dependencies=[Depends(jwt_required)])
def updateOnlyServiceOrderedRouter(
    workorder_id: UUID,
    service_ordered_data: UpdateServiceOrderedOnly,
    db: Session = Depends(get_db)
):
    try:
        result = update_only_serviceordered(db, workorder_id, service_ordered_data)
        if not result:
            return error_response(message="Failed to update only service ordered")
        return success_response(data=result, message="Service ordered updated successfully")
    except Exception as e:
        return error_response(message=str(e))
    finally:
        db.close()  

@router.post("/update/workorderlengkap/{workorder_id}", dependencies=[Depends(jwt_required)])
def updateWorkorderLengkapRouter(
    workorder_id: UUID,
    workorder_data: CreateWorkOrder,
    db: Session = Depends(get_db)
):
    try:
        result = update_workorder_lengkap(db, workorder_id, workorder_data)
        if not result:
            return error_response(message="Failed to update workorder lengkap")
        return success_response(data=result, message="Workorder updated successfully")
    except Exception as e:
        return error_response(message=str(e))
    finally:
        db.close()

@router.post("/add/productorder", dependencies=[Depends(jwt_required)])
def addProductOrderRouter(
    product_order_data: AddProductOrderById,
    db: Session = Depends(get_db)
):
    try:
        result = addProductOrder(db, product_order_data)
        if not result:
            return error_response(message="Failed to add product order")
        return success_response(data=result, message="Product order added successfully")
    except Exception as e:
        return error_response(message=str(e))
    finally:
        db.close()

@router.put("/update/productorder/{product_ordered_id}", dependencies=[Depends(jwt_required)])
def updateProductOrderRouter(
    product_ordered_id: UUID,
    product_order_data: UpdateProductOrderById,
    db: Session = Depends(get_db)
):
    try:
        result = updateProductOrder(db, str(product_ordered_id), product_order_data)
        if not result:
            return error_response(message="Failed to update product order")
        return success_response(data=result, message="Product order updated successfully")
    except Exception as e:
        return error_response(message=str(e))
    finally:
        db.close()

@router.delete("/delete/productorder/{product_ordered_id}", dependencies=[Depends(jwt_required)])
def deleteProductOrderRouter(
    product_ordered_id: UUID,
    db: Session = Depends(get_db)
):
    try:
        result = deleteProductOrder(db, str(product_ordered_id))
        if not result:
            return error_response(message="Failed to delete product order")
        return success_response(data=result, message="Product order deleted successfully")
    except Exception as e:
        return error_response(message=str(e))
    finally:
        db.close()

@router.post("/add/serviceorder", dependencies=[Depends(jwt_required)])
def addServiceOrderRouter(
    service_order_data: AddServiceOrderById,
    db: Session = Depends(get_db)
):
    try:
        result = addServiceOrder(db, service_order_data)
        if not result:
            return error_response(message="Failed to add service order")
        return success_response(data=result, message="Service order added successfully")
    except Exception as e:
        return error_response(message=str(e))
    finally:
        db.close()

@router.put("/update/serviceorder/{service_ordered_id}", dependencies=[Depends(jwt_required)])
def updateServiceOrderRouter(
    service_ordered_id: UUID,
    service_order_data: UpdateServiceOrderById,
    db: Session = Depends(get_db)
):
    try:
        result = updateServiceOrder(db, str(service_ordered_id), service_order_data)
        if not result:
            return error_response(message="Failed to update service order")
        return success_response(data=result, message="Service order updated successfully")
    except Exception as e:
        return error_response(message=str(e))
    finally:
        db.close()

@router.delete("/delete/serviceorder/{service_ordered_id}", dependencies=[Depends(jwt_required)])
def deleteServiceOrderRouter(
    service_ordered_id: UUID,
    db: Session = Depends(get_db)
):
    try:
        result = deleteServiceOrder(db, str(service_ordered_id))
        if not result:
            return error_response(message="Failed to delete service order")
        return success_response(data=result, message="Service order deleted successfully")
    except Exception as e:
        return error_response(message=str(e))
    finally:
        db.close()
