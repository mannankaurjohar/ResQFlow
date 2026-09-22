from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from app.routers.official_warehouses_router import (
    router as official_warehouses_router
)
from app.config import settings
from app.database import engine, Base, SessionLocal
from app.seed_data import seed_all_data
from app.routers.public_data_router import router as public_data_router
from fastapi.staticfiles import StaticFiles
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
    description="""
    Intelligent Flood-Relief Coordination Platform connecting:
    Affected Communities -> Volunteers -> NGOs -> Warehouses -> Donors -> Authorities.
    
    Principles:
    RIGHT RESOURCE -> RIGHT PLACE -> RIGHT TIME -> RIGHT PRIORITY -> FULL TRACEABILITY
    """,
    version="1.0.0",
    lifespan=lifespan
)
app.mount(
    "/uploads",
    StaticFiles(directory="uploads"),
    name="uploads"
)
# CORS Configuration
# CORS Configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "https://resqflow-ai.vercel.app",
    ],
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
app.include_router(
    public_data_router,
    prefix="/api",
)
app.include_router(
    official_warehouses_router,
    prefix="/api"
)
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
import os

FRONTEND_DIST = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "frontend", "dist"))
if os.path.exists(FRONTEND_DIST):
    assets_dir = os.path.join(FRONTEND_DIST, "assets")
    if os.path.exists(assets_dir):
        app.mount("/assets", StaticFiles(directory=assets_dir), name="assets")

from fastapi import Request

@app.get("/")
def root(request: Request):
    accept_header = request.headers.get("accept", "")
    if "text/html" in accept_header and os.path.exists(FRONTEND_DIST):
        index_file = os.path.join(FRONTEND_DIST, "index.html")
        if os.path.exists(index_file):
            return FileResponse(index_file)
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
