from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from models.database import SessionLocal
from services.services_customer import create_customer_with_vehicles,getListCustomersWithvehicles, getListCustomersWithVehiclesCustomersID
from services.services_product import CreateProductNew, get_all_products, get_product_by_id, createServicenya,get_all_services, createBrandnya, createCategorynya, createSatuannya, getAllBrands, getAllCategories, getAllSatuans, getAllInventoryProducts, getInventoryByProductID, createProductMoveHistoryNew, get_service_by_id, update_product_cost, getAllInventoryProductsConsignment,getAllInventoryProductsExcConsignment
from services.services_inventory import manual_adjustment_inventory
from services.services_costing import get_product_cost_history, get_product_cost_summary
from schemas.service_inventory import CreateProductMovedHistory, ManualAdjustment
from schemas.service_product import CreateProduct, ProductResponse, CreateService, ServiceResponse, CreateBrand, CreateCategory, CreateSatuan, UpdateProductCost, ProductCostHistoryRequest, ProductCostHistoryResponse
from typing import Optional
from datetime import datetime
from supports.utils_json_response import success_response, error_response
from middleware.jwt_required import jwt_required
from schemas.service_customer import CreateCustomerWithVehicles, CustomerWithVehicleResponse

router = APIRouter(prefix="/products", tags=["Product"])

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("/create/new")
def create_product_router(
    product_data: CreateProduct,
    db: Session = Depends(get_db)
):
    print(product_data)  # Akan tampil di terminal/server
    print(product_data.dict())  # Lihat dict hasil parsing Pydantic
    try:
        result = CreateProductNew(db, product_data)
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
        result = createServicenya(db, service_data)
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
        result = get_service_by_id(db, service_id)
        if not result:
            raise HTTPException(status_code=404, detail="Service not found")
        return success_response(data=result)
    except Exception as e:
        return error_response(message=str(e))
    finally:
        db.close()

@router.post("/brand/create/new", dependencies=[Depends(jwt_required)])
def create_brand_router(
    dataBrand: CreateBrand,
    db: Session = Depends(get_db)
):
    try:
        result = createBrandnya(db, dataBrand)
        if not result:
            return error_response(message="Failed to create brand")
        return success_response(data=result)
    except Exception as e:
        return error_response(message=str(e))
    finally:
        db.close()

@router.post("/category/create/new", dependencies=[Depends(jwt_required)])
def create_category_router(
    dataCategory: CreateCategory,
    db: Session = Depends(get_db)
):
    try:
        result = createCategorynya(db, dataCategory)
        if not result:
            return error_response(message="Failed to create category")
        return success_response(data=result)
    except Exception as e:
        return error_response(message=str(e))
    finally:
        db.close()

@router.post("/satuan/create/new", dependencies=[Depends(jwt_required)])
def create_satuan_router(
    dataSatuan: CreateSatuan,
    db: Session = Depends(get_db)
):
    try:
        result = createSatuannya(db, dataSatuan)
        if not result:
            return error_response(message="Failed to create satuan")
        return success_response(data=result)
    except Exception as e:
        return error_response(message=str(e))
    finally:
        db.close()

@router.get("/brands/all")
def list_all_brands(
    db: Session = Depends(get_db)
):
    try:
        result = getAllBrands(db)
        return success_response(data=result)
    except Exception as e:
        return error_response(message=str(e))
    finally:
        db.close()

@router.get("/satuans/all")
def listSatuans(
    db: Session = Depends(get_db)
):
    try:
        result = getAllSatuans(db)
        return success_response(data=result)
    except Exception as e:
        return error_response(message=str(e))
    finally:
        db.close()

@router.get("/categories/all")
def listCategories(
    db: Session = Depends(get_db)
):
    try:
        result = getAllCategories(db)
        return success_response(data=result)
    except Exception as e:
        return error_response(message=str(e))
    finally:
        db.close()

@router.get("/inventory/all")
def getAllInventoryProduct(
    db: Session = Depends(get_db)
):
    try:
        result = getAllInventoryProducts(db)
        return success_response(data=result)
    except Exception as e:
        return error_response(message=str(e))
    finally:
        db.close()

@router.get("/inventory/all/consignment")
def getAllInventoryProduct(
    db: Session = Depends(get_db)
):
    try:
        result = getAllInventoryProductsConsignment(db)
        return success_response(data=result)
    except Exception as e:
        return error_response(message=str(e))
    finally:
        db.close()

@router.get("/inventory/all/excconsignment")
def getAllInventoryProduct(
    db: Session = Depends(get_db)
):
    try:
        result = getAllInventoryProductsExcConsignment(db)
        return success_response(data=result)
    except Exception as e:
        return error_response(message=str(e))
    finally:
        db.close()

@router.get("/inventory/{product_id}")
def getInventoryByProductIDRouter(
    product_id: str,
    db: Session = Depends(get_db)
):
    try:
        result = getInventoryByProductID(db, product_id)
        if not result:
            return error_response(message="Inventory not found for the given product ID", status_code=404)
        return success_response(data=result)
    except Exception as e:
        return error_response(message=str(e))
    finally:
        db.close()

@router.post("/inventory/move/new", dependencies=[Depends(jwt_required)])
def createProductMoveHistoryRouter(
    move_data: CreateProductMovedHistory,
    db: Session = Depends(get_db)
):
    try:
        result = createProductMoveHistoryNew(db, move_data)
        if not result:
            return error_response(message="Failed to create product move history")
        return success_response(data=result)
    except Exception as e:
        return error_response(message=str(e))
    finally:
        db.close()

@router.put("/cost", dependencies=[Depends(jwt_required)])
def update_product_cost_router(
    cost_data: UpdateProductCost,
    db: Session = Depends(get_db)
):
    try:
        result = update_product_cost(db, str(cost_data.product_id), cost_data.cost)
        if not result:
            return error_response(message="Failed to update product cost")
        return success_response(data=result)
    except Exception as e:
        return error_response(message=str(e))
    finally:
        db.close()

@router.post("/inventory/adjustment", dependencies=[Depends(jwt_required)])
def manual_adjustment_inventory_router(
    adjustment_data: ManualAdjustment,
    db: Session = Depends(get_db)
):
    try:
        result = manual_adjustment_inventory(db, adjustment_data)
        if not result:
            return error_response(message="Failed to perform manual adjustment")
        return success_response(data=result)
    except Exception as e:
        return error_response(message=str(e))
    finally:
        db.close()

# Cost History Endpoints
@router.get("/cost-history", response_model=list[ProductCostHistoryResponse])
def get_cost_history_router(
    product_id: Optional[str] = None,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    calculation_method: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """
    Get product cost history with optional filters.
    
    Query Parameters:
    - product_id: Filter by specific product UUID
    - start_date: Filter by start date (ISO format)
    - end_date: Filter by end date (ISO format)
    - calculation_method: Filter by method (average, adjustment, manual)
    """
    try:
        result = get_product_cost_history(
            db=db,
            product_id=product_id,
            start_date=start_date,
            end_date=end_date,
            calculation_method=calculation_method
        )
        return success_response(data=result)
    except Exception as e:
        return error_response(message=str(e))
    finally:
        db.close()

@router.get("/{product_id}/cost-history", response_model=list[ProductCostHistoryResponse])
def get_product_cost_history_router(
    product_id: str,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    db: Session = Depends(get_db)
):
    """
    Get cost history for a specific product.
    
    Path Parameters:
    - product_id: Product UUID
    
    Query Parameters:
    - start_date: Filter by start date (ISO format)
    - end_date: Filter by end date (ISO format)
    """
    try:
        result = get_product_cost_history(
            db=db,
            product_id=product_id,
            start_date=start_date,
            end_date=end_date
        )
        if not result:
            return success_response(data=[], message="No cost history found for this product")
        return success_response(data=result)
    except Exception as e:
        return error_response(message=str(e))
    finally:
        db.close()

@router.get("/{product_id}/cost-summary")
def get_product_cost_summary_router(
    product_id: str,
    db: Session = Depends(get_db)
):
    """
    Get cost summary for a specific product.
    
    Returns current cost, quantity, and latest cost change information.
    
    Path Parameters:
    - product_id: Product UUID
    """
    try:
        result = get_product_cost_summary(db=db, product_id=product_id)
        if not result:
            return error_response(message="Product not found", status_code=404)
        return success_response(data=result)
    except ValueError as e:
        return error_response(message=str(e), status_code=404)
    except Exception as e:
        return error_response(message=str(e))
    finally:
        db.close()





