import os

ROUTERS_DIR = os.path.join(os.path.dirname(__file__), "backend", "app", "routers")

inventory_code = """import datetime
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Dict, Any

from app.database import get_db
from app.models import Warehouse, Inventory, InventoryBatch, User
from app.schemas import InventoryResponse, WarehouseResponse, InventoryBatchResponse
from app.auth import get_current_user, log_audit_event

router = APIRouter(prefix="/inventory", tags=["Inventory Management"])

@router.get("", response_model=List[InventoryResponse])
def get_inventory(category: str = None, warehouse_id: int = None, db: Session = Depends(get_db)):
    query = db.query(Inventory)
    if category:
        query = query.filter(Inventory.category.ilike(f"%{category}%"))
    if warehouse_id:
        query = query.filter(Inventory.warehouse_id == warehouse_id)
        
    items = query.all()
    # Attach warehouse name
    for it in items:
        it.warehouse_name = it.warehouse.name if it.warehouse else "Main Depot"
        # Dynamic status check
        if it.available_quantity <= 0:
            it.status = "CRITICAL_SHORTAGE"
        elif it.available_quantity <= it.min_threshold:
            it.status = "LOW_STOCK"
        else:
            it.status = "AVAILABLE"
            
    return items

@router.get("/warehouses", response_model=List[WarehouseResponse])
def get_warehouses(db: Session = Depends(get_db)):
    warehouses = db.query(Warehouse).filter(Warehouse.is_active == True).all()
    for wh in warehouses:
        for it in wh.inventory:
            it.warehouse_name = wh.name
    return warehouses

@router.get("/alerts")
def get_inventory_alerts(db: Session = Depends(get_db)):
    # Low stock & critical shortages
    low_stock = db.query(Inventory).filter(Inventory.available_quantity <= Inventory.min_threshold).all()
    
    # Expiring batches (within 14 days)
    two_weeks_ahead = datetime.datetime.utcnow() + datetime.timedelta(days=14)
    expiring_batches = db.query(InventoryBatch).filter(
        InventoryBatch.expiry_date != None,
        InventoryBatch.expiry_date <= two_weeks_ahead
    ).all()
    
    alerts = []
    for it in low_stock:
        alerts.append({
            "type": "SHORTAGE" if it.available_quantity == 0 else "LOW_STOCK",
            "severity": "CRITICAL" if it.available_quantity == 0 else "HIGH",
            "warehouse": it.warehouse.name if it.warehouse else "Warehouse",
            "item": it.item_name,
            "category": it.category,
            "available": it.available_quantity,
            "threshold": it.min_threshold,
            "unit": it.unit,
            "message": f"{it.item_name} is critically low ({it.available_quantity:g} {it.unit} left) at {it.warehouse.name if it.warehouse else 'Depot'}."
        })
        
    for b in expiring_batches:
        inv = b.inventory
        alerts.append({
            "type": "EXPIRING",
            "severity": "HIGH",
            "warehouse": inv.warehouse.name if inv and inv.warehouse else "Depot",
            "item": inv.item_name if inv else "Batch Item",
            "batch_number": b.batch_number,
            "expiry_date": b.expiry_date.strftime("%Y-%m-%d") if b.expiry_date else "",
            "quantity": b.quantity,
            "unit": inv.unit if inv else "units",
            "message": f"Batch {b.batch_number} ({inv.item_name if inv else ''}) expires on {b.expiry_date.strftime('%Y-%m-%d')}."
        })
        
    return alerts
"""

with open(os.path.join(ROUTERS_DIR, "inventory_router.py"), "w", encoding="utf-8") as f:
    f.write(inventory_code)

print("inventory_router.py written")

# donations_router.py
donations_code = """import datetime
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional

from app.database import get_db
from app.models import Donation, DonationItem, Delivery, Allocation, CommunityRequest, ReliefStatus, User
from app.schemas import DonationCreate, DonationResponse, ReliefTraceResponse, TimelineStep
from app.auth import get_current_user, log_audit_event

router = APIRouter(prefix="/donations", tags=["Donations & Transparency"])

@router.get("", response_model=List[DonationResponse])
def list_donations(db: Session = Depends(get_db)):
    return db.query(Donation).order_by(Donation.created_at.desc()).all()

@router.post("", response_model=DonationResponse)
def create_donation(
    donation_in: DonationCreate,
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_current_user)
):
    count = db.query(Donation).count() + 10284
    tracking_id = f"D-{count}"
    relief_id = f"RELIEF-2026-0{count % 1000:03d}"

    donation = Donation(
        donor_id=current_user.id if current_user else None,
        donor_name=donation_in.donor_name,
        donor_email=donation_in.donor_email,
        tracking_id=tracking_id,
        relief_id=relief_id,
        target_zone_id=donation_in.target_zone_id,
        status=ReliefStatus.DONATED,
        notes=donation_in.notes
    )
    db.add(donation)
    db.flush()

    for it in donation_in.items:
        db_it = DonationItem(
            donation_id=donation.id,
            category=it.category,
            item_name=it.item_name,
            quantity=it.quantity,
            unit=it.unit
        )
        db.add(db_it)

    db.commit()
    db.refresh(donation)

    log_audit_event(
        db=db,
        actor_id=current_user.id if current_user else None,
        actor_name=donation.donor_name,
        actor_role="DONOR",
        action="CREATE_DONATION",
        entity_type="DONATION",
        entity_id=donation.tracking_id,
        previous_state=None,
        new_state=f"Relief ID: {relief_id}",
        reason="Citizen relief contribution pledged"
    )

    return donation

@router.get("/{identifier}/trace", response_model=ReliefTraceResponse)
def trace_relief_package(identifier: str, db: Session = Depends(get_db)):
    # Match by relief_id or donation tracking_id or request tracking_code
    clean_id = identifier.strip().upper()
    
    # Try finding donation
    donation = db.query(Donation).filter(
        (Donation.relief_id == clean_id) | (Donation.tracking_id == clean_id)
    ).first()

    # Try finding delivery by relief_id
    delivery = db.query(Delivery).filter(Delivery.relief_id == clean_id).first()
    
    # If found via donation but no delivery yet, search delivery by relief_id
    if donation and not delivery:
        delivery = db.query(Delivery).filter(Delivery.relief_id == donation.relief_id).first()

    # If delivery found, locate allocation and request
    allocation = None
    request = None
    if delivery:
        allocation = delivery.allocation
        if allocation:
            request = allocation.request
            
    # If no delivery but allocation with relief_id exists
    if not delivery and not allocation:
        allocation = db.query(Allocation).filter(Allocation.relief_id == clean_id).first()
        if allocation:
            request = allocation.request
            delivery = allocation.delivery

    # If still not found, search by request tracking code
    if not request:
        request = db.query(CommunityRequest).filter(CommunityRequest.tracking_code == clean_id).first()
        if request and request.allocations:
            allocation = request.allocations[0]
            clean_id = allocation.relief_id
            delivery = allocation.delivery

    if not donation and not delivery and not allocation and not request:
        raise HTTPException(
            status_code=404,
            detail=f"No relief journey record found for identifier '{clean_id}'"
        )

    # Resolve items summary
    items_summary = []
    if allocation and allocation.items:
        for it in allocation.items:
            items_summary.append({
                "category": it.category,
                "item_name": it.item_name,
                "quantity": it.allocated_quantity,
                "unit": it.unit
            })
    elif donation and donation.items:
        for it in donation.items:
            items_summary.append({
                "category": it.category,
                "item_name": it.item_name,
                "quantity": it.quantity,
                "unit": it.unit
            })
    elif request and request.items:
        for it in request.items:
            items_summary.append({
                "category": it.category,
                "item_name": it.item_name,
                "quantity": it.requested_quantity,
                "unit": it.unit
            })

    # Current status resolution
    current_status = ReliefStatus.DONATED
    if delivery:
        current_status = delivery.status
    elif allocation:
        current_status = ReliefStatus.ALLOCATED
    elif donation:
        current_status = donation.status

    # Build the signature 8-step visual timeline
    # DONATED -> RECEIVED -> VERIFIED -> STORED -> ALLOCATED -> DISPATCHED -> IN TRANSIT -> DELIVERED
    status_order = [
        ReliefStatus.DONATED,
        ReliefStatus.RECEIVED,
        ReliefStatus.VERIFIED,
        ReliefStatus.STORED,
        ReliefStatus.ALLOCATED,
        ReliefStatus.DISPATCHED,
        ReliefStatus.IN_TRANSIT,
        ReliefStatus.DELIVERED
    ]
    
    current_idx = status_order.index(current_status) if current_status in status_order else 0

    base_time = donation.created_at if donation else (request.created_at if request else datetime.datetime.utcnow())
    
    timeline_steps = [
        TimelineStep(
            step="DONATED",
            label="Pledged by Donor",
            status="COMPLETED" if current_idx >= 0 else "PENDING",
            created_at=(base_time).strftime("%b %d, %H:%M"),
            actor=donation.donor_name if donation else "Relief Contributor",
            details="Relief pledge registered in central transparent ledger."
        ),
        TimelineStep(
            step="RECEIVED",
            label="Received at Warehouse",
            status="COMPLETED" if current_idx >= 1 else ("CURRENT" if current_idx == 0 else "PENDING"),
            created_at=(base_time + datetime.timedelta(hours=1.2)).strftime("%b %d, %H:%M") if current_idx >= 1 else None,
            actor="Warehouse Inflow Inspector",
            details="Cargo verified, scanned, and physical condition authenticated."
        ),
        TimelineStep(
            step="VERIFIED",
            label="Quality & Batch Verified",
            status="COMPLETED" if current_idx >= 2 else ("CURRENT" if current_idx == 1 else "PENDING"),
            created_at=(base_time + datetime.timedelta(hours=1.8)).strftime("%b %d, %H:%M") if current_idx >= 2 else None,
            actor="Relief Quality Officer",
            details="Lot numbers and expiration dates certified safe for consumption."
        ),
        TimelineStep(
            step="STORED",
            label="Stored in Climate Buffer",
            status="COMPLETED" if current_idx >= 3 else ("CURRENT" if current_idx == 2 else "PENDING"),
            created_at=(base_time + datetime.timedelta(hours=2.4)).strftime("%b %d, %H:%M") if current_idx >= 3 else None,
            actor="Inventory Controller",
            details=f"Palletized in {allocation.warehouse.name if allocation and allocation.warehouse else 'Central Hub'}."
        ),
        TimelineStep(
            step="ALLOCATED",
            label="AI Matched & Authority Approved",
            status="COMPLETED" if current_idx >= 4 else ("CURRENT" if current_idx == 3 else "PENDING"),
            created_at=(base_time + datetime.timedelta(hours=3.5)).strftime("%b %d, %H:%M") if current_idx >= 4 else None,
            actor="Emergency Operations Authority",
            details=f"Matched to {request.location_name if request else 'Flood Zone B'} based on priority score."
        ),
        TimelineStep(
            step="DISPATCHED",
            label="Loaded & Manifest Issued",
            status="COMPLETED" if current_idx >= 5 else ("CURRENT" if current_idx == 4 else "PENDING"),
            created_at=(base_time + datetime.timedelta(hours=4.2)).strftime("%b %d, %H:%M") if current_idx >= 5 else None,
            actor="Logistics Dispatcher",
            details=f"Loaded onto {delivery.vehicle.vehicle_type if delivery and delivery.vehicle else 'All-Terrain Relief Truck'}."
        ),
        TimelineStep(
            step="IN_TRANSIT",
            label="Navigating Inundated Corridor",
            status="COMPLETED" if current_idx >= 6 else ("CURRENT" if current_idx == 5 else "PENDING"),
            created_at=(base_time + datetime.timedelta(hours=4.9)).strftime("%b %d, %H:%M") if current_idx >= 6 else None,
            actor=delivery.driver_name if delivery and delivery.driver_name else "Field Convoy Driver",
            details="Live GPS tracking active; route avoiding flooded Causeway Bridge."
        ),
        TimelineStep(
            step="DELIVERED",
            label="Verified Community Handover",
            status="COMPLETED" if current_idx >= 7 else ("CURRENT" if current_idx == 6 else "PENDING"),
            created_at=delivery.delivered_at.strftime("%b %d, %H:%M") if (delivery and delivery.delivered_at) else (
                (base_time + datetime.timedelta(hours=5.8)).strftime("%b %d, %H:%M") if current_idx >= 7 else None
            ),
            actor="Community Representative / Field Volunteer",
            details=f"Relief received at {request.location_name if request else 'Flood Zone B'} with digital signature."
        )
    ]

    proof = None
    if current_idx >= 7 and delivery:
        proof = {
            "delivered_at": delivery.delivered_at.isoformat() if delivery.delivered_at else datetime.datetime.utcnow().isoformat(),
            "recipient_signature": delivery.recipient_signature or "Verified - Village Council Chair",
            "proof_photo_url": delivery.proof_photo_url or "https://images.unsplash.com/photo-1547841243-eacb14453cd9?auto=format&fit=crop&w=600&q=80",
            "notes": delivery.notes or "Delivered directly to community shelter without incident."
        }

    return ReliefTraceResponse(
        relief_id=clean_id,
        donation_id=donation.tracking_id if donation else None,
        donor_name=donation.donor_name if donation else "Community Donor Network",
        request_tracking_code=request.tracking_code if request else "FR-1048",
        destination_location=request.location_name if request else "Village A, Sector 4",
        destination_zone=request.zone.name if request and request.zone else "Flood Zone B (Delta Basin)",
        current_status=current_status,
        people_supported=request.affected_people if request else 350,
        items_summary=items_summary,
        origin_warehouse=allocation.warehouse.name if allocation and allocation.warehouse else "Warehouse A (Central Depot)",
        assigned_vehicle=delivery.vehicle.code if delivery and delivery.vehicle else "RESQ-V01 (Heavy 4x4)",
        driver_contact=delivery.driver_phone if delivery and delivery.driver_phone else "+91 98451 22390",
        timeline=timeline_steps,
        proof_of_delivery=proof
    )
"""

with open(os.path.join(ROUTERS_DIR, "donations_router.py"), "w", encoding="utf-8") as f:
    f.write(donations_code)

print("donations_router.py written")
