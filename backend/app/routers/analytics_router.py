from datetime import datetime
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from collections import defaultdict

from app.database import get_db
from app.models import (
    CommunityRequest,
    RequestItem,
    AffectedZone,
    Inventory,
    Delivery,
    Allocation,
    DonationItem,
    RequestStatus,
    ReliefStatus,
    SeverityLevel,
)
from app.ai.demand_forecaster import generate_demand_forecast
from app.routers.simulation_router import SIMULATION_STATE

router = APIRouter(
    prefix="/analytics",
    tags=["Impact Analytics & Shortage Intelligence"]
)


def average_minutes(values):
    """Return average duration in minutes, or None if no valid values."""
    if not values:
        return None

    return round(
        sum(values) / len(values),
        1
    )


@router.get("")
def get_analytics(
    db: Session = Depends(get_db)
):
    requests = db.query(CommunityRequest).all()
    deliveries = db.query(Delivery).all()
    inventory = db.query(Inventory).all()
    allocations = db.query(Allocation).all()

    # -------------------------------------------------
    # REQUEST OVERVIEW
    # -------------------------------------------------

    total_requests = len(requests)

    supply_requests = sum(
        1 for r in requests
        if r.request_type == "SUPPLIES"
    )

    evacuation_requests = sum(
        1 for r in requests
        if r.request_type == "EVACUATION"
    )

    community_reports = sum(
        1 for r in requests
        if r.request_type == "COMMUNITY_REPORT"
    )

    fulfilled_requests = sum(
        1 for r in requests
        if r.status == RequestStatus.DELIVERED
    )

    critical_pending = sum(
        1
        for r in requests
        if r.priority_classification == SeverityLevel.CRITICAL
        and r.status in [
            RequestStatus.PENDING,
            RequestStatus.FLAGGED_DUPLICATE,
        ]
    )

    fulfillment_rate = round(
        (fulfilled_requests / total_requests) * 100,
        1
    ) if total_requests else 0

    # -------------------------------------------------
    # REQUEST STATUS BREAKDOWN
    # -------------------------------------------------

    status_breakdown = {
        status.value: sum(
            1 for r in requests
            if r.status == status
        )
        for status in RequestStatus
    }

    # -------------------------------------------------
    # PRIORITY BREAKDOWN
    # -------------------------------------------------

    priority_breakdown = {
        level.value: sum(
            1
            for r in requests
            if r.priority_classification == level
        )
        for level in SeverityLevel
    }

    # -------------------------------------------------
    # PEOPLE IMPACT
    # -------------------------------------------------

    people_affected = sum(
        r.affected_people or 0
        for r in requests
    )

    people_assisted = sum(
        r.affected_people or 0
        for r in requests
        if r.status == RequestStatus.DELIVERED
    )

    children_affected = sum(
        r.vulnerable_children or 0
        for r in requests
    )

    elderly_affected = sum(
        r.vulnerable_elderly or 0
        for r in requests
    )

    infants_affected = sum(
        r.vulnerable_infants or 0
        for r in requests
    )

    pregnant_affected = sum(
        r.vulnerable_pregnant or 0
        for r in requests
    )

    medical_emergency_requests = sum(
        1
        for r in requests
        if r.medical_emergency
    )

    immediate_danger_requests = sum(
        1
        for r in requests
        if r.immediate_danger == "YES"
    )

    # -------------------------------------------------
    # ACTIVE DELIVERIES
    # -------------------------------------------------

    active_deliveries = sum(
        1
        for d in deliveries
        if d.status in [
            ReliefStatus.ALLOCATED,
            ReliefStatus.DISPATCHED,
            ReliefStatus.IN_TRANSIT,
        ]
    )

    # -------------------------------------------------
    # REAL RESPONSE TIME
    #
    # Request created -> first allocation created
    # -------------------------------------------------

    allocation_by_request = {}

    for allocation in allocations:
        request_id = allocation.request_id

        if request_id not in allocation_by_request:
            allocation_by_request[request_id] = allocation
        elif allocation.created_at < allocation_by_request[request_id].created_at:
            allocation_by_request[request_id] = allocation

    response_times = []

    for request in requests:
        allocation = allocation_by_request.get(request.id)

        if (
            allocation
            and request.created_at
            and allocation.created_at
        ):
            minutes = (
                allocation.created_at -
                request.created_at
            ).total_seconds() / 60

            if minutes >= 0:
                response_times.append(minutes)

    average_response_time = average_minutes(
        response_times
    )

    # -------------------------------------------------
    # REAL DELIVERY TIME
    #
    # Delivery dispatched -> delivered
    # -------------------------------------------------

    delivery_times = []

    for delivery in deliveries:
        if (
            delivery.dispatched_at
            and delivery.delivered_at
        ):
            minutes = (
                delivery.delivered_at -
                delivery.dispatched_at
            ).total_seconds() / 60

            if minutes >= 0:
                delivery_times.append(minutes)

    average_delivery_time = average_minutes(
        delivery_times
    )

    # -------------------------------------------------
    # SUPPLY-DEMAND ANALYSIS
    # -------------------------------------------------

    category_demand = defaultdict(float)
    category_fulfilled = defaultdict(float)

    for request in requests:
        for item in request.items:
            category_demand[item.category] += (
                item.requested_quantity or 0
            )

            category_fulfilled[item.category] += (
                item.fulfilled_quantity or 0
            )

    category_stock = defaultdict(float)

    for inv in inventory:
        category_stock[inv.category] += (
            inv.available_quantity or 0
        )

    gap_data = []

    for category, demand in category_demand.items():
        fulfilled = category_fulfilled.get(
            category,
            0
        )

        available = category_stock.get(
            category,
            0
        )

        gap = max(
            0,
            demand - fulfilled
        )

        fulfillment_pct = (
            (fulfilled / demand) * 100
            if demand > 0
            else 0
        )

        gap_data.append({
            "category": category,
            "demand": round(demand, 1),
            "fulfilled": round(fulfilled, 1),
            "available": round(available, 1),
            "gap": round(gap, 1),
            "fulfillment_pct": round(
                fulfillment_pct,
                1
            ),
        })

    # -------------------------------------------------
    # REAL RESOURCE DISTRIBUTION
    #
    # Based on fulfilled RequestItems
    # -------------------------------------------------

    resource_totals = defaultdict(
        lambda: {
            "quantity": 0,
            "unit": ""
        }
    )

    for request in requests:
        for item in request.items:
            fulfilled = item.fulfilled_quantity or 0

            if fulfilled > 0:
                resource_totals[item.item_name]["quantity"] += (
                    fulfilled
                )

                resource_totals[item.item_name]["unit"] = (
                    item.unit
                )

    resources_distributed = [
        {
            "item": item_name,
            "quantity": round(data["quantity"], 1),
            "unit": data["unit"],
        }
        for item_name, data
        in resource_totals.items()
    ]

    # -------------------------------------------------
    # REQUEST TREND
    # -------------------------------------------------

    request_trend_map = defaultdict(int)

    for request in requests:
        if request.created_at:
            date_key = request.created_at.strftime(
                "%Y-%m-%d"
            )
            request_trend_map[date_key] += 1

    request_trend = [
        {
            "date": date,
            "requests": count,
        }
        for date, count
        in sorted(request_trend_map.items())
    ]

    # -------------------------------------------------
    # LOCATION BREAKDOWN
    # -------------------------------------------------

    location_map = defaultdict(
        lambda: {
            "requests": 0,
            "people": 0
        }
    )

    for request in requests:
        location = (
            request.location_name
            or "Unknown"
        )

        location_map[location]["requests"] += 1
        location_map[location]["people"] += (
            request.affected_people or 0
        )

    location_breakdown = [
        {
            "location": location,
            "requests": values["requests"],
            "people": values["people"],
        }
        for location, values
        in sorted(
            location_map.items(),
            key=lambda x: x[1]["requests"],
            reverse=True
        )
    ]

    # -------------------------------------------------
    # FINAL RESPONSE
    # -------------------------------------------------

    return {
        "total_requests": total_requests,

        "supply_requests": supply_requests,
        "evacuation_requests": evacuation_requests,
        "community_reports": community_reports,

        "fulfilled_requests": fulfilled_requests,
        "critical_requests_pending": critical_pending,
        "fulfillment_rate_pct": fulfillment_rate,

        "active_deliveries": active_deliveries,

        "people_affected": people_affected,
        "people_assisted": people_assisted,

        "children_affected": children_affected,
        "elderly_affected": elderly_affected,
        "infants_affected": infants_affected,
        "pregnant_affected": pregnant_affected,

        "medical_emergency_requests": medical_emergency_requests,
        "immediate_danger_requests": immediate_danger_requests,

        "average_response_time_mins": average_response_time,
        "average_delivery_time_mins": average_delivery_time,

        "status_breakdown": status_breakdown,
        "priority_breakdown": priority_breakdown,

        "supply_demand_gap": gap_data,
        "resources_distributed": resources_distributed,

        "request_trend": request_trend,
        "location_breakdown": location_breakdown,

        "simulation_escalated": SIMULATION_STATE.get(
            "is_escalated",
            False
        ),
    }


@router.get("/forecasts")
def get_forecasts(
    db: Session = Depends(get_db)
):
    zones = db.query(AffectedZone).all()
    requests = db.query(CommunityRequest).all()

    return generate_demand_forecast(
        zones=zones,
        requests=requests,
        disaster_escalated=SIMULATION_STATE.get(
            "is_escalated",
            False
        )
    )
@router.get("/shortages")
def get_shortage_intelligence(
    db: Session = Depends(get_db)
):
    shortages = []

    requests = db.query(CommunityRequest).all()
    inventory = db.query(Inventory).all()

    # Calculate requested quantity by category
    demand_by_category = defaultdict(float)

    for request in requests:
        for item in request.items:
            demand_by_category[item.category] += (
                item.requested_quantity or 0
            )

    # Calculate available inventory by category
    stock_by_category = defaultdict(float)

    for item in inventory:
        stock_by_category[item.category] += (
            item.available_quantity or 0
        )

    # Build shortage records from actual database data
    for category, required in demand_by_category.items():
        available = stock_by_category.get(category, 0)

        shortage = max(
            0,
            required - available
        )

        if shortage <= 0:
            continue

        matching_requests = [
            r
            for r in requests
            if any(
                item.category == category
                for item in r.items
            )
        ]

        affected_people = sum(
            r.affected_people or 0
            for r in matching_requests
        )

        urgency = "HIGH"

        if any(
            r.priority_classification == SeverityLevel.CRITICAL
            for r in matching_requests
        ):
            urgency = "CRITICAL"
        elif any(
            r.priority_classification == SeverityLevel.HIGH
            for r in matching_requests
        ):
            urgency = "HIGH"

        location = (
            matching_requests[0].location_name
            if matching_requests
            else "Multiple locations"
        )

        shortages.append({
            "id": len(shortages) + 1,
            "sector": location,
            "zone": location,
            "category": category,
            "required": round(required, 1),
            "available": round(available, 1),
            "shortage": round(shortage, 1),
            "unit": (
                matching_requests[0].items[0].unit
                if matching_requests
                and matching_requests[0].items
                else ""
            ),
            "urgency": urgency,
            "affected_people": affected_people,
            "potential_sources": [],
        })

    return shortages