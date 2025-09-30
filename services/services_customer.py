from sqlalchemy.orm import Session
from models.customer import Customer, Vehicle
import uuid
from schemas.service_customer import CreateCustomerWithVehicles
from models.database import get_db
from schemas.service_customer import CustomerWithVehicleResponse, CreateCustomer, CreateVehicle
from schemas.service_vehicle import VehicleResponse, CreateVehicle
import decimal
import datetime
from dateutil.relativedelta import relativedelta

def to_dict(obj):
    result = {}
    for c in obj.__table__.columns:
        value = getattr(obj, c.name)
        # Konversi UUID ke string
        if isinstance(value, uuid.UUID):
            value = str(value)
        # Konversi Decimal ke float
        elif isinstance(value, decimal.Decimal):
            value = float(value)
        # Konversi datetime/date/time ke isoformat string
        elif isinstance(value, (datetime.datetime, datetime.date, datetime.time)):
            value = value.isoformat()
        # Konversi bytes ke string (opsional, jika ada kolom bytes)
        elif isinstance(value, bytes):
            value = value.decode('utf-8')
        result[c.name] = value
    return result

def create_customer_with_vehicles(db: Session, customer_data: CreateCustomerWithVehicles):
    # Create a new customer
    new_customer = Customer(
        id=str(uuid.uuid4()),
        nama=customer_data.nama,
        hp=customer_data.hp,
        alamat=customer_data.alamat,
        email=customer_data.email
    )
    db.add(new_customer)
    db.commit()
    db.refresh(new_customer)

    # Create a new vehicle associated with the customer
    new_vehicle = Vehicle(
        id=str(uuid.uuid4()),
        model=customer_data.model,
        brand_id=customer_data.brand_id,
        type=customer_data.type,
        kapasitas=customer_data.kapasitas,
        no_pol=customer_data.no_pol,
        tahun=customer_data.tahun,
        warna=customer_data.warna,
        customer_id=new_customer.id
    )
    db.add(new_vehicle)
    db.commit()
    db.refresh(new_vehicle)

    return {
        "customer": to_dict(new_customer),
        "vehicle": to_dict(new_vehicle)
    }

def getListCustomersWithvehicles(db: Session):
    # customers = db.query(Customer).all()
    # result = []
    # for customer in customers:
    #     customer_dict = to_dict(customer)
    #     vehicles = []
    #     for vehicle in customer.vehicles:
    #         v_dict = to_dict(vehicle)
    #         # Tambahkan brand_name jika relasi brand ada
    #         v_dict['brand_name'] = vehicle.brand.name if vehicle.brand else None
    #         vehicles.append(v_dict)
    #     customer_dict['vehicles'] = vehicles
    #     result.append(customer_dict)
    # return result
    vehicles = db.query(Vehicle).all()
    result = []
    for vehicle in vehicles:
        v_dict = to_dict(vehicle)
        v_dict['brand_name'] = vehicle.brand.name if vehicle.brand else None
        customer = vehicle.customer
        if customer:
            v_dict['customer_nama'] = customer.nama
            v_dict['customer_hp'] = customer.hp
            v_dict['customer_alamat'] = customer.alamat
        else:
            v_dict['customer_nama'] = None
            v_dict['customer_hp'] = None
            v_dict['customer_alamat'] = None

        # Cari tanggal_keluar terakhir dari workorder kendaraan ini
        last_wo = None
        if hasattr(vehicle, 'workorders'):
            workorders = vehicle.workorders
            if workorders:
                # Ambil workorder dengan tanggal_keluar paling akhir (bisa None)
                last_wo = max(
                    (wo for wo in workorders if wo.tanggal_keluar is not None),
                    key=lambda wo: wo.tanggal_keluar,
                    default=None
                )

        # last_visit_date dan next_visit_date
        if last_wo and last_wo.tanggal_keluar:
            last_visit = last_wo.tanggal_keluar
            v_dict['last_visit_date'] = last_visit.isoformat()
            # Tambahkan 4 bulan ke last_visit
            try:
                next_visit = last_visit + relativedelta(months=4)
            except ImportError:
                # Fallback jika dateutil tidak ada, pakai timedelta 120 hari
                from datetime import timedelta
                next_visit = last_visit + timedelta(days=90)
            v_dict['next_visit_date'] = next_visit.isoformat()
        else:
            v_dict['last_visit_date'] = None
            v_dict['next_visit_date'] = None

        v_dict['customer'] = to_dict(customer) if customer else None
        result.append(v_dict)
    return result

def getListCustomersWithvehiclesId(db: Session, vehicle_id: str):
    # Query a single vehicle by vehicle_id
    vehicle = db.query(Vehicle).filter(Vehicle.id == vehicle_id).first()  # Get a single vehicle
    
    if not vehicle:
        return []  # Return empty list if no vehicle is found

    result = []
    
    v_dict = to_dict(vehicle)
    v_dict['brand_name'] = vehicle.brand.name if vehicle.brand else None
    
    customer = vehicle.customer  # Directly access the related customer object
    if customer:
        v_dict['customer_nama'] = customer.nama
        v_dict['customer_hp'] = customer.hp
        v_dict['customer_alamat'] = customer.alamat
    else:
        v_dict['customer_nama'] = None
        v_dict['customer_hp'] = None
        v_dict['customer_alamat'] = None

    # Find the last work order with a non-null `tanggal_keluar`
    last_wo = None
    if hasattr(vehicle, 'workorders'):
        workorders = vehicle.workorders
        if workorders:
            last_wo = max(
                (wo for wo in workorders if wo.tanggal_keluar is not None),
                key=lambda wo: wo.tanggal_keluar,
                default=None
            )

    # Set last visit date and next visit date based on the last work order
    if last_wo and last_wo.tanggal_keluar:
        last_visit = last_wo.tanggal_keluar
        v_dict['last_visit_date'] = last_visit.isoformat()
        try:
            next_visit = last_visit + relativedelta(months=4)  # Adds 4 months to last visit date
        except ImportError:
            from datetime import timedelta
            next_visit = last_visit + timedelta(days=120)  # Fallback if `dateutil` is not available
        v_dict['next_visit_date'] = next_visit.isoformat()
    else:
        v_dict['last_visit_date'] = None
        v_dict['next_visit_date'] = None

    v_dict['customer'] = to_dict(customer) if customer else None
    result.append(v_dict)
    
    return result


def getServiceOrderedAndProductOrderedByVehicleID(db: Session, vehicle_id: str):
    vehicle = db.query(Vehicle).filter(Vehicle.id == vehicle_id).first()
    if not vehicle:
        return None
    vehicle_dict = to_dict(vehicle)
    workorders = []
    from collections import defaultdict
    all_orders_dict = defaultdict(lambda: {
        'tanggal': None,
        'keluhan': None,
        'no_wo': None,
        'product_names': [],
        'service_names': []
    })
    for wo in sorted(vehicle.workorders, key=lambda w: w.tanggal_masuk or w.tanggal_keluar or '', reverse=False):
        wo_dict = to_dict(wo)
        service_orders = []
        product_orders = []
        tanggal_wo = wo.tanggal_masuk or wo.tanggal_keluar
        tanggal_str = tanggal_wo.isoformat() if isinstance(tanggal_wo, (datetime.datetime, datetime.date)) else tanggal_wo
        key = (tanggal_str, wo.keluhan, wo.no_wo)
        for so in wo.service_ordered:
            so_dict = to_dict(so)
            so_dict['service_name'] = so.service.name if so.service else None
            if so_dict['service_name']:
                all_orders_dict[key]['tanggal'] = tanggal_str
                all_orders_dict[key]['keluhan'] = wo.keluhan
                all_orders_dict[key]['no_wo'] = wo.no_wo
                all_orders_dict[key]['service_names'].append(so_dict['service_name'])
            service_orders.append(so_dict)
        for po in wo.product_ordered:
            po_dict = to_dict(po)
            po_dict['product_name'] = po.product.name if po.product else None
            if po_dict['product_name']:
                all_orders_dict[key]['tanggal'] = tanggal_str
                all_orders_dict[key]['keluhan'] = wo.keluhan
                all_orders_dict[key]['no_wo'] = wo.no_wo
                all_orders_dict[key]['product_names'].append(po_dict['product_name'])
            product_orders.append(po_dict)
        wo_dict['service_ordered'] = service_orders
        wo_dict['product_ordered'] = product_orders
        workorders.append(wo_dict)
    # Ubah dict ke list dan urutkan berdasarkan tanggal
    all_orders = list(all_orders_dict.values())
    all_orders = sorted(all_orders, key=lambda x: x['tanggal'] or '', reverse=False)
    vehicle_dict['workorders'] = workorders
    vehicle_dict['all_orders'] = all_orders
    return vehicle_dict

def getListCustomersWithVehiclesCustomersID(db: Session, customer_id: str):
    customer = db.query(Customer).filter(Customer.id == customer_id).first()
    if not customer:
        return None
    customer_dict = to_dict(customer)
    vehicles = []
    for vehicle in customer.vehicles:
        v_dict = to_dict(vehicle)
        v_dict['brand_name'] = vehicle.brand.name if vehicle.brand else None
        vehicles.append(v_dict)
    customer_dict['vehicles'] = vehicles
    return customer_dict

def createCustomerOnly(db: Session, customer_data: CreateCustomer):
    new_customer = Customer(
        id=str(uuid.uuid4()),
        nama=customer_data.nama,
        hp=customer_data.hp,
        alamat=customer_data.alamat,
        email=customer_data.email,
        tanggal_lahir=customer_data.tanggal_lahir,
        created_at=datetime.datetime.now().isoformat(),
        updated_at=datetime.datetime.now().isoformat()
    )
    db.add(new_customer)
    db.commit()
    db.refresh(new_customer)
    return to_dict(new_customer)

def getAllCustomers(db: Session):
    customers = db.query(Customer).all()
    result = []
    for customer in customers:
        customer_dict = to_dict(customer)
        result.append(customer_dict)
    return result

def createVehicletoCustomer(db: Session, CreateVehicle):
    new_vehicle = Vehicle(
        id=str(uuid.uuid4()),
        model=CreateVehicle.model,
        brand_id=CreateVehicle.brand_id,
        type=CreateVehicle.type,
        kapasitas=CreateVehicle.kapasitas,
        no_pol=CreateVehicle.no_pol,
        tahun=CreateVehicle.tahun,
        warna=CreateVehicle.warna,
        no_mesin=CreateVehicle.no_mesin,
        no_rangka=CreateVehicle.no_rangka,
        customer_id=CreateVehicle.customer_id
    )
    db.add(new_vehicle)
    db.commit()
    db.refresh(new_vehicle)
    return to_dict(new_vehicle)
