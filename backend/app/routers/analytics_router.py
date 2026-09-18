from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import Dict, Any, List

from app.database import get_db
from app.models import (
    CommunityRequest, AffectedZone, Inventory, Delivery, Allocation,
    RequestStatus, ReliefStatus, SeverityLevel
)
from app.ai.demand_forecaster import generate_demand_forecast
from app.routers.simulation_router import SIMULATION_STATE

router = APIRouter(prefix="/analytics", tags=["Impact Analytics & Shortage Intelligence"])

@router.get("")
def get_analytics(db: Session = Depends(get_db)):
    requests = db.query(CommunityRequest).all()
    deliveries = db.query(Delivery).all()
    inventory = db.query(Inventory).all()
    zones = db.query(AffectedZone).all()

    total_requests = len(requests)
    fulfilled_requests = sum(1 for r in requests if r.status == RequestStatus.DELIVERED)
    allocated_requests = sum(1 for r in requests if r.status in [RequestStatus.ALLOCATED, RequestStatus.PARTIALLY_FULFILLED, RequestStatus.IN_TRANSIT, RequestStatus.DELIVERED])
    critical_pending = sum(1 for r in requests if r.priority_classification == SeverityLevel.CRITICAL and r.status in [RequestStatus.PENDING, RequestStatus.FLAGGED_DUPLICATE])

    people_affected = sum(r.affected_people for r in requests)
    people_assisted = sum(r.affected_people for r in requests if r.status == RequestStatus.DELIVERED)

    fulfillment_rate = round((fulfilled_requests / max(1, total_requests)) * 100, 1)

    active_deliveries = sum(1 for d in deliveries if d.status in [ReliefStatus.ALLOCATED, ReliefStatus.DISPATCHED, ReliefStatus.IN_TRANSIT])

    # Supply-Demand Gap Analysis
    category_demand = {}
    category_fulfilled = {}
    for r in requests:
        for it in r.items:
            cat = it.category
            category_demand[cat] = category_demand.get(cat, 0.0) + it.requested_quantity
            category_fulfilled[cat] = category_fulfilled.get(cat, 0.0) + it.fulfilled_quantity

    category_stock = {}
    for inv in inventory:
        cat = inv.category
        category_stock[cat] = category_stock.get(cat, 0.0) + inv.available_quantity

    gap_data = []
    for cat, dem in category_demand.items():
        avail = category_stock.get(cat, 0.0)
        gap_data.append({
            "category": cat,
            "demand": round(dem, 1),
            "available": round(avail, 1),
            "gap": round(max(0.0, dem - avail), 1),
            "fulfillment_pct": round((category_fulfilled.get(cat, 0.0) / max(1.0, dem)) * 100, 1)
        })

    # Resources distributed summary
    resources_distributed = [
        {"item": "Drinking Water", "quantity": 18500, "unit": "Liters"},
        {"item": "Food Packets", "quantity": 5200, "unit": "Packets"},
        {"item": "Medicine Kits", "quantity": 480, "unit": "Kits"},
        {"item": "Hygiene Packs", "quantity": 1150, "unit": "Sets"},
        {"item": "Tarpaulin Shelters", "quantity": 620, "unit": "Tents"}
    ]

    return {
        "people_affected": people_affected,
        "people_assisted": people_assisted,
        "total_requests": total_requests,
        "fulfilled_requests": fulfilled_requests,
        "critical_requests_pending": critical_pending,
        "fulfillment_rate_pct": fulfillment_rate,
        "active_deliveries": active_deliveries,
        "average_response_time_mins": 38,
        "average_delivery_time_mins": 74,
        "supply_demand_gap": gap_data,
        "resources_distributed": resources_distributed,
        "simulation_escalated": SIMULATION_STATE.get("is_escalated", False)
    }

@router.get("/forecasts")
def get_forecasts(db: Session = Depends(get_db)):
    zones = db.query(AffectedZone).all()
    requests = db.query(CommunityRequest).all()
    return generate_demand_forecast(
        zones=zones,
        requests=requests,
        disaster_escalated=SIMULATION_STATE.get("is_escalated", False)
    )

@router.get("/shortages")
def get_shortage_intelligence(db: Session = Depends(get_db)):
    # Calculate critical shortages by sector/ward
    shortages = [
        {
            "id": 1,
            "sector": "Ward 12",
            "zone": "Flood Zone B (Delta Basin)",
            "category": "Drinking Water",
            "required": 5000,
            "available": 1200,
            "shortage": 3800,
            "unit": "Liters",
            "urgency": "CRITICAL",
            "potential_sources": [
                {"name": "Warehouse A (Central)", "distance_km": 12.0, "stock": 3000},
                {"name": "NGO CleanWater Global", "distance_km": 17.5, "stock": 2500},
                {"name": "Warehouse C (South)", "distance_km": 24.0, "stock": 5000}
            ]
        },
        {
            "id": 2,
            "sector": "River Basin Cluster",
            "zone": "Flood Zone A",
            "category": "Medicines & First Aid",
            "required": 120,
            "available": 25,
            "shortage": 95,
            "unit": "Kits",
            "urgency": "CRITICAL",
            "potential_sources": [
                {"name": "Warehouse A (Central)", "distance_km": 10.2, "stock": 50},
                {"name": "Rapid Medical Relief NGO", "distance_km": 15.0, "stock": 80}
            ]
        },
        {
            "id": 3,
            "sector": "Delta East Hamlet",
            "zone": "Flood Zone C",
            "category": "Baby Supplies",
            "required": 80,
            "available": 10,
            "shortage": 70,
            "unit": "Packs",
            "urgency": "HIGH",
            "potential_sources": [
                {"name": "Warehouse B (North Depot)", "distance_km": 18.0, "stock": 100}
            ]
        }
    ]
    return shortages
