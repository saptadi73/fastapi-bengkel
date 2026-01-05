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
from contextlib import suppress
from typing import DefaultDict, List, Optional, Tuple, TypedDict


class AggregatedOrder(TypedDict):
    """Typed structure for grouped work order data."""

    tanggal: Optional[str]
    keluhan: Optional[str]
    no_wo: Optional[str]
    product_names: List[str]
    service_names: List[str]


AggregatedKey = Tuple[Optional[str], Optional[str], Optional[str]]

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
    try:
        # Satu transaksi saja
        with db.begin():  # otomatis commit di akhir, rollback kalau exception
            # 1) Insert Customer
            new_customer = Customer(
                id=str(uuid.uuid4()),                     # kalau server-side default, id bisa dibiarkan None
                nama=customer_data.nama,
                hp=customer_data.hp,
                alamat=customer_data.alamat,
                tanggal_lahir=customer_data.tanggal_lahir,
                email=customer_data.email,
            )
            db.add(new_customer)
            db.flush()  # pastikan new_customer.id sudah tersedia

            # 2) Insert Vehicle terkait customer barusan
            new_vehicle = Vehicle(
                id=str(uuid.uuid4()),
                model=customer_data.model,
                brand_id=customer_data.brand_id,
                type=customer_data.type,
                kapasitas=customer_data.kapasitas,
                no_pol=customer_data.no_pol,
                tahun=customer_data.tahun,
                warna=customer_data.warna,
                no_mesin=customer_data.no_mesin,
                no_rangka=customer_data.no_rangka,
                customer_id=new_customer.id,  # refer ke PK yang baru di-flush
            )
            db.add(new_vehicle)
            db.flush()  # pastikan new_vehicle.id sudah tersedia

            # (opsional) tidak perlu refresh; flush sudah cukup untuk dapatkan PK

        # Di titik ini transaksi sudah commit (karena with db.begin())
        return {
            # kalau mau tetap kirim objek:
            "customer": to_dict(new_customer),
            "vehicle": to_dict(new_vehicle),
        }

    except Exception as e:
        # pastikan rollback kalau begin tidak menanganinya (cadangan)
        with suppress(Exception):
            db.rollback()
        raise


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
            v_dict['id_customer'] = str(customer.id)  # Tambahkan untuk WhatsApp report tracking
        else:
            v_dict['customer_nama'] = None
            v_dict['customer_hp'] = None
            v_dict['customer_alamat'] = None
            v_dict['id_customer'] = None

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
    all_orders_dict: DefaultDict[AggregatedKey, AggregatedOrder] = defaultdict(
        lambda: {
            'tanggal': None,
            'keluhan': None,
            'no_wo': None,
            'product_names': [],
            'service_names': []
        }
    )
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


def send_maintenance_reminder_whatsapp(db: Session):
    """
    Fungsi untuk mengirim reminder WhatsApp ke customer yang jadwal maintenance-nya
    kurang dari 3 hari.
    
    Logic:
    - Ambil daftar customer dengan vehicle dari getListCustomersWithvehicles
    - Cek setiap vehicle apakah next_visit_date kurang dari 3 hari dari hari ini
    - Jika ya, kirim pesan WhatsApp dengan format yang ditentukan
    - Update tracking di whatsapp_report table
    
    Returns:
        Dict berisi:
        {
            "total_customers": int,
            "reminder_sent": int,
            "details": list of dicts with vehicle info dan status pengiriman
        }
    """
    from datetime import datetime, timedelta
    from services.services_whatsapp import send_whatsapp_message_sync
    from services.services_whatsapp_report import create_or_update_whatsapp_report
    
    try:
        # Ambil daftar customer dengan vehicle
        customers_vehicles = getListCustomersWithvehicles(db)
        
        if not customers_vehicles:
            return {
                "total_customers": 0,
                "reminder_sent": 0,
                "details": []
            }
        
        today = datetime.now().date()
        reminder_sent = 0
        details = []
        
        for vehicle_data in customers_vehicles:
            customer_nama = vehicle_data.get('customer_nama')
            customer_hp = vehicle_data.get('customer_hp')
            no_pol = vehicle_data.get('no_pol')
            next_visit_date_str = vehicle_data.get('next_visit_date')
            customer_id = vehicle_data.get('id_customer') or vehicle_data.get('customer_id')
            vehicle_id = vehicle_data.get('id')
            
            # Skip jika data tidak lengkap
            if not all([customer_nama, customer_hp, no_pol, next_visit_date_str]):
                details.append({
                    "no_pol": no_pol,
                    "customer_nama": customer_nama,
                    "status": "skipped",
                    "reason": "Data tidak lengkap"
                })
                continue
            
            # Parse next_visit_date (format ISO string: YYYY-MM-DD)
            try:
                next_visit_date = datetime.fromisoformat(next_visit_date_str).date()
            except (ValueError, TypeError):
                details.append({
                    "no_pol": no_pol,
                    "customer_nama": customer_nama,
                    "status": "skipped",
                    "reason": "Format next_visit_date tidak valid"
                })
                continue
            
            # Hitung selisih hari antara hari ini dan next_visit_date
            days_until_visit = (next_visit_date - today).days
            
            # Jika kurang dari 3 hari (0, 1, 2 hari sebelumnya), kirim reminder
            if 0 <= days_until_visit < 3:
                try:
                    # Format nomor HP jika perlu (pastikan format 62)
                    phone = customer_hp.strip()
                    if phone.startswith('0'):
                        phone = '62' + phone[1:]
                    elif not phone.startswith('62'):
                        phone = '62' + phone
                    
                    # Format pesan
                    message = f"Bapak {customer_nama} untuk nomor kendaraan {no_pol} sebentar lagi tiba saat pemeliharaan rutin pada tanggal {next_visit_date.strftime('%d-%m-%Y')}, daftarkan segera melalui nomor pelayanan kami 08551000727"
                    
                    # Kirim WhatsApp
                    from schemas.service_whatsapp import WhatsAppMessageCreate
                    msg_data = WhatsAppMessageCreate(
                        message_type="text",
                        to=phone,
                        body=message,
                        file=None,
                        delay=None,
                        schedule=None
                    )
                    result = send_whatsapp_message_sync(msg_data)
                    
                    # Update WhatsApp report tracking (jika customer_id dan vehicle_id tersedia)
                    if customer_id and vehicle_id:
                        try:
                            create_or_update_whatsapp_report(db, customer_id, vehicle_id)
                        except Exception as report_error:
                            # Log error tapi jangan stop pengiriman
                            import logging
                            logger = logging.getLogger(__name__)
                            logger.warning(f"Error updating whatsapp report for {no_pol}: {str(report_error)}")
                    
                    reminder_sent += 1
                    details.append({
                        "no_pol": no_pol,
                        "customer_nama": customer_nama,
                        "customer_hp": customer_hp,
                        "next_visit_date": next_visit_date.isoformat(),
                        "days_until_visit": days_until_visit,
                        "status": "sent",
                        "message": message,
                        "api_response": result.get("message") if isinstance(result, dict) else str(result)
                    })
                
                except Exception as e:
                    details.append({
                        "no_pol": no_pol,
                        "customer_nama": customer_nama,
                        "status": "failed",
                        "reason": str(e)
                    })
        
        return {
            "total_customers": len(customers_vehicles),
            "reminder_sent": reminder_sent,
            "details": details
        }
    
    except Exception as e:
        raise Exception(f"Error dalam send_maintenance_reminder_whatsapp: {str(e)}")
