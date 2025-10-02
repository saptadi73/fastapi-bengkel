
from pydantic import BaseModel
from uuid import UUID
from typing import Optional
from datetime import datetime



# ProductOrder schema
class CreateProductOrder(BaseModel):
    product_id: UUID
    quantity: float
    satuan: Optional[str] = None
    harga: Optional[float] = None
    subtotal: float
    discount: Optional[float] = 0


# ServiceOrder schema
class CreateServiceOrder(BaseModel):
    service_id: UUID
    quantity: float
    satuan: Optional[str] = None
    harga: Optional[float] = None
    subtotal: float
    discount: Optional[float] = 0


# WorkOrder schema
class CreateWorkOrder(BaseModel):
    tanggal_masuk: datetime
    tanggal_keluar: Optional[datetime] = None
    keluhan: Optional[str] = None
    saran: Optional[str] = None
    status: str
    total_discount: Optional[float] = 0
    total_biaya: float = 0
    pajak: Optional[float] = 0
    customer_id: UUID
    vehicle_id: UUID
    product_ordered: Optional[list[CreateProductOrder]] = None
    service_ordered: Optional[list[CreateServiceOrder]] = None

class CreateWorkorderOnly(BaseModel):
    tanggal_masuk: datetime
    tanggal_keluar: Optional[datetime] = None
    keluhan: Optional[str] = None
    saran: Optional[str] = None
    status: str
    pajak: Optional[float] = 0
    total_discount: Optional[float] = 0
    total_biaya: float
    customer_id: UUID
    vehicle_id: UUID

class CreateServiceOrderedOnly(BaseModel):
    workorder_id: UUID
    service_id: UUID
    quantity: float
    subtotal: float
    discount: Optional[float] = 0
    performed_by: Optional[str] = 'system'
class CreateProductOrderedOnly(BaseModel):
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
    quantity: float
    subtotal: float
    discount: Optional[float] = 0
    performed_by: Optional[str] = 'system'

class UpdateServiceOrderedOnly(BaseModel):
    workorder_id: UUID
    service_id: UUID
    quantity: float
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


class CreateWorkActivityLog(BaseModel):
    workorder_id: UUID
    action: str
    timestamp: Optional[datetime] = None
    performed_by: str

class UpdateWorkoderOrders(BaseModel):
    workorder_id: UUID
    products: Optional[list[UpdateProductOrderedOnly]] = None
    services: Optional[list[UpdateServiceOrderedOnly]] = None
    performed_by: Optional[str] = 'system'