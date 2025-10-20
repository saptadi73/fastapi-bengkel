from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import os

from routes import routes_customer, routes_auth, routes_product, routes_workorder,routes_booking, routes_packet_order, routes_karyawan, routes_accounting, routes_supplier, routes_purchase_order, routes_expenses, routes_inventory, routes_attendance

app = FastAPI()

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Ganti dengan list domain jika perlu
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Ensure uploads directory exists
os.makedirs("uploads", exist_ok=True)

# Mount static files
app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")

# Include all routers
app.include_router(routes_auth.router)
app.include_router(routes_booking.router)
app.include_router(routes_workorder.router)
app.include_router(routes_product.router)
app.include_router(routes_customer.router)

app.include_router(routes_packet_order.router)
app.include_router(routes_karyawan.router)
app.include_router(routes_accounting.router)
app.include_router(routes_supplier.router)
app.include_router(routes_purchase_order.router)
app.include_router(routes_expenses.router)
app.include_router(routes_inventory.router)
app.include_router(routes_attendance.router)

@app.get("/")
def root():
    return {"message": "API is running"}
