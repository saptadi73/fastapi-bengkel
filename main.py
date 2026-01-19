from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from contextlib import asynccontextmanager
import os

# Auto-import all routers from routes directory
try:
    from routes import all_routers
    print(f"✓ Successfully imported {len(all_routers)} routers")
except Exception as e:
    print(f"✗ Error importing routers: {e}")
    import traceback
    traceback.print_exc()
    all_routers = []


# Startup dan shutdown events
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    print("🚀 FastAPI Aplikasi sedang startup...")
    # Uncomment untuk auto-start scheduler saat app startup
    # from services.scheduler_maintenance_reminder import start_scheduler
    # start_scheduler(hour=7, minute=0)
    print("✓ Aplikasi siap digunakan")
    
    yield
    
    # Shutdown
    print("🛑 FastAPI Aplikasi sedang shutdown...")
    from services.scheduler_maintenance_reminder import stop_scheduler
    stop_scheduler()
    print("✓ Scheduler dihentikan")


app = FastAPI(lifespan=lifespan)

# CORS middleware - HARUS DITAMBAHKAN PALING PERTAMA!
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",      # Frontend dev
        "http://127.0.0.1:3000",
        "https://carspeed.gagakrimang.web.id",     # Production
    ],
    # Izinkan semua port localhost saat development (Vite, CRA, dll)
    allow_origin_regex=r"http://(localhost|127\.0\.0\.1)(:\d+)?",
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)

# Ensure uploads directory exists
os.makedirs("uploads", exist_ok=True)

# Mount static files
app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")

# Auto-include all routers
# No need to manually add each router anymore!
# Just add new routes_*.py files in the routes directory
print(f"📋 Including {len(all_routers)} routers...")
for i, router in enumerate(all_routers, 1):
    try:
        app.include_router(router)
        print(f"  ✓ [{i}/{len(all_routers)}] Included: {router.prefix or 'root'}")
    except Exception as e:
        print(f"  ✗ [{i}/{len(all_routers)}] Error including router: {e}")

print(f"✓ All {len(all_routers)} routers included successfully")

@app.get("/")
def root():
    return {"message": "API is running"}
