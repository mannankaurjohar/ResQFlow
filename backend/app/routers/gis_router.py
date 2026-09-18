import json
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import Dict, Any

from app.database import get_db
from app.models import (
    AffectedZone, CommunityRequest, Warehouse, ReliefCenter,
    Delivery, Route, ReliefStatus, SeverityLevel
)

router = APIRouter(prefix="/gis", tags=["GIS & Spatial Mapping"])

@router.get("/overview")
def get_map_overview(db: Session = Depends(get_db)):
    zones = db.query(AffectedZone).all()
    requests = db.query(CommunityRequest).all()
    warehouses = db.query(Warehouse).filter(Warehouse.is_active == True).all()
    relief_centers = db.query(ReliefCenter).all()
    deliveries = db.query(Delivery).all()

    # Format zones
    zones_data = []
    for z in zones:
        polygon = []
        if z.polygon_geojson:
            try:
                polygon = json.loads(z.polygon_geojson)
            except Exception:
                polygon = []
                
        # Count critical requests in this zone
        crit_count = sum(1 for r in z.requests if r.priority_classification in [SeverityLevel.CRITICAL, SeverityLevel.SEVERE])
        
        zones_data.append({
            "id": z.id,
            "name": z.name,
            "code": z.code,
            "severity_level": z.severity_level.value if hasattr(z.severity_level, 'value') else str(z.severity_level),
            "water_level_meters": z.water_level_meters,
            "population": z.population,
            "households": z.households,
            "center": [z.center_lat, z.center_lon],
            "polygon": polygon,
            "is_isolated": z.is_isolated,
            "critical_requests_count": crit_count
        })

    # Format requests
    requests_data = []
    for r in requests:
        items_summary = [f"{it.requested_quantity:g} {it.unit} {it.item_name}" for it in r.items]
        active_score = r.authority_override_score if r.authority_override_score is not None else r.priority_score
        requests_data.append({
            "id": r.id,
            "tracking_code": r.tracking_code,
            "location_name": r.location_name,
            "lat": r.latitude,
            "lon": r.longitude,
            "affected_people": r.affected_people,
            "vulnerable_count": (r.vulnerable_elderly or 0) + (r.vulnerable_children or 0) + (r.vulnerable_infants or 0),
            "urgency": r.urgency.value if hasattr(r.urgency, 'value') else str(r.urgency),
            "priority_score": active_score,
            "priority_classification": r.priority_classification.value if hasattr(r.priority_classification, 'value') else str(r.priority_classification),
            "status": r.status.value if hasattr(r.status, 'value') else str(r.status),
            "items": items_summary
        })

    # Format warehouses
    warehouses_data = []
    for wh in warehouses:
        inv_summary = []
        for it in wh.inventory:
            inv_summary.append({
                "item_name": it.item_name,
                "category": it.category,
                "available": it.available_quantity,
                "unit": it.unit,
                "status": it.status
            })
        warehouses_data.append({
            "id": wh.id,
            "name": wh.name,
            "code": wh.code,
            "lat": wh.latitude,
            "lon": wh.longitude,
            "capacity_sqm": wh.capacity_sqm,
            "inventory": inv_summary
        })

    # Format relief centers
    relief_centers_data = []
    for rc in relief_centers:
        relief_centers_data.append({
            "id": rc.id,
            "name": rc.name,
            "lat": rc.latitude,
            "lon": rc.longitude,
            "capacity": rc.capacity,
            "occupancy": rc.current_occupancy,
            "has_medical": rc.has_medical_post
        })

    # Format active delivery routes
    deliveries_data = []
    for d in deliveries:
        waypoints = []
        if d.route and d.route.waypoints_json:
            try:
                waypoints = json.loads(d.route.waypoints_json)
            except Exception:
                waypoints = []
                
        deliveries_data.append({
            "id": d.id,
            "relief_id": d.relief_id,
            "status": d.status.value if hasattr(d.status, 'value') else str(d.status),
            "destination": d.destination_location_name,
            "dest_lat": d.destination_lat,
            "dest_lon": d.destination_lon,
            "vehicle": d.vehicle.code if d.vehicle else "RESQ-TRK",
            "driver": d.driver_name,
            "waypoints": waypoints
        })

    # Blocked roads & inundated bridges for GIS overlay
    blocked_roads = [
        {"name": "Causeway North Bridge", "lat": 14.5310, "lon": 75.3230, "reason": "Submerged under 1.4m floodwater", "status": "IMPASSABLE"},
        {"name": "East Embankment Road", "lat": 14.5050, "lon": 75.3120, "reason": "Breach in retaining wall", "status": "HEAVY_VEHICLES_ONLY"}
    ]

    return {
        "zones": zones_data,
        "requests": requests_data,
        "warehouses": warehouses_data,
        "relief_centers": relief_centers_data,
        "deliveries": deliveries_data,
        "blocked_roads": blocked_roads
    }
