from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from models.database import SessionLocal
from services.services_customer import create_customer_with_vehicles,getListCustomersWithvehicles, getListCustomersWithVehiclesCustomersID
from services.services_product import CreateProductNew, get_all_products, get_product_by_id, update_product, delete_product, ProductInUseError, createServicenya,get_all_services, createBrandnya, createCategorynya, createSatuannya, getAllBrands, getAllCategories, getAllSatuans, getAllInventoryProducts, getInventoryByProductID, createProductMoveHistoryNew, get_service_by_id, update_product_cost, getAllInventoryProductsConsignment,getAllInventoryProductsExcConsignment, update_service, delete_service, get_inventory_products_paginated
from services.services_inventory import manual_adjustment_inventory
from services.services_inventory_extended import update_inventory_adjustment, delete_inventory_adjustment, get_adjustment_by_id, get_inventory_adjustments
from uuid import UUID
from services.services_costing import get_product_cost_history, get_product_cost_summary
from schemas.service_inventory import CreateProductMovedHistory, ManualAdjustment, CreateProductMovedHistories
from schemas.service_product import ApiErrorResponse, CreateProduct, UpdateProduct, ProductResponse, ProductMutationResponse, ProductDeleteResponse, CreateService, ServiceResponse, CreateBrand, CreateCategory, CreateSatuan, UpdateProductCost, ProductCostHistoryRequest, ProductCostHistoryResponse, InventoryListResponse
from typing import Literal, Optional
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

@router.put("/service/{service_id}", response_model=ServiceResponse, dependencies=[Depends(jwt_required)])
def update_service_router(
    service_id: str,
    service_data: CreateService,
    db: Session = Depends(get_db)
):
    try:
        result = update_service(db, service_id, service_data)
        if not result:
            return error_response(message="Failed to update service")
        return success_response(data=result, message="Service updated successfully")
    except ValueError as e:
        return error_response(message=str(e), status_code=404)
    except Exception as e:
        return error_response(message=str(e))
    finally:
        db.close()

@router.delete("/service/{service_id}", dependencies=[Depends(jwt_required)])
def delete_service_router(
    service_id: str,
    db: Session = Depends(get_db)
):
    try:
        result = delete_service(db, service_id)
        if not result:
            return error_response(message="Failed to delete service")
        return success_response(message="Service deleted successfully")
    except ValueError as e:
        return error_response(message=str(e), status_code=404)
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

@router.get("/inventory/all", response_model=InventoryListResponse)
def getInventoryAllProduct(
    page: int = Query(default=1, ge=1),
    limit: int = Query(default=25, ge=1, le=100),
    search: Optional[str] = Query(default=None, min_length=1, max_length=100),
    category_id: Optional[UUID] = None,
    stock_status: Optional[Literal["safe", "reorder"]] = None,
    db: Session = Depends(get_db)
):
    try:
        return get_inventory_products_paginated(
            db,
            page=page,
            limit=limit,
            search=search,
            category_id=category_id,
            stock_status=stock_status,
        )
    except Exception:
        return error_response(
            message="Failed to retrieve inventory",
            status_code=500,
        )

@router.get("/inventory/all/consignment")
def getAllInventoryProductConsignment(
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
        db.commit()
        return success_response(data=result)
    except Exception as e:
        db.rollback()
        return error_response(message=str(e))
    finally:
        db.close()

@router.post("/inventory/move/new/multi", dependencies=[Depends(jwt_required)])
def createProductMoveHistoryMultiRouter(
    move_data: CreateProductMovedHistories,
    db: Session = Depends(get_db)
):
    try:
        results = []
        for item in move_data.items:
            result = createProductMoveHistoryNew(db, item)
            if not result:
                return error_response(message=f"Failed to create product move history for product {item.product_id}")
            results.append(result)
        db.commit()  # Commit all changes after processing all items
        return success_response(data=results)
    except Exception as e:
        db.rollback()  # Rollback on error
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


@router.get("/inventory/adjustment")
def list_adjustment_inventory_router(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    try:
        result = get_inventory_adjustments(db, skip, limit)
        return success_response(
            data=result,
            message=f"Retrieved {len(result)} adjustment records"
        )
    except Exception as e:
        return error_response(message=str(e))
    finally:
        db.close()


@router.get("/inventory/adjustment/{adjustment_id}")
def get_adjustment_inventory_router(
    adjustment_id: UUID,
    db: Session = Depends(get_db)
):
    try:
        result = get_adjustment_by_id(db, adjustment_id)
        return success_response(data=result)
    except ValueError as e:
        return error_response(message=str(e), status_code=404)
    except Exception as e:
        return error_response(message=str(e))
    finally:
        db.close()

@router.put("/inventory/adjustment/{adjustment_id}", dependencies=[Depends(jwt_required)])
def update_adjustment_inventory_router(
    adjustment_id: UUID,
    adjustment_data: ManualAdjustment,
    db: Session = Depends(get_db)
):
    """
    Update an existing inventory adjustment record
    
    **Path parameters:**
    - adjustment_id: UUID of the adjustment to update
    
    **Request body:**
    - product_id: Product ID
    - old_quantity: Old/current quantity
    - new_quantity: New quantity
    - reason: Reason for adjustment
    - performed_by: User performing adjustment
    - notes: Additional notes
    """
    try:
        result = update_inventory_adjustment(db, adjustment_id, adjustment_data.model_dump(exclude_unset=True))
        if not result:
            return error_response(message="Failed to update adjustment")
        return success_response(data=result, message="Adjustment updated successfully")
    except ValueError as e:
        return error_response(message=str(e), status_code=404)
    except Exception as e:
        return error_response(message=str(e))
    finally:
        db.close()

@router.delete("/inventory/adjustment/{adjustment_id}", dependencies=[Depends(jwt_required)])
def delete_adjustment_inventory_router(
    adjustment_id: UUID,
    db: Session = Depends(get_db)
):
    """
    Delete an inventory adjustment record and reverse the adjustment
    
    **Path parameters:**
    - adjustment_id: UUID of the adjustment to delete
    
    **Notes:**
    - Deleting an adjustment will reverse its effect on inventory
    - The quantity adjustment will be reversed automatically
    """
    try:
        result = delete_inventory_adjustment(db, adjustment_id)
        if not result:
            return error_response(message="Failed to delete adjustment")
        return success_response(data=result, message="Adjustment deleted and reversed successfully")
    except ValueError as e:
        return error_response(message=str(e), status_code=404)
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


# Keep generic product mutation routes last so static paths such as /cost are
# matched before /{product_id}.
@router.put(
    "/{product_id}",
    response_model=ProductMutationResponse,
    responses={
        404: {"model": ApiErrorResponse, "description": "Product not found"},
        422: {"model": ApiErrorResponse, "description": "Invalid product ID or update payload"},
        500: {"model": ApiErrorResponse, "description": "Unexpected database error"},
    },
    dependencies=[Depends(jwt_required)],
)
def update_product_router(
    product_id: UUID,
    product_data: UpdateProduct,
    db: Session = Depends(get_db),
):
    try:
        result = update_product(db, product_id, product_data)
        return success_response(data=result, message="Product updated successfully")
    except LookupError as exc:
        return error_response(message=str(exc), status_code=404)
    except ValueError as exc:
        return error_response(message=str(exc), status_code=422)
    except Exception:
        db.rollback()
        return error_response(message="Failed to update product", status_code=500)


@router.delete(
    "/{product_id}",
    response_model=ProductDeleteResponse,
    responses={
        404: {"model": ApiErrorResponse, "description": "Product not found"},
        409: {"model": ApiErrorResponse, "description": "Product is referenced by transactional data"},
        500: {"model": ApiErrorResponse, "description": "Unexpected database error"},
    },
    dependencies=[Depends(jwt_required)],
)
def delete_product_router(
    product_id: UUID,
    db: Session = Depends(get_db),
):
    try:
        delete_product(db, product_id)
        return success_response(message="Product deleted successfully")
    except LookupError as exc:
        return error_response(message=str(exc), status_code=404)
    except ProductInUseError as exc:
        return error_response(message=str(exc), status_code=409)
    except Exception:
        db.rollback()
        return error_response(message="Failed to delete product", status_code=500)





