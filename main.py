from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import os

# Auto-import all routers from routes directory
from routes import all_routers

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

# Auto-include all routers
# No need to manually add each router anymore!
# Just add new routes_*.py files in the routes directory
for router in all_routers:
    app.include_router(router)

@app.get("/")
def root():
    return {"message": "API is running"}
