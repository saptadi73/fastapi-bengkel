from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from routes import routes_customer, routes_auth

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
app.include_router(routes_customer.router)
app.include_router(routes_auth.router)

@app.get("/")
def root():
    return {"message": "API is running"}
