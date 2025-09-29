from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from routes import routes_customer, routes_auth, routes_product, routes_workorder,routes_booking, routes_packet_order

app = FastAPI()

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Ganti dengan list domain jika perlu
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Include all routers
app.include_router(routes_booking.router)
app.include_router(routes_workorder.router)
app.include_router(routes_product.router)
app.include_router(routes_customer.router)
app.include_router(routes_auth.router)
app.include_router(routes_packet_order.router)

@app.get("/")
def root():
    return {"message": "API is running"}
