from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from services.services_inventory import get_or_create_inventory, createProductMoveHistoryNew, generate_product_move_history_report, createProductMoveHistoryNewLoss, updateCostCostingMethodeAverage
from services.services_inventory_extended import update_inventory_loss, delete_inventory_loss, get_loss_by_id, get_inventory_losses
from uuid import UUID
from schemas.service_inventory import CreateProductMovedHistory, ProductMoveHistoryReportRequest, ProductMoveHistoryReport, PurchaseOrderUpdateCost
from models.database import SessionLocal
from supports.utils_json_response import success_response, error_response
from middleware.jwt_required import jwt_required


router = APIRouter(prefix="/inventory", tags=["Inventory"])

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()



@router.get("/{product_id}")
def get_inventory(
    product_id: str,
    db: Session = Depends(get_db)
):
    try:
        result = get_or_create_inventory(db, product_id)
        if not result:
            return error_response(message="Failed to get or create inventory")
        return success_response(data=result)
    except Exception as e:
        return error_response(message=str(e))

@router.post("/product-move-history-report", response_model=ProductMoveHistoryReport)
def generate_product_move_history_report_route(request: ProductMoveHistoryReportRequest, db: Session = Depends(get_db)):
    try:
        result = generate_product_move_history_report(db, request)
        return success_response(data=result.model_dump(mode='json'))
    except Exception as e:
        return error_response(message=str(e))
    
@router.post("/move/new", dependencies=[Depends(jwt_required)])
def product_move_router(
    data_move: CreateProductMovedHistory,
    db: Session = Depends(get_db)
):
    try:
        result = createProductMoveHistoryNew(db, data_move)
        return success_response(data=result)
    except Exception as e:
        return error_response(message=str(e))
    
@router.post("/move/loss", dependencies=[Depends(jwt_required)])
def product_move_loss_router(
    data_move: CreateProductMovedHistory,
    db: Session = Depends(get_db)
):
    try:
        result = createProductMoveHistoryNewLoss(db, data_move)
        return success_response(data=result)
    except Exception as e:
        return error_response(message=str(e))


@router.get("/loss")
def list_loss_inventory_router(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    try:
        result = get_inventory_losses(db, skip, limit)
        return success_response(
            data=result,
            message=f"Retrieved {len(result)} loss records"
        )
    except Exception as e:
        return error_response(message=str(e))


@router.get("/loss/{loss_id}")
def get_loss_inventory_router(
    loss_id: UUID,
    db: Session = Depends(get_db)
):
    try:
        result = get_loss_by_id(db, loss_id)
        return success_response(data=result)
    except ValueError as e:
        return error_response(message=str(e), status_code=404)
    except Exception as e:
        return error_response(message=str(e))

@router.put("/loss/{loss_id}", dependencies=[Depends(jwt_required)])
def update_loss_inventory_router(
    loss_id: UUID,
    loss_data: CreateProductMovedHistory,
    db: Session = Depends(get_db)
):
    """
    Update an existing inventory loss record
    
    **Path parameters:**
    - loss_id: UUID of the loss record to update
    
    **Request body:**
    - product_id: Product ID
    - quantity: Loss quantity
    - reason: Reason for loss
    - performed_by: User recording the loss
    - notes: Additional notes
    
    **Notes:**
    - Updating a loss will adjust inventory accordingly
    """
    try:
        result = update_inventory_loss(db, loss_id, loss_data.model_dump(exclude_unset=True))
        if not result:
            return error_response(message="Failed to update loss record")
        return success_response(data=result, message="Loss record updated successfully")
    except ValueError as e:
        return error_response(message=str(e), status_code=404)
    except Exception as e:
        return error_response(message=str(e))

@router.delete("/loss/{loss_id}", dependencies=[Depends(jwt_required)])
def delete_loss_inventory_router(
    loss_id: UUID,
    db: Session = Depends(get_db)
):
    """
    Delete an inventory loss record and reverse the loss
    
    **Path parameters:**
    - loss_id: UUID of the loss record to delete
    
    **Notes:**
    - Deleting a loss will reverse its effect on inventory
    - The lost quantity will be added back to inventory automatically
    """
    try:
        result = delete_inventory_loss(db, loss_id)
        if not result:
            return error_response(message="Failed to delete loss record")
        return success_response(data=result, message="Loss record deleted and reversed successfully")
    except ValueError as e:
        return error_response(message=str(e), status_code=404)
    except Exception as e:
        return error_response(message=str(e))

@router.post("/update-cost", dependencies=[Depends(jwt_required)])
def update_cost_route(
    data: PurchaseOrderUpdateCost,
    db: Session = Depends(get_db)
):
    try:
        result = updateCostCostingMethodeAverage(db, data)
        return success_response(data=result)
    except Exception as e:
        return error_response(message=str(e))

