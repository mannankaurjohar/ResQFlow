import datetime
import json
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app.database import get_db
from app.models import (
    CommunityRequest, Warehouse, Inventory, Allocation, AllocationItem,
    Delivery, Vehicle, Route, RequestStatus, ReliefStatus, User, UserRole
)
from app.schemas import (
    AIResourceMatchRecommendation, ApproveAllocationRequest, AllocationResponse
)
from app.auth import get_current_user, log_audit_event
from app.ai.resource_matcher import match_resources_for_request

router = APIRouter(prefix="/allocations", tags=["Resource Allocations"])

@router.get("", response_model=List[AllocationResponse])
def list_allocations(db: Session = Depends(get_db)):
    return db.query(Allocation).order_by(Allocation.created_at.desc()).all()

@router.get("/recommend/{request_id}", response_model=AIResourceMatchRecommendation)
def get_match_recommendation(request_id: int, db: Session = Depends(get_db)):
    req = db.query(CommunityRequest).filter(CommunityRequest.id == request_id).first()
    if not req:
        raise HTTPException(status_code=404, detail="Request not found")
        
    warehouses = db.query(Warehouse).filter(Warehouse.is_active == True).all()
    recommendation = match_resources_for_request(req, warehouses)
    return recommendation

@router.post("/approve", response_model=AllocationResponse)
def approve_allocation(
    payload: ApproveAllocationRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    req = db.query(CommunityRequest).filter(CommunityRequest.id == payload.request_id).first()
    if not req:
        raise HTTPException(status_code=404, detail="Request not found")
        
    warehouse = db.query(Warehouse).filter(Warehouse.id == payload.warehouse_id).first()
    if not warehouse:
        raise HTTPException(status_code=404, detail="Warehouse not found")

    # Generate relief ID if not provided
    relief_id = payload.relief_id or f"RELIEF-2026-{req.id:05d}"
    
    # Check if allocation with relief_id already exists
    existing_alloc = db.query(Allocation).filter(Allocation.relief_id == relief_id).first()
    if existing_alloc:
        return existing_alloc

    # 1. Create Allocation
    allocation = Allocation(
        request_id=req.id,
        warehouse_id=warehouse.id,
        relief_id=relief_id,
        status="APPROVED",
        ai_score=req.priority_score,
        ai_rationale=f"Authority {current_user.full_name if current_user else 'Command'} approved allocation from {warehouse.name}.",
        is_partial=False,
        approved_by_id=current_user.id if current_user else None,
        approved_at=datetime.datetime.utcnow(),
        override_notes=payload.override_notes
    )
    db.add(allocation)
    db.flush()

    total_requested_units = 0.0
    total_allocated_units = 0.0

    # 2. Process Items & Update Inventory Integrity
    for it_data in payload.items:
        category = it_data.get("category", "")
        item_name = it_data.get("item_name", "")
        alloc_qty = float(it_data.get("allocated_quantity", 0.0))
        unit = it_data.get("unit", "units")
        
        if alloc_qty <= 0:
            continue

        # Find matching inventory in this warehouse
        inv = db.query(Inventory).filter(
            Inventory.warehouse_id == warehouse.id,
            Inventory.category.ilike(f"%{category}%")
        ).first()

        if not inv:
            inv = db.query(Inventory).filter(Inventory.warehouse_id == warehouse.id).first()

        if inv:
            if inv.available_quantity < alloc_qty:
                # Restrict to available - Never allow negative inventory!
                alloc_qty = inv.available_quantity
                allocation.is_partial = True

            inv.available_quantity -= alloc_qty
            inv.allocated_quantity += alloc_qty
            
        alloc_item = AllocationItem(
            allocation_id=allocation.id,
            category=category,
            item_name=item_name or (inv.item_name if inv else "Relief Supply"),
            requested_quantity=alloc_qty,
            allocated_quantity=alloc_qty,
            unit=unit
        )
        db.add(alloc_item)
        
        # Update RequestItem fulfilled quantity
        for r_item in req.items:
            if category.lower() in r_item.category.lower():
                r_item.fulfilled_quantity += alloc_qty
                total_requested_units += r_item.requested_quantity
                total_allocated_units += r_item.fulfilled_quantity

    # 3. Update Request Status
    if allocation.is_partial or (total_requested_units > 0 and total_allocated_units < total_requested_units):
        req.status = RequestStatus.PARTIALLY_FULFILLED
        allocation.is_partial = True
    else:
        req.status = RequestStatus.ALLOCATED

    # 4. Create Linked Delivery
    vehicle = db.query(Vehicle).filter(Vehicle.status == "AVAILABLE").first()
    if vehicle:
        vehicle.status = "IN_TRANSIT"

    delivery = Delivery(
        relief_id=relief_id,
        allocation_id=allocation.id,
        vehicle_id=vehicle.id if vehicle else None,
        driver_name=vehicle.driver_name if vehicle else "Devan Sharma",
        driver_phone=vehicle.driver_phone if vehicle else "+91 98451 22390",
        origin_warehouse_id=warehouse.id,
        destination_location_name=req.location_name,
        destination_lat=req.latitude,
        destination_lon=req.longitude,
        status=ReliefStatus.ALLOCATED,
        dispatched_at=datetime.datetime.utcnow(),
        estimated_delivery_at=datetime.datetime.utcnow() + datetime.timedelta(hours=2),
        notes="Relief payload locked and manifest generated."
    )
    db.add(delivery)
    db.flush()

    # Create Delivery Route
    route = Route(
        delivery_id=delivery.id,
        waypoints_json=json.dumps([
            {"lat": warehouse.latitude, "lon": warehouse.longitude, "name": warehouse.name},
            {"lat": (warehouse.latitude + req.latitude) / 2, "lon": (warehouse.longitude + req.longitude) / 2, "name": "Bypass Checkpoint 4"},
            {"lat": req.latitude, "lon": req.longitude, "name": req.location_name}
        ]),
        total_distance_km=round(abs(req.latitude - warehouse.latitude) * 111.0 + abs(req.longitude - warehouse.longitude) * 90.0, 1),
        estimated_time_mins=45,
        avoids_flooded_bridges=True
    )
    db.add(route)

    db.commit()
    db.refresh(allocation)

    # 5. Chained Audit Log
    log_audit_event(
        db=db,
        actor_id=current_user.id if current_user else None,
        actor_name=current_user.full_name if current_user else "Authority Commander",
        actor_role="AUTHORITY",
        action="APPROVE_ALLOCATION",
        entity_type="ALLOCATION",
        entity_id=relief_id,
        previous_state="PENDING_ALLOCATION",
        new_state=json.dumps({"status": "APPROVED", "warehouse": warehouse.name, "partial": allocation.is_partial}),
        reason=f"Approved relief dispatch for {req.location_name} ({req.tracking_code})"
    )

    return allocation
