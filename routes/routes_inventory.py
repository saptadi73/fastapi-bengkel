from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from services.services_inventory import get_or_create_inventory, createProductMoveHistoryNew
from schemas.service_inventory import CreateProductMovedHistory
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

