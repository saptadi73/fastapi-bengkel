from pydantic import BaseModel
from uuid import UUID
from typing import Optional
from datetime import datetime



# ProductOrder schema
class CreateProductOrder(BaseModel):
    id: Optional[UUID] = None
    product_id: UUID
    quantity: float
    satuan_id: Optional[UUID] = None
    price: Optional[float] = None
    subtotal: float
    discount: Optional[float] = 0
    cost: Optional[float] = None
    productSubtotalHPP: Optional[float] = None
    stockku: Optional[float] = None
    product_name: Optional[str] = None


# ServiceOrder schema
class CreateServiceOrder(BaseModel):
    id: Optional[UUID] = None
    service_id: UUID
    quantity: float
    satuan: Optional[str] = None
    price: Optional[float] = None
    subtotal: float
    discount: Optional[float] = 0
    cost: Optional[float] = None
    serviceSubtotal: Optional[float] = None
    serviceSubtotalHPP: Optional[float] = None
    service_name: Optional[str] = None
    workorder_id: Optional[UUID] = None


# WorkOrder schema
class CreateWorkOrder(BaseModel):
    tanggal_masuk: datetime
    tanggal_keluar: Optional[datetime] = None
    keluhan: str
    kilometer: Optional[float] = None
    saran: Optional[str] = None
    status: str
    status_pembayaran: Optional[str] = None
    update_pembayaran: Optional[float] = None
    total_discount: Optional[float] = 0
    total_biaya: float = 0
    pajak: Optional[float] = 0
    customer_id: UUID
    vehicle_id: UUID
    karyawan_id: Optional[UUID] = None

    totalProductHarga: Optional[float]=0
    totalProductDiscount: Optional[float]=0
    totalProductCost: Optional[float]=0

    totalServiceHarga:Optional[float]=0
    totalServiceDiscount:Optional[float]=0
    totalServiceCost: Optional[float]=0

    product_ordered: Optional[list[CreateProductOrder]] = None
    service_ordered: Optional[list[CreateServiceOrder]] = None

    model_config = {"extra": "ignore"}

class CreateWorkorderOnly(BaseModel):
    tanggal_masuk: datetime
    tanggal_keluar: Optional[datetime] = None
    keluhan: str
    kilometer: Optional[float] = None
    saran: Optional[str] = None
    status: str
    status_pembayaran: Optional[str] = None
    update_pembayaran: Optional[float] = None
    pajak: Optional[float] = 0
    total_discount: Optional[float] = 0
    total_biaya: float
    customer_id: UUID
    vehicle_id: UUID

class CreateServiceOrderedOnly(BaseModel):
    id: Optional[UUID] = None
    workorder_id: UUID
    service_id: UUID
    quantity: float
    subtotal: float
    discount: Optional[float] = 0
    performed_by: Optional[str] = 'system'

class CreateProductOrderedOnly(BaseModel):
    id: Optional[UUID] = None
    workorder_id: UUID
    product_id: UUID
    quantity: float
    subtotal: float
    discount: Optional[float] = 0
    performed_by: Optional[str] = 'system'

class WorkOrderResponse(BaseModel):
    id: UUID
    no_wo: str
    tanggal_masuk: datetime
    tanggal_keluar: Optional[datetime] = None
    keluhan: Optional[str] = None
    saran: Optional[str] = None
    status: str
    status_pembayaran: Optional[str] = None
    update_pembayaran: Optional[float] = None
    total_discount: Optional[float] = 0
    total_biaya: float
    customer_id: UUID
    vehicle_id: UUID
    product_ordered: Optional[list[CreateProductOrder]] = None
    service_ordered: Optional[list[CreateServiceOrder]] = None

    model_config = {
        "from_attributes": True
    }

class UpdateWorkorderStatus(BaseModel):
    workorder_id: UUID
    status: str
    performed_by: Optional[str] = 'system'

class UpdateWorkorderDates(BaseModel):
    workorder_id: UUID
    tanggal_masuk: Optional[datetime] = None
    tanggal_keluar: Optional[datetime] = None
    performed_by: Optional[str] = 'system'

class UpdateWorkorderComplaint(BaseModel):
    workorder_id: UUID
    keluhan: str
    performed_by: Optional[str] = 'system'

class UpdateWorkorderTotalCost(BaseModel):
    workorder_id: UUID
    total_discount: Optional[float] = 0
    total_biaya: float
    performed_by: Optional[str] = 'system'

class UpdateProductOrderedOnly(BaseModel):
    workorder_id: UUID
    product_id: UUID
    price: Optional[float] = None
    quantity: float
    subtotal: float
    discount: Optional[float] = 0
    performed_by: Optional[str] = 'system'

class UpdateServiceOrderedOnly(BaseModel):
    workorder_id: UUID
    service_id: UUID
    quantity: float
    price: Optional[float] = None
    subtotal: float
    discount: Optional[float] = 0
    performed_by: Optional[str] = 'system'

class DeleteProductOrderedOnly(BaseModel):
    workorder_id: UUID
    product_id: UUID
    performed_by: Optional[str] = 'system'

class DeleteServiceOrderedOnly(BaseModel):
    workorder_id: UUID
    service_id: UUID
    performed_by: Optional[str] = 'system'

class addServiceOrderedOnly(BaseModel):
    workorder_id: UUID
    service_id: UUID
    quantity: float
    subtotal: float
    discount: Optional[float] = 0
    performed_by: Optional[str] = 'system'

class addProductOrderedOnly(BaseModel):
    workorder_id: UUID
    product_id: UUID
    quantity: float
    subtotal: float
    discount: Optional[float] = 0
    performed_by: Optional[str] = 'system'




class UpdateWorkoderOrders(BaseModel):
    workorder_id: UUID
    products: Optional[list[UpdateProductOrderedOnly]] = None
    services: Optional[list[UpdateServiceOrderedOnly]] = None
    performed_by: Optional[str] = 'system'

class AddProductOrderById(BaseModel):
    workorder_id: UUID
    product_id: UUID
    quantity: float
    subtotal: float
    discount: Optional[float] = 0
    satuan_id: Optional[UUID] = None
    price: Optional[float] = None
    performed_by: Optional[str] = 'system'

class UpdateProductOrderById(BaseModel):
    product_id: Optional[UUID] = None
    quantity: Optional[float] = None
    subtotal: Optional[float] = None
    discount: Optional[float] = None
    satuan_id: Optional[UUID] = None
    price: Optional[float] = None
    performed_by: Optional[str] = 'system'

class DeleteProductOrderById(BaseModel):
    performed_by: Optional[str] = 'system'

class AddServiceOrderById(BaseModel):
    workorder_id: UUID
    service_id: UUID
    quantity: float
    subtotal: float
    discount: Optional[float] = 0
    price: Optional[float] = None
    performed_by: Optional[str] = 'system'

class UpdateServiceOrderById(BaseModel):
    service_id: Optional[UUID] = None
    quantity: Optional[float] = None
    subtotal: Optional[float] = None
    discount: Optional[float] = None
    price: Optional[float] = None
    performed_by: Optional[str] = 'system'

class DeleteServiceOrderById(BaseModel):
    performed_by: Optional[str] = 'system'
