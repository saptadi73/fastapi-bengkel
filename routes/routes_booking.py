from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from models.database import SessionLocal
from services.services_booking import createBookingnya,get_all_bookings, get_booking_by_id, edit_booking, del_booking
from schemas.service_booking import CreateBooking,UpdateBookingFromNew, BookingResponse
from services.services_customer import create_customer_with_vehicles,getListCustomersWithvehicles, getListCustomersWithVehiclesCustomersID
from services.services_product import CreateProductNew, get_all_products, get_product_by_id, createServicenya,get_all_services, createBrandnya, createCategorynya, createSatuannya, getAllBrands, getAllCategories, getAllSatuans, getAllInventoryProducts, getInventoryByProductID, createProductMoveHistoryNew
from services.services_workorder import createNewWorkorder,getAllWorkorders, getWorkorderByID, updateServiceorderedOnlynya,updateStatusWorkorder,updateWorkOrdeKeluhannya,UpdateDateWorkordernya,UpdateWorkorderOrdersnya,updateProductOrderedOnlynya,createNewWorkorderActivityLog, updateWorkorderActivityLognya,get_workorder_activitylog_by_customer,UpdateWorkorderOrdersnya
from schemas.service_inventory import CreateProductMovedHistory
from schemas.service_product import CreateProduct, ProductResponse, CreateService, ServiceResponse
from schemas.service_workorder import CreateWorkOrder,UpdateProductOrderedOnly,UpdateServiceOrderedOnly,UpdateWorkoderOrders,UpdateWorkorderComplaint,UpdateWorkorderDates,UpdateWorkorderStatus,UpdateWorkorderTotalCost,DeleteProductOrderedOnly,DeleteServiceOrderedOnly, CreateWorkActivityLog
from supports.utils_json_response import success_response, error_response
from middleware.jwt_required import jwt_required
from schemas.service_customer import CreateCustomerWithVehicles, CustomerWithVehicleResponse

router = APIRouter(prefix="/bookings", tags=["Booking"])

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("/create/new")
def create_booking_router(
    booking_data: CreateBooking,
    db: Session = Depends(get_db)
):
    try:
        result = createBookingnya(db, booking_data)
        if not result:
            return error_response(message="Failed to create booking")
        return success_response(data=result,message='Success Create Booking', status_code=201)
    except Exception as e:
        return error_response(message=str(e))   
    finally:
        db.close()

@router.get("/all", response_model=list[CreateBooking])
def list_all_bookings(
    db: Session = Depends(get_db)
):
    try:
        result = get_all_bookings(db)
        return success_response(data=result)
    except Exception as e:
        return error_response(message=str(e))   
    finally:
        db.close()

@router.get("/{booking_id}", response_model=CreateBooking)
def get_booking(
    booking_id: str,
    db: Session = Depends(get_db)
):
    try:
        result = get_booking_by_id(db, booking_id)
        if not result:
            raise HTTPException(status_code=404, detail="Booking not found")
        return success_response(data=result)
    except Exception as e:
        return error_response(message=str(e))   
    finally:
        db.close()

@router.post("/edit/{booking_id}", dependencies=[Depends(jwt_required)])
def edit_booking_router(
    booking_id: str,
    booking_data: UpdateBookingFromNew,
    db: Session = Depends(get_db)
):
    try:
        result = edit_booking(db, booking_id, booking_data)
        if not result:
            return error_response(message="Failed to edit booking")
        return success_response(data=result,message='Success Edit Booking', status_code=200)
    except Exception as e:
        return error_response(message=str(e))
    finally:
        db.close()

@router.get("/delete/{booking_id}", dependencies=[Depends(jwt_required)])
def delete_booking_router(
    booking_id: str,
    db: Session = Depends(get_db)
):
    try:
        result = del_booking(db, booking_id)
        if not result:
            return error_response(message="Failed to delete booking")
        return success_response(data={"deleted": True},message='Success Delete Booking', status_code=200)
    except Exception as e:
        return error_response(message=str(e))
    finally:
        db.close()
