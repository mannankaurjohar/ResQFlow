import os

APP_DIR = os.path.join(os.path.dirname(__file__), "backend", "app")

main_code = """from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from app.config import settings
from app.database import engine, Base, SessionLocal
from app.seed_data import seed_all_data

# Import routers
from app.routers import (
    auth_router, requests_router, inventory_router, donations_router,
    allocations_router, deliveries_router, gis_router, simulation_router,
    analytics_router, audit_router
)

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: Create tables & seed data
    print("ResQFlow AI Backend initializing...")
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        seed_all_data(db)
    finally:
        db.close()
    print("ResQFlow AI Backend is ready for emergency response.")
    yield
    # Shutdown
    print("ResQFlow AI Backend stopping.")

app = FastAPI(
    title="ResQFlow AI - Flood Relief & Resource Coordination API",
    description=\"\"\"
    Intelligent Flood-Relief Coordination Platform connecting:
    Affected Communities -> Volunteers -> NGOs -> Warehouses -> Donors -> Authorities.
    
    Principles:
    RIGHT RESOURCE -> RIGHT PLACE -> RIGHT TIME -> RIGHT PRIORITY -> FULL TRACEABILITY
    \"\"\",
    version="1.0.0",
    lifespan=lifespan
)

# CORS Configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register API Routers
app.include_router(auth_router.router, prefix=settings.API_V1_STR)
app.include_router(requests_router.router, prefix=settings.API_V1_STR)
app.include_router(inventory_router.router, prefix=settings.API_V1_STR)
app.include_router(donations_router.router, prefix=settings.API_V1_STR)
app.include_router(allocations_router.router, prefix=settings.API_V1_STR)
app.include_router(deliveries_router.router, prefix=settings.API_V1_STR)
app.include_router(gis_router.router, prefix=settings.API_V1_STR)
app.include_router(simulation_router.router, prefix=settings.API_V1_STR)
app.include_router(analytics_router.router, prefix=settings.API_V1_STR)
app.include_router(audit_router.router, prefix=settings.API_V1_STR)

@app.get("/")
def root():
    return {
        "platform": "ResQFlow AI",
        "tagline": "From community needs to verified relief delivery.",
        "core_message": "Know what is needed. Know where it is needed. Know where the resources went.",
        "status": "OPERATIONAL",
        "mode": "FLOOD_RELIEF_MODE",
        "version": "1.0.0",
        "docs_url": "/docs",
        "api_v1": "/api"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
"""

with open(os.path.join(APP_DIR, "main.py"), "w", encoding="utf-8") as f:
    f.write(main_code)

print("main.py written successfully.")
